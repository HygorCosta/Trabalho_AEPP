import math
import numpy as np
import pandas as pd

class Perfuracao:

    def __init__(self, dados_perfuracao, LDA) -> None:
        self.dados = pd.read_excel(dados_perfuracao, sheet_name='Básico')
        self.LDA = LDA
    
    # def tempo_de_broca(self, index, alpha=0.000889, k=3.6):
    #     return (1 / alpha * k) * (math.e**(alpha * self.dados['Comprimento'][index]) - 1)
    
    def tempo_de_manobra(self, taxa=0.003):
        tempo = 0
        fases_anteriores = self.LDA
        for fase, nbrocas in zip(self.dados.fases_pioneiro, self.dados.num_brocas):
            # O comprimento do trecho perfurado foi admitido constante.
            trecho_perfurado = fase / nbrocas
            for _ in range(nbrocas):
                tempo_descida = taxa * (fases_anteriores + trecho_perfurado)
                fases_anteriores += trecho_perfurado
                tempo += tempo_descida
        return tempo
    
    def tempo_de_broca_parada(self):
        num_brocas_usadas = 2 + 2 + 6 + 6
        num_manobras = num_brocas_usadas - 1
        return 2 * num_manobras
    
    # def tempo_de_perfuracao(self, index=0):
    #     return self.tempo_de_broca(index) + self.tempo_de_broca_parada() + self.tempo_de_manobra(index)

    # def custo_completacao(self):
    #     return 0.75 * self.cr * self.tempo_de_perfuracao()
    
    # def c2(self):
    #     if self.modelo == 'Up':
    #         c2 = 0.375
    #     elif self.modelo == 'Base':
    #         c2 = 0.250
    #     elif self.modelo == 'Down':
    #         c2 = 0.125
    #     else:
    #         raise TypeError("Palavra chave do modelo incorreta.")
    #     return c2
    
    # def cap(self):
    #     """Curva de aprendizagem de perfuração - atualizar o tempo de perfuração"""
    #     tempo_pioneiro = self.tempo_de_perfuracao()
    #     c1 = 2/3 * tempo_pioneiro
    #     c2 = self.c2()
    #     c3 = 1/3 * tempo_pioneiro
    #     return c1 * math.e**((1 - self.num_poco) * c2) + c3
    
    # def custo_poco(self, parcela=0.7):
    #     """Custo do total de construção do poço, considerando todas as despesas do CAPEX.

    #     Args:
    #         parcela (float): Percentual referente a soma completação e produção. Defaults to 0.7.

    #     Returns:
    #         float: CAPEX do poço
    #     """
    #     return (1/parcela) * (self.custo_completacao() + self.custo_de_perfuracao() * self.comp_perfurado)
    
    # def custo_de_perfuracao(self):
    #     """Calcular o custo do posto pioneiro - P1."""
    #     cb = 1e3 * (2*58 + 2*45 + 6*23 + 6*16)
    #     cr = 5e5
    #     return (cb + cr * self.tempo_de_perfuracao()) / self.dados['Comprimento']