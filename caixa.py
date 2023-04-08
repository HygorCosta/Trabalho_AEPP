import pandas as pd
import numpy_financial as npf
from perfuracao import Perfuracao
from producao import Producao

class Caixa(Perfuracao, Producao):

    def __init__(self, tarefa, modelo, dados_trabalho, dados_producao) -> None:
       self.tarefa = tarefa
       self.modelo = modelo
       self.perf = Perfuracao(dados_trabalho, modelo)
       self.prod = Producao(dados_producao, dados_trabalho, modelo)
       self.receitas = self.calcular_receitas()
       self.capex_prod = self._capex_prod()
       self.despesas = self.calcular_despesas()

    def _receita_gas(self, preco_gas=4, fator=37.31):
        return self.prod.prod_anual.gas_prod * preco_gas * fator / 1000 / 6.29

    def calcular_receitas(self):
        self.prod.price.index = self.prod.prod_anual.index
        rec_oleo = self.prod.prod_anual.oil_prod * self.prod.price[self.modelo]
        return rec_oleo + self._receita_gas()
    
    @staticmethod
    def _calcular_redutor(aliquota):
        redutor = None
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
        return pd.Series(redutor)
    
    def _calcular_aliquota(self, prod_trim):
        anos_base = pd.DatetimeIndex(self.prod.price.index[:4]).year
        aliquota = None
        red = None
        ano = prod_trim.name.year
        equiv_oil = prod_trim.equiv_oil
        if ano == anos_base[0]:
            if equiv_oil < 1350: aliquota = 0
            elif equiv_oil < 1800: aliquota = 0.1
            elif equiv_oil < 2250: aliquota = 0.2
            elif equiv_oil < 2700: aliquota = 0.3
            elif equiv_oil < 3150: aliquota = 0.35
            elif equiv_oil > 3150: aliquota = 0.4
        if ano == anos_base[1]:
            if equiv_oil < 1050: aliquota = 0
            elif equiv_oil < 1500: aliquota = 0.1
            elif equiv_oil < 1950: aliquota = 0.2
            elif equiv_oil < 2400: aliquota = 0.3
            elif equiv_oil < 2850: aliquota = 0.35
            elif equiv_oil > 2850: aliquota = 0.4
        if ano == anos_base[2]:
            if equiv_oil < 750: aliquota = 0
            elif equiv_oil < 1200: aliquota = 0.1
            elif equiv_oil < 1650: aliquota = 0.2
            elif equiv_oil < 2100: aliquota = 0.3
            elif equiv_oil < 2550: aliquota = 0.35
            elif equiv_oil > 2550: aliquota = 0.4
        if ano >= anos_base[3]:
            if equiv_oil < 450: aliquota = 0
            elif equiv_oil < 900: aliquota = 0.1
            elif equiv_oil < 1350: aliquota = 0.2
            elif equiv_oil < 1800: aliquota = 0.3
            elif equiv_oil < 2250: aliquota = 0.35
            elif equiv_oil > 2250: aliquota = 0.4
        return pd.Series(aliquota)
    
    def _aliquota_partipacao_especial(self):
        self.prod.prod_trim['aliquota'] = self.prod.prod_trim.apply(lambda x: self._calcular_aliquota(x), axis=1)
    
    def _pe_redutor(self):
        redutor = self.prod.prod_trim.apply(lambda x: self._calcular_redutor(x.aliquota), axis=1)
        self.prod.prod_trim['redutor'] = redutor
    
    def _calcular_part_especial(self):
        self._aliquota_partipacao_especial()
        self._pe_redutor()
        ptrim = self.prod.prod_trim
        bruto = ptrim.receita * ptrim.aliquota
        desconto = (ptrim.redutor / ptrim.equiv_oil).fillna(0)
        self.prod.prod_trim['part_esp'] = bruto * (1 - desconto)

    def calcular_despesas(self):
        despesas = pd.DataFrame()
        despesas['impostos'] = self._calcular_imposto_producao()
        despesas['opex_var'] = self._calcular_opex_variavel()
        despesas['opex_fixo'] = self._calcular_opex_fixo()
        despesas['descom'] = 0
        despesas['descom'][-1] = self._calcular_descom()
        return despesas

    def _calcular_imposto_producao(self, roy=0.1, pasep=0.0925):
        self._calcular_part_especial()
        taxa = roy + pasep
        imp_direto = taxa * self.receitas
        grupo = pd.Grouper(axis=0, freq='Y')
        part_esp = self.prod.prod_trim.part_esp.groupby(grupo).sum()
        return imp_direto + part_esp
    
    def _calcular_opex_variavel(self, co=3, cwi=2, cwp=2, cg=2):
        oleo =  co * self.prod.prod_anual.oil_prod
        winj =  cwi * self.prod.prod_anual.water_inj
        wprod =  cwi * self.prod.prod_anual.water_prod
        gas =  cg * self.prod.prod_anual.gas_prod / 1017.5321
        return oleo + winj + wprod + gas
    
    def _calcular_valor_presente(self, vf, ano_abert, ano_base, tma=0.1):
        rate_day = (1 + tma)**(1/365) - 1
        delta_t = (ano_abert - ano_base).days
        vp = vf / (1 + rate_day)**delta_t
        return pd.Series(vp)

    def _calcular_capex_pocos(self):
        return self.perf.pocos.apply(lambda x: self._calcular_valor_presente(x.custo, x.open, self.perf.comercialidade), axis=1).sum()
    
    def _calcular_capex_subsea(self, a=-67.871986, b=127.33084, c=0.7):
        return (a + b * self.perf.num_pocos**c) * 10**6
    
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

    def _calcular_opex_fixo(self, taxa=0.025):
        return taxa * self.capex_prod
    
    def _calcular_descom(self, taxa=0.2):
        return taxa * self.capex_prod
    
    def calcular_lucro_bruto(self):
        return self.receitas - self.despesas.sum(axis=1)
    
    def _calcular_depreciacao(self, taxa=0.03):
        return taxa * self.capex_prod

