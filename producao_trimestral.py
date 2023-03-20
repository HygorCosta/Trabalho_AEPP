import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Producao:

    def __init__(self, producao_excel) -> None:
        self.df = pd.read_excel(producao_excel, skiprows = range(0, 2))
        self.df.columns = ['Tempo (dias)', 'Data', 'Oil-PROD - Trimestral (Mm3)', 'Water-PROD - Trimestral (Mm3)', 'Gas-PROD - Trimestral (Mm3)', 'Water-INJ - Trimestral (Mm3)']
        self.df['Data'] = pd.to_datetime(self.df['Data'])
        self.datas = self.df['Data']

    def producao_trimestral(self, coluna):
        return self.df.groupby(self.df['Data'].dt.to_period('Q'))[coluna].sum()/1000

    def shift_values(self):
        self.df = self.df.shift(-1)
        self.df['Data'] = self.datas
        self.df.fillna(0)

    def write_file(self):
        df_trimestral = pd.DataFrame()
        self.shift_values()
        for col in self.df.columns[2:]: 
            df_trimestral[col] = self.producao_trimestral(col)
        df_trimestral.to_excel("Producao_Trimestral.xlsx")


#################################
if __name__ == '__main__':
    prod = Producao('Pituba_Down_Mensal.xlsx')
    prod.write_file()