import pandas as pd
import numpy_financial as npf
import numpy as np
from .caixa import Caixa
from scipy.optimize import root_scalar


class AEPP:
    def __init__(self, caixa) -> None:
        self.caixa = caixa
        self.preco_atual = self.caixa.prod.price[self.caixa.modelo].values[0]
        self.price_vp_zero = self._find_oil_price_vpl_null()

    def vpl(self):
        return self.caixa()

    def tir(self) -> float:
        return npf.irr(self.caixa.cash_flow())

    def _dispendios_presente(self):
        # valor absoluto
        cf = self.caixa.cash_flow().values
        cf[cf > 0] = 0
        cf = np.insert(cf, 0, 0)
        return -npf.npv(self.caixa.tma, cf)

    def _receitas_futuro(self):
        cf = self.caixa.cash_flow().values
        cf[cf < 0] = 0
        periods = np.arange(0, len(cf))[::-1]
        fv = npf.fv(self.caixa.tma, periods, 0, -cf)
        return np.sum(fv)

    def tgr(self) -> float:
        f = self._receitas_futuro()
        i = self._dispendios_presente()
        n = len(self.caixa.cash_flow()) - 1
        return (f / i) ** (1 / n) - 1

    def il(self):
        caixa_descontado = self.caixa.discounted_cash_flow()
        receitas = caixa_descontado[caixa_descontado > 0].sum()
        disp = - caixa_descontado[caixa_descontado < 0].sum()
        return receitas / disp

    def roi(self):
        return self.caixa.vpl() / self.capex_vp

    def lu(self):
        return self.caixa.vpl() / self.vp_pec

    def _fun_cup(self, x):
        self.prod.price.iloc[:] = x
        self.receitas = self.total_revenue()
        self.capex_prod = self.capex_producao()
        self.despesas = self.total_cost()
        return pd.Series(self.vpl())

    def _find_oil_price_vpl_null(self):
        root = root_scalar(self.caixa, x0=20, x1=100).root
        self.caixa.restore_model()
        return root

    def vpl_zero_model(self):
        self.caixa.prod.price[self.caixa.modelo] = self.price_vp_zero
        self.caixa.update_model()

    def _capex(self):
        capex = self.caixa.capex()
        descom = self.caixa.despesas["descom"]
        return capex + descom

    def _get_vp(self, df):
        df = np.insert(df.values, 0, 0)
        capex_pres = npf.npv(self.caixa.tma, df)
        return capex_pres

    @property
    def capex_vp(self):
        return self._get_vp(self._capex())

    @property
    def opex_vp(self):
        return self._get_vp(self._opex())

    @property
    def tributo_vp(self):
        return self._get_vp(self._tributacao())

    def _opex(self):
        if self.caixa.tarefa in ("4A", "4B"):
            opex = self.caixa.despesas[["opex_var", "opex_fixo", "opex_p16"]].sum(
                axis=1
            )
        else:
            opex = self.caixa.despesas[["opex_var", "opex_fixo"]].sum(axis=1)
        return opex

    def _tributacao(self):
        imposto = self.caixa.despesas["imposto"]
        ir_csll = self.caixa.net_profit_tax()
        return imposto + ir_csll

    def _dispendios_total_presente(self):
        capex = self._capex()
        opex = self._opex()
        tributo = self._tributacao()
        disp = (capex + opex + tributo).values
        disp = np.insert(disp, 0, 0)
        disp_pres = npf.npv(self.caixa.tma, disp)
        return disp_pres

    def _receitas_total_presente(self):
        receitas = self.caixa.receitas.values
        receitas = np.insert(receitas, 0, 0)
        receitas_pres = npf.npv(self.caixa.tma, receitas)
        return receitas_pres

    @property
    def vp_pec(self):
        receita_pres = self._receitas_total_presente()
        price = self.caixa.prod.price.values[0][0]
        vp_pec = receita_pres / price
        return vp_pec

    def cup(self):
        return self.price_vp_zero

    def cui(self):
        self.vpl_zero_model()
        custo_unit_inv = self.capex_vp / self.vp_pec
        self.caixa.restore_model()
        return custo_unit_inv

    def cuo(self):
        self.vpl_zero_model()
        custo_unit_oper = self.opex_vp / self.vp_pec
        self.caixa.restore_model()
        return custo_unit_oper

    def cut(self):
        self.vpl_zero_model()
        custo_unit_trib = self.tributo_vp / self.vp_pec
        self.caixa.restore_model()
        return custo_unit_trib

    def hub_indicadores_economicos(self):
        names = ["vpl", "tir", "tgr", "il", "roi", "lu", "cup", "cui", "cuo", "cut"]
        indicadores = pd.DataFrame(columns=names)
        indicadores.loc[0] = [
            self.caixa.vpl(),
            self.tir(),
            self.tgr(),
            self.il(),
            self.roi(),
            self.lu(),
            self.cup(),
            self.cui(),
            self.cuo(),
            self.cut(),
        ]
        indicadores = indicadores.stack()
        indicadores.index.names = ['zero', 'param']
        indicadores.index = indicadores.index.get_level_values('param')
        return indicadores

