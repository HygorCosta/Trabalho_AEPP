import math
import numpy as np
import numpy_financial as npf
import pandas as pd

class Perfuracao:

    def __init__(self, tarefa, modelo='Base', dados_trabalho='config/dados_trabalho.xlsx', LDA=1_000):
        self.tarefa = tarefa
        self.modelo = modelo
        self.LDA = LDA
        self.dados = pd.read_excel(dados_trabalho, sheet_name='Perfuracao')
        self.pocos = self._set_pocos(dados_trabalho)
        self.comercialidade = pd.read_excel(dados_trabalho, sheet_name='Stock_Oil_Price', parse_dates=['Ano'], usecols=['Ano']).loc[0, 'Ano']
        if tarefa == '1':
            self.pocos['custo'] = 30e6
        else:
            self.pocos['custo'] = self.custo_pocos()

    def _set_pocos(self, dados_trabalho):
        if self.tarefa in ('4A', '4B'):
            sheet = 'Abertura_' + self.tarefa
        else:
            sheet = 'Abertura'
        pocos = pd.read_excel(dados_trabalho, sheet_name=sheet, parse_dates=[self.modelo], usecols=[self.modelo])
        return pocos.rename(columns={pocos.columns[0]:'open'})
    
    def _tempo_de_broca(self, alpha=0.000889, k=3.6):
        return (1 / (alpha * k)) * (math.e**(alpha * self.dados.fases_pioneiro.sum()) - 1)
    
    def _tempo_de_manobra(self, taxa=0.003):
        tempo_manobra = 0
        fases_anteriores = self.LDA
        tempo = [0.5 * taxa * self.LDA]
        for fase, nbrocas in zip(self.dados.fases_pioneiro, self.dados.num_brocas):     
            # O comprimento do trecho perfurado foi admitido constante.
            tempo_fase = 0
            trecho_perfurado = fase / nbrocas
            for _ in range(nbrocas):
                tempo_manobra = taxa * (fases_anteriores + trecho_perfurado)
                tempo_fase += tempo_manobra
                fases_anteriores += trecho_perfurado
            tempo.append(tempo_fase)      
        tempo[-1] = tempo[-1] - 0.5*tempo_manobra
        return np.sum(tempo)
    
    def _tempo_de_broca_parada(self):
        return 2 * (self.dados.num_brocas.sum() - 1)
    
    def _tempo_de_perfuracao(self, index=0):
        return (self._tempo_de_broca() + self._tempo_de_broca_parada() + self._tempo_de_manobra()) / 24
    
    @staticmethod
    def _c2(modelo):
        if modelo == 'Up':
            c2 = 0.375
        elif modelo == 'Base':
            c2 = 0.250
        elif modelo == 'Down':
            c2 = 0.125
        else:
            raise TypeError("Palavra chave do modelo incorreta.")
        return c2
    
    def cap(self):
        """Curva de aprendizagem de perfuração - atualizar o tempo de perfuração"""
        tempo_pioneiro = self._tempo_de_perfuracao()
        tempo_perf = pd.DataFrame()
        pocos = np.arange(1, self.pocos.shape[0] + 1)
        c1 = 2/3 * tempo_pioneiro
        c2 = self._c2(self.modelo)
        c3 = 1/3 * tempo_pioneiro
        tempo_perf[self.modelo] = c1 * math.e**((1 - pocos) * c2) + c3
        return tempo_perf
    
    def _custo_broca(self):
        return (self.dados.num_brocas * self.dados.preco_broca).sum()
    
    def custo_pocos(self, parcela=0.7, sonda=180e3):
        broca = self._custo_broca()
        custo_perf_comp = 1.75 * sonda * self.cap()
        return (broca + custo_perf_comp) / parcela