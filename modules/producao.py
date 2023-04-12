import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path

class Producao:

    def __init__(self, dados_producao, dados_trabalho, modelo='Base') -> None:
        self.producao = pd.DataFrame()
        self._file_name = os.path.splitext(dados_producao)
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
    
    def __m3_to_bbl(self):
        return 6.289814 

    def producao_anual_em_bbl(self):
        grupo = pd.Grouper(key='date', axis=0, freq='Y')
        return self.__m3_to_bbl() *self.df.groupby(grupo).sum()
    
    def prod_trim_em_mm3(self):
        grupo = pd.Grouper(key='date', axis=0, freq='Q')
        prod_trim = self.df.groupby(grupo).sum() / 1_000
        prod_trim['equiv_oil'] = prod_trim.oil_prod + prod_trim.gas_prod / 1017.5321
        prod_trim['receita'] = self._receita_trimestral(prod_trim)
        return prod_trim
    
    def _receita_trimestral(self, prod_trim):
        prod_oleo = prod_trim.oil_prod.to_numpy()
        prod_gas = prod_trim.gas_prod.to_numpy()
        price = np.repeat(self.price['Base'].to_numpy(), 4)
        return price * self.__m3_to_bbl() * 1_000 * prod_oleo + (4*37.31)*prod_gas

    def write_file(self):
        Path("resultados/").mkdir(parents=True, exist_ok=True)
        output_name = 'resultados/' + self._file_name[0] + '_AEPP' + self._file_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.prod_anual.to_excel(writer, sheet_name='Produção Anual')
        self.prod_trim.to_excel(writer, sheet_name='Produção Trimestral')
        writer.close()

        