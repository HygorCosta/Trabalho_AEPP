# -*- coding: utf-8 -*-
import pandas as pd
from modules.caixa import Caixa
from modules.results import Results
from modules.aepp import AEPP
from modules.plot import PPlot


def create_obj():
    tarefa_01 = Caixa(tarefa="1", modelo="Up")
    # Tarefas 02 - Down:
    tarefa_02_down = Caixa(
        tarefa="2", dados_producao="producao/Pituba_Down_Mensal.xlsx", modelo="Down"
    )
    # Tarefas 02 - Base:
    tarefa_02_base = Caixa(
        tarefa="2", dados_producao="producao/Pituba_Base_Mensal.xlsx"
    )
    # Tarefa 03:
    tarefa_03 = Caixa(tarefa="3", dados_producao="producao/Pituba_Base_LS.xlsx")
    # Tarefa 04 - Flexivel:
    tarefa_04_flex = Caixa(tarefa="4A", dados_producao="producao/Producao_P16F.xlsx")
    # Tarefa 04 - Rigido:
    tarefa_04_rigido = Caixa(tarefa="4B", dados_producao="producao/Producao_P16R.xlsx")
    # Tarefas 02 - Up:
    tarefa_02_up = Caixa(
        tarefa="2", dados_producao="producao/Pituba_Up_Mensal.xlsx", modelo="Up"
    )
    lista_projetos = [
        tarefa_02_down,
        tarefa_02_base,
        tarefa_02_up,
        tarefa_03,
        tarefa_04_flex,
        tarefa_04_rigido,
    ]
    nome_projetos = [
        "tarefa_02_down",
        "tarefa_02_base",
        "tarefa_02_up",
        "tarefa_03",
        "tarefa_04_flex",
        "tarefa_04_rigido",
    ]
    return PPlot(lista_projetos, names=nome_projetos)


def test_cumulative_production():
    projeto = create_obj()
    projeto.plot_cumulative_production()


def test_barplot_cash_flow():
    projeto = Caixa(tarefa="1", modelo="Up")
    pplot = PPlot(projeto)
    pplot.barplot_cash_flow()