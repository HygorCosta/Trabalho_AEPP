import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

class Cronograma:

    def __init__(self, dados_perfuracao) -> None:
        self.dados = pd.read_excel(dados_perfuracao)
        self.modelos = ['Base', 'Down', 'Up']

    def write_base(self):
        data_comercializacao = datetime.datetime(2024, 1, 1)
        data_fim = datetime.datetime(2054, 1, 1)
        month_increase = relativedelta(months=1)
        num_wells = self.dados['Seq'].iat[-1]
        for modelo in self.modelos:
            with open('cronogramas/Cronograma_' + modelo + '.inc', 'w') as f:
                i = 0
                data_base = data_comercializacao
                while data_fim >= data_base:
                    if i <= num_wells - 1:
                        data_open = self.dados['1º Óleo - ' + modelo][i].to_pydatetime()
                        if data_open < data_base:
                            f.write('DATE ' + data_open.strftime("%Y %m %d") + '\n')
                            f.write('OPEN ' + self.dados['Well'][i] + '\n')
                            i += 1
                    f.write('DATE ' + data_base.strftime("%Y %m %d") + '\n')
                    data_base += month_increase

                    