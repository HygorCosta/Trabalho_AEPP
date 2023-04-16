# -*- coding: utf-8 -*-
import pandas as pd
from modules.caixa import Caixa
from modules.results import Results

# Tarefas 01:
tarefa_01 = Caixa(tarefa='1', modelo='Up')

# Tarefas 02:
tarefa_02_down = Caixa(tarefa='2', dados_producao='producao/Pituba_Down_Mensal.xlsx')
tarefa_02_base = Caixa(tarefa='2', dados_producao='producao/Pituba_Base_Mensal.xlsx')
tarefa_02_up = Caixa(tarefa='2', dados_producao='producao/Pituba_Up_Mensal.xlsx')

# TODO: Add: calcular o VPL médio dos três casos da tarefa 02

# Tarefa 03:
tarefa_03 = Caixa(tarefa='3', dados_producao='producao/Pituba_Base_LS.xlsx')

# Tarefa 04:
# TODO - Add: incluir os dois cenários (A e B)