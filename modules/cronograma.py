import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

class Cronograma:

    def __init__(self, dados_perfuracao) -> None:
        self.dados = pd.read_excel(dados_perfuracao)
        self.modelos = {'Down': '01-01-2029', 'Base': '01-01-2028', 'Up': '01-01-2027'}

    def write_cronogramas(self):
        for modelo, data in self.modelos.items():
            data_abertura = datetime.datetime.strptime(data, '%d-%m-%Y')
            self.write_cronograma_abertura(modelo, data_abertura)

    def write_cronograma_abertura(self, modelo, ano_abertura):
        data_fim = datetime.datetime(2054, 1, 1)
        month_increase = relativedelta(months=1)
        num_wells = self.dados['Seq'].iat[-1]
        count = 0
        with open('cronogramas/Cronograma_' + modelo + '.inc', 'w') as f:
            data_atual = ano_abertura
            while data_atual <= data_fim:
                if data_atual.month % 2 != 0 and count <= num_wells - 1:
                    f.write('DATE ' + data_atual.strftime("%Y %m %d") + '\n')
                    f.write('OPEN ' + '\'' + self.dados['Well'][count] + '\''  + '\n')
                    count += 1
                else:
                    f.write('DATE ' + data_atual.strftime("%Y %m %d") + '\n')
                data_atual += month_increase


    def write_cronograma_perfuracao(self):
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

                    