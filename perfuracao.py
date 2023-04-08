import math
import numpy as np
import numpy_financial as npf
import pandas as pd

class Perfuracao:

    def __init__(self, dados_trabalho, modelo='Base',LDA=1_000) -> None:
        self.dados = pd.read_excel(dados_trabalho, sheet_name='Perfuracao')
        self.modelo = modelo
        self.pocos = pd.read_excel(dados_trabalho, sheet_name='Cronograma_Abertura', parse_dates=[self.modelo], usecols=[self.modelo])
        self.pocos = self.pocos.rename(columns={self.pocos.columns[0]:'open'})
        self.comercialidade = pd.read_excel(dados_trabalho, sheet_name='Stock_Oil_Price', parse_dates=['Ano'], usecols=['Ano']).loc[0, 'Ano']
        self.LDA = LDA
        self.num_pocos = self.pocos.shape[0]
        self.pocos['custo']= self._calcular_custo_poco()
    
    def _tempo_de_broca(self, alpha=0.000889, k=3.6):
        return (1 / (alpha * k)) * (math.e**(alpha * self.dados.fases_pioneiro.sum()) - 1)
    
    def _tempo_de_manobra(self, taxa=0.003):
        tempo_descida = 0
        fases_anteriores = self.LDA
        tempo = 0.5 * taxa * self.LDA
        for fase, nbrocas in zip(self.dados.fases_pioneiro, self.dados.num_brocas):
            # O comprimento do trecho perfurado foi admitido constante.
            trecho_perfurado = fase / nbrocas
            for _ in range(nbrocas):
                tempo_descida = taxa * (fases_anteriores + trecho_perfurado)
                fases_anteriores += trecho_perfurado
                tempo += tempo_descida
        tempo -= 0.5 * tempo_descida
        return tempo
    
    def _tempo_de_broca_parada(self):
        return 2 * (self.dados.num_brocas.sum() - 1)
    
    def _calcular_tempo_de_perfuracao(self, index=0):
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
    
    def _calcular_cap(self):
        """Curva de aprendizagem de perfuração - atualizar o tempo de perfuração"""
        tempo_pioneiro = self._calcular_tempo_de_perfuracao()
        tempo_perf = pd.DataFrame()
        pocos = np.arange(1, self.num_pocos+1)
        c1 = 2/3 * tempo_pioneiro
        c2 = self._c2(self.modelo)
        c3 = 1/3 * tempo_pioneiro
        tempo_perf[self.modelo] = c1 * math.e**((1 - pocos) * c2) + c3
        return tempo_perf
    
    def _custo_broca(self):
        return (self.dados.num_brocas * self.dados.preco_broca).sum()
    
    def _calcular_custo_poco(self, parcela=0.7, sonda=180e3):
        broca = self._custo_broca()
        custo_perf_comp = 1.75 * sonda * self._calcular_cap()
        return (broca + custo_perf_comp) / parcela
    
    def _calcular_valor_presente(self, vf, ano_abert, tma=0.1):
        rate_day = (1 + tma)**(1/365) - 1
        delta_t = (ano_abert - self.comercialidade).days
        vp = vf / (1 + rate_day)**delta_t
        return pd.Series(vp)

    def _calcular_capex_pocos(self):
        return self.pocos.apply(lambda x: self._calcular_valor_presente(x.custo, x.open), axis=1).sum()
    
    def _calcular_capex_subsea(self, a=-67.871986, b=127.33084, c=0.7):
        return (a + b * self.num_pocos**c) * 10**6
    
    def _calcular_capex_fpso(self, capacidade=100, a=-7878.421023, b=5426.536367, c=0.1):
        return (a + b * capacidade**c) * 10**6
    
    def _capex_prod(self, gasoduto=70e6, pr=0.2, ps=0.3, pf=0.15):
        subsea = self._calcular_capex_subsea()
        fpso = self._calcular_capex_fpso()
        pocos = self._calcular_capex_pocos()
        capex_pocos = pocos / pr + gasoduto
        capex_fpso = fpso / pf + gasoduto
        capex_subsea = subsea / ps + gasoduto
        return (capex_pocos + capex_fpso + capex_subsea) / 3

    