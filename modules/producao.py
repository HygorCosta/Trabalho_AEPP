import os
import math
import numpy as np
import pandas as pd
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from pathlib import Path


class Producao:

    def __init__(self, dados_producao, modelo='Base', dados_trabalho='config/dados_trabalho.xlsx') -> None:
        self.producao = pd.DataFrame()
        self._file_name = os.path.basename(dados_producao)
        self._file_name = os.path.splitext(self._file_name)
        self.df = self.configurar_producao(dados_producao)
        self.price = pd.read_excel(dados_trabalho, sheet_name='Stock_Oil_Price', index_col=0, parse_dates=[
                                   'Ano'], usecols=['Ano', modelo])
        self.prod_anual = self.producao_anual_em_bbl()
        self.prod_trim = self.prod_trim_em_mm3()

    def configurar_producao(self, producao_excel):
        prod = pd.read_excel(producao_excel, skiprows=range(0, 2))
        prod.columns = ['time', 'date', 'oil_prod',
                        'water_prod', 'gas_prod', 'water_inj']
        prod = prod.drop(['time'], axis=1)
        data_original = prod.date[:-1]
        prod = prod.shift(-1)[:-1]
        prod.date = pd.to_datetime(data_original)
        return prod

    def __m3_to_bbl(self):
        return 6.289814

    def producao_anual_em_bbl(self):
        grupo = pd.Grouper(key='date', axis=0, freq='Y')
        return self.__m3_to_bbl() * self.df.groupby(grupo).sum()

    def prod_trim_em_mm3(self, fator_gas = 1017.045686):
        grupo = pd.Grouper(key='date', axis=0, freq='Q')
        prod_trim = self.df.groupby(grupo).sum() / 1_000
        prod_trim['equiv_oil'] = prod_trim.oil_prod + \
            prod_trim.gas_prod / fator_gas
        return prod_trim

    def write_file(self):
        Path("resultados/").mkdir(parents=True, exist_ok=True)
        output_name = 'resultados/' + \
            self._file_name[0] + '_AEPP' + self._file_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.prod_anual.to_excel(writer, sheet_name='Produção Anual')
        self.prod_trim.to_excel(writer, sheet_name='Produção Trimestral')
        writer.close()


class ProducaoTarefa01:

    def __init__(self, dados_trabalho='config/dados_trabalho.xlsx') -> None:
        self.modelo = 'Up'
        self._file_name = ['Tarefa01', '.xlsx']
        self.producao = pd.DataFrame()
        self.price = pd.read_excel(dados_trabalho,
                                   sheet_name='Stock_Oil_Price', index_col=0, parse_dates=['Ano'], usecols=['Ano'])
        self.price[self.modelo] = 70
        self._prod_tarefa_01_anual()
        self._prod_year_to_quarter()

    def _prod_oil_t1(self):
        oil = np.zeros(len(self.price))
        q0 = 85e3
        oil[:3] = 0
        rump = np.arange(3, 6)
        oil[3:6] = np.array([0.25*q0*(x + 1 - 3) for x in rump])
        oil[6:11] = q0
        decli = np.arange(11, 30)
        oil[11:] = np.array([q0*math.exp(-0.07*(x + 1 - 11)) for x in decli])
        return oil

    def sigmoid_injecao(self, t, qinj_plato=141800, qinj_abd=88700, k=0.5, ts=12):
        return qinj_plato - (qinj_plato - qinj_abd)/(1 + math.exp(-k*(t-ts)))

    def sigmoid_producao(self, t, qprod_abd=32360, k=0.5, ts=12):
        return qprod_abd/(1 + math.exp(-k*(t-ts)))

    def _inj_water_t1(self):
        water = np.zeros(len(self.price))
        qinj_plato = 141800
        water[:3] = 0
        rump = np.arange(3, 7)
        water[3:7] = np.array([0.25*qinj_plato*(x + 1 - 3) for x in rump])
        decli = np.arange(7, 30)
        water[7:] = np.array([self.sigmoid_injecao(x+1) for x in decli])
        return water

    def _prod_water_t1(self):
        water = np.zeros(len(self.price))
        water[:3] = 0
        decli = np.arange(3, 30)
        water[3:] = np.array([self.sigmoid_producao(x+1) for x in decli])
        return water

    def _quarter_index(self):
        start_date = self.price.index[0]
        end_date = date(self.price.index[-1].year, 12, 31)
        quarters = pd.date_range(pd.to_datetime(start_date),
                                 pd.to_datetime(end_date) + pd.offsets.QuarterBegin(1), freq='Q')
        return quarters

    def _year_index(self):
        date_prod = list()
        start_date = date(self.price.index[0].year, 12, 31)
        for i in range(len(self.price)):
            date_prod.append(start_date + relativedelta(years=i))
        return date_prod

    def _prod_year_to_quarter(self, fator_gas=1017.045686):
        self.prod_trim = self.prod_anual.loc[self.prod_anual.index.repeat(4)]
        self.prod_trim.index = self._quarter_index()
        self.prod_trim = self.prod_trim / (4 * 6.29 * 1000)
        self.prod_trim['equiv_oil'] = self.prod_trim.oil_prod + \
            self.prod_trim.gas_prod / fator_gas
        
    def _day_prod_to_anual(self, prod):
        if calendar.isleap(prod.name.year):
            prod = prod.mul(366)
        else:
            prod = prod.mul(365)
        return prod

    def _prod_tarefa_01_anual(self, RGO=100):
        self.prod_anual = pd.DataFrame(index=self._year_index())
        self.prod_anual.index = self.prod_anual.index.astype('datetime64[ns]')
        self.prod_anual.astype({})
        self.prod_anual['oil_prod'] = self._prod_oil_t1()
        self.prod_anual['water_prod'] = self._prod_water_t1()
        self.prod_anual['water_inj'] = self._inj_water_t1()
        self.prod_anual['gas_prod'] = RGO * self.prod_anual.oil_prod
        self.prod_anual = self.prod_anual.apply(lambda row: self._day_prod_to_anual(row), axis=1)
