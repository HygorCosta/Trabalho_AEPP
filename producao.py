import os
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Producao:

    def __init__(self, dados_producao, dados_trabalho, modelo) -> None:
        self.producao = pd.DataFrame()
        self._split_name = os.path.splitext(dados_producao)
        self.df = self.configurar_producao(dados_producao)
        self.price = pd.read_excel(dados_trabalho, sheet_name='Stock_Oil_Price', index_col=0, parse_dates=['Ano'], usecols=['Ano', modelo])
        self.prod_anual = self.producao_anual_em_bbl()
        self.prod_trim = self.prod_trim_em_mm3()

    def configurar_producao(self, producao_excel):
        prod = pd.read_excel(producao_excel, skiprows = range(0, 2))
        prod.columns = ['time', 'date', 'oil_prod', 'water_prod', 'gas_prod', 'water_inj']
        prod = prod.drop(['time'], axis=1)
        data_original = prod.date[:-1]
        prod = prod.shift(-1)[:-1]
        prod.date = pd.to_datetime(data_original)
        return prod

    def producao_anual_em_bbl(self):
        fator_conv = 6.29
        grupo = pd.Grouper(key='date', axis=0, freq='Y')
        return fator_conv *self.df.groupby(grupo).sum()
    
    def prod_trim_em_mm3(self):
        grupo = pd.Grouper(key='date', axis=0, freq='Q')
        prod_trim = self.df.groupby(grupo).sum() / 1_000
        prod_trim['equiv_oil'] = prod_trim.oil_prod + prod_trim.gas_prod / 1017.5321
        prod_trim['receita'] = self._calcular_receita_trimestral(prod_trim)
        return prod_trim
    
    def _calcular_receita_trimestral(self, prod_trim):
        prod_oleo = prod_trim.oil_prod.to_numpy()
        prod_gas = prod_trim.gas_prod.to_numpy()
        price = np.repeat(self.price['Base'].to_numpy(), 4)
        return price * 6.29 * 1_000 * prod_oleo + (4*37.31)*prod_gas

    def write_file(self):
        output_name = self._split_name[0] + '_AEPP' + self._split_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.prod_anual.to_excel(writer, sheet_name='Produção Anual')
        self.prod_trim.to_excel(writer, sheet_name='Produção Trimestral')
        writer.close()

        