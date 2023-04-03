import os
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Producao:

    def __init__(self, producao_excel, dados) -> None:
        self._split_name = os.path.splitext(producao_excel)
        self.df = self.configurar_producao(producao_excel)
        self.price = pd.read_excel(dados, sheet_name='Stock_Oil_Price', index_col=0)
        self.datas = self.df['Data']
        self.prod_trimestral = self.producao_trimestral()
        self.calcular_receita_trimestral()

    def configurar_producao(self, producao_excel):
        prod = pd.read_excel(producao_excel, skiprows = range(0, 2))
        prod.columns = ['Tempo (dias)', 'Data', 'Oil-PROD - Trimestral (Mm3)', 'Water-PROD - Trimestral (Mm3)', 'Gas-PROD - Trimestral (Mm3)', 'Water-INJ - Trimestral (Mm3)']
        prod['Data'] = pd.to_datetime(prod['Data'])
        return prod

    def agrupar_trimestral(self, coluna):
        return self.df.groupby(self.df['Data'].dt.to_period('Q'))[coluna].sum()/1000
    
    def shift_values(self):
        self.df = self.df.shift(-1)
        self.df['Data'] = self.datas
        self.df.fillna(0)
    
    def producao_trimestral(self):
        prod_tri = pd.DataFrame()
        self.shift_values()
        for col in self.df.columns[2:]: 
            prod_tri[col] = self.agrupar_trimestral(col)
        prod_tri['Óleo_Equiv_(Mm3)'] = prod_tri['Oil-PROD - Trimestral (Mm3)'] + prod_tri['Gas-PROD - Trimestral (Mm3)'] / 1017.5321
        return prod_tri
    
    def calcular_receita_trimestral(self):
        prod_oleo = self.prod_trimestral['Oil-PROD - Trimestral (Mm3)']
        prod_gas = self.prod_trimestral['Gas-PROD - Trimestral (Mm3)']
        price = self.price['Base'].repeat(4).reset_index()
        price = price.drop(price.tail(3).index)
        price = price.set_index(prod_oleo.index)
        self.prod_trimestral['Receita']  = price['Base']*6.29*1_000*prod_oleo + (4*37.31/1000)*prod_gas

    def write_file(self):
        output_name = self._split_name[0] + '_Trimestral' + self._split_name[1]
        self.prod_trimestral.to_excel(output_name)