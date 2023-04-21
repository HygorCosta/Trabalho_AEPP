import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
plt.rcParams["figure.figsize"] = [10, 6]
sns.set( style = "darkgrid" )  

class PPlot:
    def __init__(self, lista_projetos: list, names: list) -> None:
        self.lista_projetos = lista_projetos
        self.names = names

    def cumulative_production(self):
        producao = [proj.prod.prod_anual for proj in self.lista_projetos]
        for project, name in zip(producao, self.names):
            project['oil_prod_cum'] = project['oil_prod'].cumsum()
            project['projeto'] = name
        pp = pd.concat(producao)
        pp['date'] = np.tile(np.arange(2024, 2054), len(self.names)) 
        return pp

    def plot_cumulative_production(self):
        fig, ax = plt.subplots()
        producao_acumulada = self.cumulative_production()
        axes = sns.lineplot(x='date', y='oil_prod_cum', data=producao_acumulada, hue='projeto', style='projeto', markers=True, ax=ax)
        axes.set(xlabel='Anos', ylabel='Produção acumulada ($m^3$)')
        ax2 = plt.axes([.6, .2, .3, .3], xlim=[2044, 2053], ylim=[4e8, 5.2e8])
        axes2 = sns.lineplot(x='date', y='oil_prod_cum', data=producao_acumulada, hue='projeto', style='projeto', markers=True, ax=ax2)
        axes2.set_ylabel('')
        axes2.set_xlabel('')
        plt.legend([], [], frameon=False)
        axes2.set_title('zoom')
        axes2.set_xlim([2045, 2053])
        plt.tight_layout()
        plt.show()

        

    def net_cash_split(self):
        pass

    def net_cash_flows(self):
        pass

    def npv_sensitivity(self):
        pass

    def npv_profile(self):
        pass
