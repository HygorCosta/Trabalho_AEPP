import pandas as pd
import numpy as np
from .producao import Producao
from .perfuracao import Perfuracao
from .dutos import Dutos
from dateutil.relativedelta import relativedelta
from datetime import date


class PartipacaoEspecial:

    def __init__(self, prod: Producao, perf: Perfuracao, capex_prod, capex) -> None:
        self.tarefa = perf.tarefa
        self.prod_trim = prod.prod_trim
        self.capex_prod = capex_prod
        self.capex = capex
        self.pocos = perf.pocos
        self.price = prod.price[perf.modelo].repeat(4)
        self.price.index = self.prod_trim.index
        self.receita_bruta = self.total_revenue()
        if self.tarefa in ('4A', '4B'):
            self.dutos = Dutos('config/config_tarefa_4.yaml', self.tarefa)
        self.despesas = self.total_cost()
        self.prod_trim['receita_liq'] = self.lucro_liquido_pe()
        self.calcular_partipacao_especial()
        self.values = self._group_by_year(self.prod_trim.part_esp)

    def _group_by_year(self, valor: pd.Series, period='y'):
        grupo = pd.Grouper(level='date', axis=0, freq=period)
        valor.index.name = 'date'
        return valor.groupby(grupo).sum()

    def __get_start_prod_index(self):
        index = pd.Index(pd.DatetimeIndex(self.price.index))
        return index.get_loc(self.pocos.open[0] - relativedelta(days=1)) + 1

    def __init_series(self):
        return pd.Series(np.zeros(len(self.price)), index=self.prod_trim.index)

    def _receita_gas(self, preco_gas=4, fator=37.31):
        return self.prod_trim.gas_prod * preco_gas * fator

    def total_revenue(self):
        rec_oleo = self.prod_trim.oil_prod * self.price * 1000 * 6.29
        return rec_oleo + self._receita_gas()

    def imposto_producao(self, roy=0.1, pasep=0.0925) -> pd.Series:
        return (roy + pasep) * self.receita_bruta

    def opex_variavel(self, co=3, cwi=2, cwp=2, cg=2, fator_gas=1017.532078) -> pd.Series:
        oleo = co * self.prod_trim.oil_prod
        wprod = cwp * self.prod_trim.water_prod
        gas = cg * self.prod_trim.gas_prod / fator_gas
        winj = cwi * self.prod_trim.water_inj
        return (oleo + winj + wprod + gas) * 1000 * 6.29

    def opex_fixo(self, taxa=0.025):
        opex_fixo = self.__init_series()
        id_prod = self.__get_start_prod_index()
        opex_fixo.iloc[id_prod:] = taxa * self.capex_prod / 4
        return opex_fixo

    def descomissionamento(self, taxa=0.2) -> pd.Series:
        descom = self.__init_series()
        descom.iloc[-4:] = taxa * self.capex_prod / 4
        if self.tarefa in ('4A', '4B'):
            descom.iloc[-4:] += self.dutos.descomissionamento() / 4
        return descom

    def _opex_p16(self):
        inicia_serie = self.__init_series()
        opex_16 = self.dutos.opex_trimestral()
        opex = inicia_serie + opex_16
        return opex.fillna(0)

    def total_cost(self) -> pd.DataFrame:
        imposto = self.imposto_producao()
        opex_var = self.opex_variavel()
        opex_fixo = self.opex_fixo()
        descom = self.descomissionamento()
        opex_p16 = self._opex_p16()
        despesas = pd.concat(
            [imposto, opex_var, opex_fixo, descom, opex_p16], axis=1)
        despesas.columns = ['imposto', 'opex_var',
                            'opex_fixo', 'descom', 'opex_p16']
        return despesas

    def lucro_bruto(self):
        return self.receita_bruta - self.despesas.sum(axis=1)

    def _add_depreciacao_p16(self, depreciacao):
        capex_duto = self.dutos.capex()
        data_lanc = date(self.dutos.dados['capex']['ano_lancamento'], 12, 31)
        index = depreciacao.index.get_loc(pd.Timestamp(data_lanc)) + 1 - 4
        rate = self.dutos.dados['capex']['taxa_de_depre']
        periodos = (self.dutos.dados['capex']['anos_depre'] + 1)
        capex_linear = np.linspace(0, rate*capex_duto, periodos)
        capex_linear = np.repeat(capex_linear, 4) / 4
        depreciacao.iloc[index:index+4*periodos] += capex_linear
        return depreciacao

    def depreciacao(self, taxa=0.03, duracao=20*4) -> pd.Series:
        depreciacao = self.__init_series()
        id_prod = self.__get_start_prod_index()
        depreciacao.iloc[id_prod:id_prod+duracao] = taxa * self.capex_prod / 4
        if self.tarefa in ('4A', '4B'):
            depreciacao = self._add_depreciacao_p16(depreciacao)
        return depreciacao

    def net_income_before_tax(self) -> pd.Series:
        return self.lucro_bruto() - self.depreciacao()

    def lucro_liquido_pe(self):
        lucro = self.lucro_bruto()
        depreciacao = self.depreciacao()
        capex = self.capex.repeat(4) / 4
        capex.index = lucro.index
        return lucro - depreciacao - capex

    def net_profit_tax(self, ir=0.25, csll=0.09) -> pd.Series:
        lucro_liq_trib = self.net_income_before_tax()
        lucro_liq_trib[lucro_liq_trib < 0] = 0
        return (ir + csll) * lucro_liq_trib

    def net_income_after_tax(self) -> pd.Series:
        liq_trib = self.net_income_before_tax()
        impostos = self.net_profit_tax()
        return liq_trib - impostos

    def _redutor(self, prod_trim) -> pd.Series:
        redutor = 0
        aliquota = prod_trim.aliquota
        ano = prod_trim.name.year
        anos_base = self.pocos.open[0].year
        if ano == anos_base:
            match aliquota:
                case 0:
                    redutor = 0
                case 0.1:
                    redutor = 1350
                case 0.2:
                    redutor = 1575
                case 0.3:
                    redutor = 1800
                case 0.35:
                    redutor = 675/0.35
                case 0.4:
                    redutor = 2081.25
        if ano == anos_base + 1:
            match aliquota:
                case 0:
                    redutor = 0
                case 0.1:
                    redutor = 1050
                case 0.2:
                    redutor = 1275
                case 0.3:
                    redutor = 1500
                case 0.35:
                    redutor = 570/0.35
                case 0.4:
                    redutor = 1781.25
        if ano == anos_base + 2:
            match aliquota:
                case 0:
                    redutor = 0
                case 0.1:
                    redutor = 750
                case 0.2:
                    redutor = 975
                case 0.3:
                    redutor = 1200
                case 0.35:
                    redutor = 465/0.35
                case 0.4:
                    redutor = 1481.25
        if ano >= anos_base + 3:
            match aliquota:
                case 0:
                    redutor = 0
                case 0.1:
                    redutor = 450
                case 0.2:
                    redutor = 675
                case 0.3:
                    redutor = 900
                case 0.35:
                    redutor = 360/0.35
                case 0.4:
                    redutor = 1181.25
        return pd.Series(redutor, dtype='float64')

    def _aliquota(self, prod_trim) -> pd.Series:
        anos_base = self.pocos.open[0].year
        aliquota = 0
        ano = prod_trim.name.year
        equiv_oil = prod_trim.equiv_oil
        if ano == anos_base:
            if equiv_oil < 1350:
                aliquota = 0
            elif equiv_oil < 1800:
                aliquota = 0.1
            elif equiv_oil < 2250:
                aliquota = 0.2
            elif equiv_oil < 2700:
                aliquota = 0.3
            elif equiv_oil < 3150:
                aliquota = 0.35
            elif equiv_oil > 3150:
                aliquota = 0.4
        if ano == anos_base + 1:
            if equiv_oil < 1050:
                aliquota = 0
            elif equiv_oil < 1500:
                aliquota = 0.1
            elif equiv_oil < 1950:
                aliquota = 0.2
            elif equiv_oil < 2400:
                aliquota = 0.3
            elif equiv_oil < 2850:
                aliquota = 0.35
            elif equiv_oil > 2850:
                aliquota = 0.4
        if ano == anos_base + 2:
            if equiv_oil < 750:
                aliquota = 0
            elif equiv_oil < 1200:
                aliquota = 0.1
            elif equiv_oil < 1650:
                aliquota = 0.2
            elif equiv_oil < 2100:
                aliquota = 0.3
            elif equiv_oil < 2550:
                aliquota = 0.35
            elif equiv_oil > 2550:
                aliquota = 0.4
        if ano >= anos_base + 3:
            if equiv_oil < 450:
                aliquota = 0
            elif equiv_oil < 900:
                aliquota = 0.1
            elif equiv_oil < 1350:
                aliquota = 0.2
            elif equiv_oil < 1800:
                aliquota = 0.3
            elif equiv_oil < 2250:
                aliquota = 0.35
            elif equiv_oil > 2250:
                aliquota = 0.4
        return pd.Series(aliquota, dtype='float64')

    def aliquota_partipacao_especial(self):
        self.prod_trim['aliquota'] = self.prod_trim.apply(
            lambda x: self._aliquota(x), axis=1)

    def _redutor_part_esp(self):
        redutor = self.prod_trim.apply(
            lambda x: self._redutor(x), axis=1)
        self.prod_trim['redutor'] = redutor

    def calcular_partipacao_especial(self):
        self.aliquota_partipacao_especial()
        self._redutor_part_esp()
        prod_liq = self.prod_trim.equiv_oil - self.prod_trim.redutor
        self.prod_trim['part_esp'] = self.prod_trim.aliquota * \
            (prod_liq * self.prod_trim.receita_liq / self.prod_trim.equiv_oil)
        self.prod_trim.part_esp = self.prod_trim.part_esp.fillna(0)
