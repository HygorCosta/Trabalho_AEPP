import pandas as pd
import numpy as np
from .producao import Producao
from .perfuracao import Perfuracao
from .dutos import Dutos
from dateutil.relativedelta import relativedelta
from datetime import date


class PartipacaoEspecial:
    def __init__(
        self, prod: Producao, perf: Perfuracao, capex_prod, capex, financiamento
    ):
        self.tarefa = perf.tarefa
        self.prod_trim = prod.prod_trim
        self.capex_prod = capex_prod
        self.capex = capex
        self.financiamento = financiamento
        self.pocos = perf.pocos
        self.price = prod.price[perf.modelo].repeat(4)
        self.price.index = self.prod_trim.index
        self.receita_bruta = self.total_revenue()
        if self.tarefa in ("4A", "4B"):
            self.dutos = Dutos("config/config_tarefa_4.yaml", self.tarefa)
        self.despesas = self.total_cost()
        self.calcular_partipacao_especial()
        self.values = self.prod_trim.part_esp.groupby(self.prod_trim.index.year).sum()

    def _group_by_year(self, valor: pd.Series, period="y"):
        grupo = pd.Grouper(level="date", axis=0, freq=period)
        valor.index.name = "date"
        return valor.groupby(grupo).sum()

    def _p0(self):
        return self.price.index.year.get_loc(self.pocos.open.dt.year[0]).start

    def __init_series(self):
        return pd.Series(np.zeros(len(self.price)), index=self.prod_trim.index)

    def _receita_gas(self, preco_gas=4, fator=37.31):
        return self.prod_trim.gas_prod * preco_gas * fator

    def total_revenue(self):
        rec_oleo = self.prod_trim.oil_prod * self.price * 1000 * 6.29
        return rec_oleo + self._receita_gas()

    def imposto_producao(self, roy=0.1, pasep=0):
        return (roy + pasep) * self.receita_bruta

    def opex_variavel(self, co=3, cwi=2, cwp=2, cg=2, fator_gas=1017.045686):
        return (
            self.prod_trim.loc[:, ['oil_prod', 'water_prod', 'gas_prod', 'water_inj']]
            .mul([co, cwp, cg/fator_gas, cwi], axis="columns")
            .sum(axis=1)
            * 1000
            * 6.29
        )

    def opex_fixo(self, taxa=0.025):
        opex_fixo = pd.Series(0, index=self.prod_trim.index)
        opex_fixo.iloc[self._p0() :] = taxa * self.capex_prod / 4
        return opex_fixo

    def provisao_descomissionamento(self, taxa=0.2, duracao=20 * 4):
        descom = pd.Series(0, index=self.prod_trim.index)
        descom.iloc[-duracao:] = taxa * self.capex_prod / duracao
        if self.tarefa in ("4A", "4B"):
            descom.iloc[-duracao:] += self.dutos.descomissionamento() / duracao
        return descom

    def _opex_p16(self):
        inicia_serie = self.__init_series()
        opex_16 = self.dutos.opex_trimestral()
        opex = inicia_serie + opex_16
        return opex.fillna(0)

    def total_cost(self):
        imposto = self.imposto_producao()
        opex_var = self.opex_variavel()
        opex_fixo = self.opex_fixo()
        descom = self.provisao_descomissionamento()
        list_desp = [imposto, opex_var, opex_fixo, descom]
        nomes = ["imposto", "opex_var", "opex_fixo", "descom"]
        if self.tarefa in ("4A", "4B"):
            opex_p16 = self._opex_p16()
            list_desp.append(opex_p16)
            nomes.append("opex_p16")
        despesas = pd.concat(list_desp, axis=1)
        despesas.columns = nomes
        return despesas

    def lucro_bruto(self):
        return self.receita_bruta - self.despesas.sum(axis=1)

    def _add_depreciacao_p16(self, depreciacao):
        capex_duto = self.dutos.capex()
        data_lanc = date(self.dutos.dados["capex"]["ano_lancamento"], 12, 31)
        index = depreciacao.index.get_loc(pd.Timestamp(data_lanc)) + 1 - 4
        rate = self.dutos.dados["capex"]["taxa_de_depre"]
        periodos = self.dutos.dados["capex"]["anos_depre"] + 1
        capex_linear = np.linspace(0, rate * capex_duto, periodos)
        capex_linear = np.repeat(capex_linear, 4) / 4
        depreciacao.iloc[index : index + 4 * periodos] += capex_linear
        return depreciacao

    def depreciacao(self, taxa=0.03, duracao=20 * 4):
        depreciacao = pd.Series(0, index=self.prod_trim.index)
        depreciacao.iloc[self._p0() : self._p0() + duracao] = taxa * self.capex_prod / 4
        if self.tarefa in ("4A", "4B"):
            depreciacao = self._add_depreciacao_p16(depreciacao)
        return depreciacao

    def juros_financiamento(self):
        juros = self.financiamento.juros.repeat(4) / 4
        return pd.Series(juros.to_numpy(), index=self.prod_trim.index)

    def lucro_liquido_pe(self):
        lucro = self.lucro_bruto()
        depreciacao = self.depreciacao()
        juros = self.juros_financiamento()
        self.prod_trim["receita_liq"] = lucro - depreciacao - juros

    def _redutor(self, prod_trim):
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
                    redutor = 675 / 0.35
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
                    redutor = 570 / 0.35
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
                    redutor = 465 / 0.35
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
                    redutor = 360 / 0.35
                case 0.4:
                    redutor = 1181.25
        return pd.Series(redutor, dtype="float64")

    def _aliquota(self, prod_trim):
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
        return pd.Series(aliquota, dtype="float64")

    def aliquota_partipacao_especial(self):
        self.prod_trim["aliquota"] = self.prod_trim.apply(
            lambda x: self._aliquota(x), axis=1
        )

    def _redutor_part_esp(self):
        redutor = self.prod_trim.apply(lambda x: self._redutor(x), axis=1)
        self.prod_trim["redutor"] = redutor

    def calcular_partipacao_especial(self):
        self.lucro_liquido_pe()
        self.aliquota_partipacao_especial()
        self._redutor_part_esp()
        receita_liq = self.prod_trim.receita_liq.copy()
        receita_liq[receita_liq < 0] = 0
        prod_liq = self.prod_trim.equiv_oil - self.prod_trim.redutor
        self.prod_trim["part_esp"] = self.prod_trim.aliquota * (
            prod_liq * receita_liq / self.prod_trim.equiv_oil
        )
        self.prod_trim.part_esp = self.prod_trim.part_esp.fillna(0)