import pandas as pd
from .caixa import Caixa


class AEPP:

    def __init__(self, caixa: Caixa) -> None:
        self.caixa = caixa

    def tir(self) -> float:
        return npf.irr(self.cash_flow())

    def _valor_futuro(self, valor, nint):
        return pd.Series(valor * (1 + self.tma)**nint)

    def _global_dispendios_presente(self):
        cf = self.cash_flow().rename('valor').reset_index()['valor']
        cf[cf > 0] = 0
        return -npf.npv(self.tma, cf.to_numpy())

    def _global_receitas_futuro(self):
        cf = self.cash_flow().rename('valor').reset_index()['valor']
        cf[cf < 0] = 0
        return cf.apply(lambda x: npf.fv(self.tma, len(cf) - 1 - cf.loc[cf == x].index[0], 0, -x)).sum()

    def _global_receitas_presente(self):
        cf = self.cash_flow().rename('valor').reset_index()['valor']
        cf[cf < 0] = 0
        return npf.npv(self.tma, cf.to_numpy())

    # TODO: corrigir parâmetros econômicos
    def tgr(self) -> float:
        f = self._global_receitas_futuro()
        i = self._global_dispendios_presente()
        n = len(self.cash_flow())
        return (f/i)**(1/n) - 1

    def il(self):
        disp = self._global_dispendios_presente()
        receitas = self._global_receitas_presente()
        return receitas/disp

    def roi(self):
        capex_pres = npf.npv(self.tma, self.capex().to_numpy())
        return self.vpl() / capex_pres

    def lu(self):
        receita_pres = npf.npv(self.tma, self.receitas.to_numpy())
        price = self.prod.price.iloc[0]
        vol_oil = receita_pres / price
        return float(self.vpl() / vol_oil)

    def _fun_cup(self, x):
        self.prod.price.iloc[:] = x
        self.receitas = self.total_revenue()
        self.capex_prod = self.capex_producao()
        self.despesas = self.total_cost()
        return pd.Series(self.vpl())

    def _find_oil_price_vpl_null(self):
        or_price = self.prod.price
        x0 = self.prod.price.mean()['Base']
        _ = self._fun_cup(x0)
        raiz = root(self._fun_cup, x0)
        self.price_vpl_null = raiz.x
        self._update_model(raiz.x)

    def _update_model(self, price):
        self.prod.price.iloc[:] = price
        self.receitas = self.total_revenue()
        self.capex_prod = self.capex_producao()
        self.despesas = self.total_cost()

    def _receitas_vpl_zero(self):
        self._update_model(self.price_vpl_null)
        receitas_pe = self.receitas.to_numpy()
        return receitas_pe

    def _dispendios_vpl_zero(self):
        self._update_model(self.price_vpl_null)
        disp = self._global_dispendios_presente()
        return disp

    def cup(self):
        if self.price_vpl_null:
            self._find_oil_price_vpl_null()
        receita_pres = npf.npv(self.tma, self.receitas.to_numpy())
        vp_pec = receita_pres / self.or_vpl_null
        disp = self._dispendios_vpl_zero()
        self._restore_original()
        return float(disp / vp_pec)

    def cui(self):
        if self.price_vpl_null:
            self._find_oil_price_vpl_null()
        receita_pres = npf.npv(self.tma, self.receitas.to_numpy())
        vp_capex = npf.npv(self.tma, self.capex().to_numpy())
        vp_pec = receita_pres / self.or_vpl_null
        self._restore_original()
        return float(vp_capex / vp_pec)

    def cuo(self):
        pass

    def cut(self):
        pass
