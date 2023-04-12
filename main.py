# -*- coding: utf-8 -*-
import pandas as pd
from modules.caixa import Caixa

projeto = Caixa(tarefa=2, modelo='Base', dados_trabalho='config/dados_trabalho.xlsx', dados_producao='Produção_Pituba_Base_P16.xlsx')
print(projeto)