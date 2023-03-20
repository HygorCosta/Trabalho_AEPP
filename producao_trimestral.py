import numpy as np
import pandas as pd
from datetime import datetime

class Producao:

    def __init__(self, producao_excel) -> None:
        self.df = pd.read_excel(producao_excel, skiprows = range(0, 2))
        self.df.columns = ['Tempo (dias)', 'Data', 'Oil-PROD - Trimestral (Mm3)', 'Water-PROD - Trimestral (Mm3)', 'Gas-PROD - Trimestral (Mm3)', 'Water-INJ - Trimestral (Mm3)']
        self.df['Data'] = pd.to_datetime(self.df['Data'])

    def producao_trimestral(self, coluna):
        return self.df.groupby(self.df['Data'].dt.to_period('Q'))[coluna].sum()/1000

    def write_file(self):
        df_trimestral = pd.DataFrame()
        for col in self.df.columns[2:]:
            df_trimestral[col] = self.producao_trimestral(col)
        df_trimestral.to_excel("Producao_Trimestral.xlsx")


#################################
if __name__ == '__main__':
    prod = Producao('Pituba_Up_Mensal.xlsx')
    prod.write_file()