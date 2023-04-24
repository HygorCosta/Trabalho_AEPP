import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from modules.caixa import Caixa

plt.rcParams["figure.figsize"] = [10, 6]
sns.set(style="darkgrid")


class PPlot:
    def __init__(self, projeto: Caixa) -> None:
        self.projeto = projeto
        self.df = projeto._hub_financial()

    def plot_cumulative_production(self):
        # TODO: Fix cumulative production
        fig, ax = plt.subplots()
        producao_acumulada = self.cumulative_production()
        axes = sns.lineplot(
            x="date",
            y="oil_prod_cum",
            data=producao_acumulada,
            hue="projeto",
            style="projeto",
            markers=True,
            ax=ax,
        )
        axes.set(xlabel="Anos", ylabel="Produção acumulada ($m^3$)")
        ax2 = plt.axes([0.6, 0.2, 0.3, 0.3], xlim=[2044, 2053], ylim=[4e8, 5.2e8])
        axes2 = sns.lineplot(
            x="date",
            y="oil_prod_cum",
            data=producao_acumulada,
            hue="projeto",
            style="projeto",
            markers=True,
            ax=ax2,
        )
        axes2.set_ylabel("")
        axes2.set_xlabel("")
        plt.legend([], [], frameon=False)
        axes2.set_title("zoom")
        axes2.set_xlim([2045, 2053])
        plt.tight_layout()
        plt.show()

    @property
    def receitas(self):
        return self.df.receita.rename("Receitas")

    @property
    def capex(self):
        return -self.df.capex_prod.rename("CAPEX")

    @property
    def dispendios(self):
        # OPEX + GT
        opex = self.df[["opex_var", "opex_fixo"]].sum(axis=1)
        gt = self.df.imposto + self.df.ir_csll
        return -(opex + gt).rename("OPEX + GT")

    @property
    def abex(self):
        # descomissionamento
        return -self.df.descom.rename("ABEX")

    @property
    def disc_cash_flow(self):
        return self.df.disc_cash_flow.rename("FCL (nominal)")

    def barplot_cash_flow(self):
        df = pd.concat(
            [self.receitas, self.capex, self.dispendios, self.abex],
            join="outer",
            axis=1,
        )
        fig, ax = plt.subplots()
        df.plot(kind="bar", stacked=True, ax=ax, alpha=.7)
        self.disc_cash_flow.plot(
            kind="line", ax=ax, use_index=False, color="black", lw=2
        )
        ax.set_xlabel("Anos")
        ax.set_ylabel("Valor Monetário - US$")
        plt.xticks(rotation=90)
        plt.legend()
        file_name = self.projeto.prod._file_name
        plt.savefig("out/" + file_name[0] + "_barplot_cash_flow.png")
