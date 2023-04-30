# -*- coding: utf-8 -*-
import pandas as pd
from modules.caixa import Caixa
from modules.results import Results
from modules.aepp import AEPP
from modules.plot import PPlot

# # Tarefas 01:
# tarefa_01 = Caixa(tarefa='1', modelo='Up')

# # Tarefas 02 - Down:
# tarefa_02_down = Caixa(
#     tarefa='2', dados_producao='producao/Pituba_Down_Mensal.xlsx', modelo='Down')

# # Tarefas 02 - Base:
# tarefa_02_base = Caixa(
#     tarefa='2', dados_producao='producao/Pituba_Base_Mensal.xlsx')

# # Tarefas 02 - Up:
# tarefa_02_up = Caixa(
#     tarefa='2', dados_producao='producao/Pituba_Up_Mensal.xlsx',
#     modelo='Up')

# vpl_proj_t2 = (tarefa_02_down.vpl() +
#                tarefa_02_base.vpl() + tarefa_02_up.vpl()) / 3

# # print(f'O VPL ponderado da tarefa 02 é de {vpl_proj_t2}.')

# # Tarefa 03:
# tarefa_03 = Caixa(tarefa='3', dados_producao='producao/Pituba_Base_LS.xlsx')

# # Tarefa 04 - Flexivel:
# tarefa_04_flex = Caixa(
#     tarefa='4A', dados_producao='producao/Producao_P16F.xlsx')

# Tarefa 04 - Flexivel:
tarefa_04_flex_inter = Caixa(
    tarefa='4A', dados_producao='producao/Producao_P16F_Interv.xlsx')

# Tarefa 04 - Rigido:
tarefa_04_rigido = Caixa(
    tarefa='4B', dados_producao='producao/Producao_P16R.xlsx')

# Tarefa 04 - Rigido:
tarefa_04_rigido_inter = Caixa(
    tarefa='4B', dados_producao='producao/Producao_P16R_Interv.xlsx')

# Gerar planilha com descritivo dos resultados
tarefas = [tarefa_01, tarefa_02_down, tarefa_02_base,
           tarefa_02_up, tarefa_03, tarefa_04_flex, tarefa_04_flex_inter, tarefa_04_rigido, tarefa_04_rigido_inter]
for tarefa in tarefas:
    parametros = AEPP(tarefa).hub_indicadores_economicos()
    Results(tarefa, parametros).write_results()
    # PPlot(tarefa).barplot_cash_flow()
