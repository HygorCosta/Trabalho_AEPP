# -*- coding: utf-8 -*-
import pandas as pd
from modules.caixa import Caixa
from modules.results import Results

# Tarefas:
# 2, 3, 4A e 4B (str)
projeto = Caixa(tarefa='4A', modelo='Base', dados_trabalho='config/dados_trabalho.xlsx', dados_producao='Produção_Pituba_Base_P16.xlsx')
resultados = Results(projeto)
resultados.write_results()