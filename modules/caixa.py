import pandas as pd
import numpy as np
import numpy_financial as npf
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from scipy.optimize import root
from .perfuracao import Perfuracao
from .producao import Producao, ProducaoTarefa01
from .dutos import Dutos
from .partipacao_especial import PartipacaoEspecial


class Caixa:

    def __init__(self, tarefa: str, modelo='Base', dados_producao=None):
        self.tarefa = tarefa
        self.modelo = modelo
        self.perf = Perfuracao(tarefa, modelo)
        if tarefa == '1':
            self.prod = ProducaoTarefa01()
        else:
            self.prod = Producao(dados_producao, modelo)
        if tarefa in ('4A', '4B'):
            self.dutos = Dutos('config/config_tarefa_4.yaml', tarefa)
        self.capex_prod = self.capex_producao()
        self.part_esp = PartipacaoEspecial(
            self.prod, self.perf, self.capex_prod, self.capex(), self.payment_loan_price())
        self.receitas = self.total_revenue()
        self.despesas = self.total_cost()
        self.tma = 0.1

    def __str__(self):
        return f'O VPL do projeto eh de $ {self.vpl():,.2f}.'

    def _start_prod_index(self):
        index = pd.Index(pd.DatetimeIndex(self.prod.price.index).year)
        return index.get_loc(self.perf.pocos.open[0].year)

    def __init_cost_series(self):
        ref = self.prod.prod_anual.index
        return pd.Series(np.zeros(len(ref)), index=ref)

    def _group_by_year(self, valor: pd.Series, period='Y'):
        grupo = pd.Grouper(level='date', axis=0, freq=period)
        valor.index.name = 'date'
        return valor.groupby(grupo).sum()

    def total_revenue(self):
        return self._group_by_year(self.part_esp.receita_bruta)
    
    def _fix_descom(self, despesas):
        descom = np.zeros_like(despesas.descom.values)
        valor_total = despesas.descom.sum()
        descom[-1] = valor_total
        return descom
    
    def _fix_imposto(self, despesas, pasep=0.0925):
        impostos = despesas.imposto.values
        impostos += pasep * self.receitas.values
        impostos += self.part_esp.values.to_numpy()
        return impostos

    def total_cost(self) -> pd.DataFrame:
        despesas = self._group_by_year(self.part_esp.despesas)
        despesas.descom = self._fix_descom(despesas)
        despesas.imposto = self._fix_imposto(despesas)
        return despesas

    def _npv(self, vf, data_despesa, tma=0.1, period='Y'):
        comercialidade = datetime.strptime(
            str(self.perf.comercialidade), r'%Y-%m-%d %H:%M:%S')
        data = datetime.strptime(str(data_despesa), r'%Y-%m-%d %H:%M:%S')
        if period == 'Y':
            time_step = data.year - comercialidade.year
        elif period == 'd':
            time_step = (data - comercialidade).days
        else:
            raise TypeError("Período inválido.")
        vp = vf / (1 + tma)**time_step
        return pd.Series(vp)

    def capex_pocos(self):
        return self.perf.pocos.apply(lambda x: self._npv(x.custo, x.open, tma=0.0261158/100, period='d'), axis=1).sum()

    def capex_subsea(self, a=-67.871986, b=127.33084, c=0.7):
        return (a + b * self.perf.pocos.shape[0]**c) * 10**6

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
        match str(self.tarefa):
            case '3':
                capex_prod += 170e6
        return float(capex_prod)

    def lucro_bruto(self):
        return self.receitas - self.despesas.sum(axis=1)

    def depreciacao(self, taxa=0.03, duracao=20) -> pd.Series:
        return self._group_by_year(self.part_esp.depreciacao())

    def valor_residual(self, taxa=0):
        capex_prod = self.__init_cost_series() + self.capex_prod
        return taxa * capex_prod

    def net_income_before_tax(self) -> pd.Series:
        residual = self.valor_residual()
        bruto = self.lucro_bruto()
        depreciacao = self.depreciacao()
        return bruto - depreciacao + residual

    def net_profit_tax(self, ir=0.25, csll=0.09) -> pd.Series:
        lucro_liq_trib = self.net_income_before_tax()
        lucro_liq_trib[lucro_liq_trib < 0] = 0
        return (ir + csll) * lucro_liq_trib

    def net_income_after_tax(self) -> pd.Series:
        liq_trib = self.net_income_before_tax()
        impostos = self.net_profit_tax()
        return liq_trib - impostos

    def payment_loan_sac(self, perc_fin=0.8, taxa=6.78/100, nparc=20):
        financ = pd.DataFrame(0, columns=[
                              'saldo_devedor', 'juros', 'amortizacao', 'pagamento'], index=self.__init_cost_series().index)
        pgto = 0
        saldo_dev = perc_fin * self.capex_prod
        amort = saldo_dev / nparc
        for id in financ.index[:nparc]:
            juros = taxa * saldo_dev
            pgto = amort + juros
            saldo_dev -= amort
            financ.loc[id] = [saldo_dev, juros, amort, pgto]
        return financ

    def payment_loan_price(self, perc_fin=0.8, taxa=6.78/100, nparc=20):
        financ = pd.DataFrame(0, columns=[
                              'saldo_devedor', 'juros', 'amortizacao', 'pagamento'], index=self.__init_cost_series().index)
        saldo_dev = perc_fin * self.capex_prod
        parcela = saldo_dev*((1+taxa)**nparc * taxa)/((1+taxa)**nparc - 1)
        for id in financ.index[:nparc]:
            juros = taxa * saldo_dev
            amort = parcela - juros
            saldo_dev -= amort
            financ.loc[id] = [saldo_dev, juros, amort, parcela]
        return financ

    def _add_capex_p16(self, capex):
        capex_duto = self.dutos.capex()
        data_lanc = date(self.dutos.dados['capex']['ano_lancamento'], 12, 31)
        capex[data_lanc] = capex_duto
        return capex

    def capex(self, tma=0.1, parcela=0.8):
        inv = self.payment_loan_price().pagamento
        proprio_fv = (1 + tma) * (1 - parcela) * self.capex_prod
        inv.iloc[0] += proprio_fv
        if self.tarefa in ('4A', '4B'):
            inv = self._add_capex_p16(inv)
        return inv

    def cash_flow(self):
        liquido = self.net_income_after_tax()
        depreciacao = self.depreciacao()
        return liquido + depreciacao - self.capex()

    def discounted_cash_flow(self):
        cash_flow = self.cash_flow().reset_index()
        cash_flow.columns = ['date', 'parcelas']
        disc_cf = cash_flow.apply(lambda x: npf.pv(self.tma, x.name+1, 0, -x.parcelas), axis=1)
        disc_cf.index = self.__init_cost_series().index
        disc_cf.columns = ['cash_flow_disc']
        return disc_cf

    def vpl(self) -> float:
        return float(self.discounted_cash_flow().sum())