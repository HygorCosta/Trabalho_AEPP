import math
import numpy as np
import pandas as pd

class Perfuracao:
    """
    Classe usada para avaliar economicamente um projeto de perfuração de poços de petróleo.

    ...

    Attributos
    ----------
    tb : float
        tempo de broca em atividade (h)
    tc : float
        tempo de broca parada (h)
    tt : float
        tempo de manobra (h)
    comp_perfurado: float
        comprimento perfurado (m)

    Methods
    -------
    custo_de_perfuracao:
        Retorna o custo US$ por metro de perfuração.
    tempo_de_broca:
        Estima o tempo de broca em atividade em horas (tb).
    tempo_de_manobra:
        Estima o tempo de manobra em horas (tt).
    tempo_de_broca_parada:
        Define o tempo de broca parada em horas (tc).
    """

    def __init__(self, dados_perfuracao) -> None:
        self.dados = pd.read_excel(dados_perfuracao, index_col=0)

    def custo_de_perfuracao(self):
        """Calcular o custo do posto pioneiro - P1."""
        cb = 1e3 * (2*58 + 2*45 + 6*23 + 6*16)
        cr = 5e5
        return (cb + cr * self.tempo_de_perfuracao()) / self.dados['Comprimento']
    
    def tempo_de_broca(self, index, alpha=0.000889, k=3.6):
        return (1 / alpha * k) * (math.e**(alpha * self.dados['Comprimento'][index]) - 1)
    
    def tempo_de_manobra(self, index):
        return 0.003 * self.dados['Comprimento'][index]
    
    def tempo_de_broca_parada(self):
        num_brocas_usadas = 2 + 2 + 6 + 6
        num_manobras = num_brocas_usadas - 1
        return 2 * num_manobras
    
    def tempo_de_perfuracao(self, index=0):
        return self.tempo_de_broca(index) + self.tempo_de_broca_parada() + self.tempo_de_manobra(index)

    def custo_completacao(self):
        return 0.75 * self.cr * self.tempo_de_perfuracao()
    
    def c2(self):
        if self.modelo == 'Up':
            c2 = 0.375
        elif self.modelo == 'Base':
            c2 = 0.250
        elif self.modelo == 'Down':
            c2 = 0.125
        else:
            raise TypeError("Palavra chave do modelo incorreta.")
        return c2
    
    def cap(self):
        """Curva de aprendizagem de perfuração - atualizar o tempo de perfuração"""
        tempo_pioneiro = self.tempo_de_perfuracao()
        c1 = 2/3 * tempo_pioneiro
        c2 = self.c2()
        c3 = 1/3 * tempo_pioneiro
        return c1 * math.e**((1 - self.num_poco) * c2) + c3
    
    def custo_poco(self):
        return (1/0.7) * (self.custo_completacao() + self.custo_de_perfuracao() * self.comp_perfurado)