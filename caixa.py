import pandas as pd
import numpy as np
import numpy_financial as npf
from dateutil.relativedelta import relativedelta
from datetime import datetime
from perfuracao import Perfuracao
from producao import Producao
from pathlib import Path

class Caixa:

    def __init__(self, tarefa, modelo, dados_trabalho, dados_producao) -> None:
       self.tarefa = tarefa
       self.modelo = modelo
       self.perf = Perfuracao(tarefa, dados_trabalho, modelo)
       self.prod = Producao(dados_producao, dados_trabalho, modelo)
       self.receitas = self.total_revenue()
       self.capex_prod = self.capex_producao()
       self.despesas = self.total_cost()

    def __str__(self):
        return f'O valor presente liquido do projeto eh de $ {self.vpl():,.2f}.'

    def _receita_gas(self, preco_gas=4, fator=37.31):
        m3_to_bbl = 6.289814
        return self.prod.prod_anual.gas_prod * preco_gas * fator / 1000 / m3_to_bbl

    def total_revenue(self):
        self.prod.price.index = self.prod.prod_anual.index
        rec_oleo = self.prod.prod_anual.oil_prod * self.prod.price[self.modelo]
        return rec_oleo + self._receita_gas()
    
    def _redutor(self, aliquota) -> pd.Series:
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
        return pd.Series(redutor, dtype='float64')
    
    def _aliquota(self, prod_trim) -> pd.Series:
        # anos_base = pd.DatetimeIndex(self.perf.pocos.open).year[0]
        anos_base = self.perf.pocos.open[0].year
        aliquota = None
        red = None
        ano = prod_trim.name.year
        equiv_oil = prod_trim.equiv_oil
        if ano == anos_base:
            if equiv_oil < 1350: aliquota = 0
            elif equiv_oil < 1800: aliquota = 0.1
            elif equiv_oil < 2250: aliquota = 0.2
            elif equiv_oil < 2700: aliquota = 0.3
            elif equiv_oil < 3150: aliquota = 0.35
            elif equiv_oil > 3150: aliquota = 0.4
        if ano == anos_base + 1:
            if equiv_oil < 1050: aliquota = 0
            elif equiv_oil < 1500: aliquota = 0.1
            elif equiv_oil < 1950: aliquota = 0.2
            elif equiv_oil < 2400: aliquota = 0.3
            elif equiv_oil < 2850: aliquota = 0.35
            elif equiv_oil > 2850: aliquota = 0.4
        if ano == anos_base + 2:
            if equiv_oil < 750: aliquota = 0
            elif equiv_oil < 1200: aliquota = 0.1
            elif equiv_oil < 1650: aliquota = 0.2
            elif equiv_oil < 2100: aliquota = 0.3
            elif equiv_oil < 2550: aliquota = 0.35
            elif equiv_oil > 2550: aliquota = 0.4
        if ano >= anos_base + 3:
            if equiv_oil < 450: aliquota = 0
            elif equiv_oil < 900: aliquota = 0.1
            elif equiv_oil < 1350: aliquota = 0.2
            elif equiv_oil < 1800: aliquota = 0.3
            elif equiv_oil < 2250: aliquota = 0.35
            elif equiv_oil > 2250: aliquota = 0.4
        return pd.Series(aliquota, dtype='float64')
    
    def aliquota_partipacao_especial(self):
        self.prod.prod_trim['aliquota'] = self.prod.prod_trim.apply(lambda x: self._aliquota(x), axis=1)
    
    def _redutor_part_esp(self):
        redutor = self.prod.prod_trim.apply(lambda x: self._redutor(x.aliquota), axis=1)
        self.prod.prod_trim['redutor'] = redutor
    
    def partipacao_especial(self):
        self.aliquota_partipacao_especial()
        self._redutor_part_esp()
        ptrim = self.prod.prod_trim
        bruto = ptrim.receita * ptrim.aliquota
        desconto = (ptrim.redutor / ptrim.equiv_oil).fillna(0)
        self.prod.prod_trim['part_esp'] = bruto * (1 - desconto)

    def total_cost(self) -> pd.DataFrame:
        despesas = self.cost_of_goods_sold()
        return despesas.join(self.fix_cost())
    
    def fix_cost(self) -> pd.DataFrame:
        despesas = pd.DataFrame()
        despesas['opex_fixo'] = self.opex_fixo()
        despesas['descom'] = self.descomissionamento()
        return despesas

    def cost_of_goods_sold(self) -> pd.DataFrame:
        despesas = pd.DataFrame()
        despesas['impostos'] = self.imposto_producao()
        despesas['opex_var'] = self.opex_variavel()
        return despesas

    def imposto_producao(self, roy=0.1, pasep=0.0925) -> pd.Series:
        self.partipacao_especial()
        taxa = roy + pasep
        imp_direto = taxa * self.receitas
        grupo = pd.Grouper(axis=0, freq='Y')
        part_esp = self.prod.prod_trim.part_esp.groupby(grupo).sum()
        return imp_direto + part_esp
    
    @staticmethod
    def __diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
    
    def opex_variavel(self, co=3, cwi=2, cwp=2, cg=2) -> pd.Series:
        oleo =  co * self.prod.prod_anual.oil_prod
        winj =  cwi * self.prod.prod_anual.water_inj
        wprod =  cwi * self.prod.prod_anual.water_prod
        gas =  cg * self.prod.prod_anual.gas_prod / 1017.5321
        return oleo + winj + wprod + gas
    
    def _npv(self, vf, data_despesa, tma=0.1, period='Y'):
        comercialidade = datetime.strptime(str(self.perf.comercialidade), r'%Y-%m-%d %H:%M:%S')
        data = datetime.strptime(str(data_despesa), r'%Y-%m-%d %H:%M:%S')
        if period == 'Y':
            time_step = data.year - comercialidade.year
        elif period == 'd':
            time_step = (data - comercialidade).days
        elif period == 'M':
            time_step = self.__diff_month(data_despesa, self.perf.comercialidade)
        else:
            raise TypeError("Período inválido.")
        vp = vf / (1 + tma)**time_step
        return pd.Series(vp)

    def capex_pocos(self):
        return self.perf.pocos.apply(lambda x: self._npv(x.custo, x.open, tma=0.0261158/100, period='d'), axis=1).sum()
    
    def capex_subsea(self, a=-67.871986, b=127.33084, c=0.7):
        return (a + b * self.perf.num_pocos**c) * 10**6
    
    def capex_fpso(self, capacidade=100, a=-7878.421023, b=5426.536367, c=0.1):
        return (a + b * capacidade**c) * 10**6
    
    def capex_producao(self, gasoduto=70e6, pr=0.2, ps=0.3, pf=0.15) -> float:
        subsea = self.capex_subsea()
        fpso = self.capex_fpso()
        pocos = self.capex_pocos()
        capex_pocos = pocos / pr + gasoduto
        capex_fpso = fpso / pf + gasoduto
        capex_subsea = subsea / ps + gasoduto
        capex_prod = (capex_pocos + capex_fpso + capex_subsea) / 3
        match self.tarefa:
            case 3:
                capex_prod += 170e6
        return float(capex_prod)
    
    def __get_start_prod_index(self):
        index = pd.Index(pd.DatetimeIndex(self.prod.price.index).year)
        return index.get_loc(self.perf.pocos.open[0].year)
    
    def __init_cost_series(self):
        return pd.Series(np.zeros(len(self.prod.price.index)), index=self.prod.price.index)

    def opex_fixo(self, taxa=0.025):
        opex_fixo = self.__init_cost_series()
        id_prod = self.__get_start_prod_index()
        opex_fixo.iloc[id_prod:] = taxa * self.capex_prod
        return opex_fixo.replace()
    
    def descomissionamento(self, taxa=0.2) -> pd.Series:
        descom = self.__init_cost_series()
        descom.iloc[-1] = taxa * self.capex_prod
        return descom
    
    def gross_profit(self):
        return self.receitas.sum() - self.cost_of_goods_sold().sum()
    
    def lucro_bruto(self):
        return self.receitas - self.despesas.sum(axis=1)
    
    def depreciacao(self, taxa=0.03, duracao=20) -> pd.Series:
        depreciacao = self.__init_cost_series()
        id_prod = self.__get_start_prod_index()
        depreciacao.iloc[id_prod:id_prod+duracao] = taxa * self.capex_prod
        return depreciacao
    
    def valor_residual(self, taxa=0):
        capex_prod = self.__init_cost_series() + self.capex_prod
        return taxa * capex_prod
    
    def net_income_before_tax(self) -> pd.Series:
        residual = self.valor_residual()
        bruto = self.lucro_bruto()
        depreciacao = self.depreciacao()
        return bruto - depreciacao + residual

    def net_profit_tax(self, ir= 0.25, csll=0.09)  -> pd.Series:
        lucro_liq_trib = self.net_income_before_tax()
        lucro_liq_trib[lucro_liq_trib < 0] = 0
        return (ir + csll) * lucro_liq_trib

    def net_income_after_tax(self) -> pd.Series:
        liq_trib = self.net_income_before_tax()
        impostos = self.net_profit_tax()
        return liq_trib - impostos
    
    def payment_loan_sac(self, perc_fin=0.8, taxa=6.78/100, nparc=20):
        financ = pd.DataFrame(0, columns=['Saldo_Devedor', 'Juros', 'Amortizacao', 'Pagamento'], index=self.__init_cost_series().index)
        self.__perc_fin = 0.8
        pgto = 0
        saldo_dev = perc_fin * self.capex_prod
        amort = saldo_dev / nparc
        for id in financ.index[:nparc]:
            juros = taxa * saldo_dev
            pgto = amort + juros
            saldo_dev -= amort
            financ.loc[id] = [saldo_dev, juros, amort, pgto]
        return financ

    def capex(self, tma=0.1):
        # capex = self.payment_loan_sac()
        capex = self.payment_loan_sac()['Pagamento']
        proprio_fv = (1 + tma) * (1 - self.__perc_fin) * self.capex_prod
        capex.iloc[0] += proprio_fv 
        return capex
    
    def cash_flow(self):
        liquido = self.net_income_after_tax()
        depreciacao = self.depreciacao()
        return liquido + depreciacao - self.capex()

    def discounted_cash_flow(self):
        cash_flow = self.cash_flow().to_frame(name='valor').reset_index()
        return cash_flow.apply(lambda x: self._npv(x.valor, x.date + relativedelta(days=1)), axis=1)
    
    def vpl(self) -> float:
        return self.discounted_cash_flow().sum().iloc[0]
        
    def write_results(self):
        Path("resultados/").mkdir(parents=True, exist_ok=True)
        output_name = 'resultados/' + self.prod._file_name[0] + '_AEPP' + self.prod._file_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.prod.prod_anual.to_excel(writer, sheet_name='Prod_Anual')
        self.prod.prod_trim.to_excel(writer, sheet_name='Prod_Trimestral_PE')
        self.payment_loan_sac().to_excel(writer, sheet_name='Financiamento')
        writer.close()
