import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from modules.caixa import Caixa
from modules.results import Results
from modules.aepp import AEPP

sns.set_theme(style="darkgrid")

# Tarefas 02 - Down:
tarefa_02_down = Caixa(
    tarefa='2', dados_producao='producao/Pituba_Down_Mensal.xlsx', modelo='Down')
# Tarefas 02 - Base:
tarefa_02_base = Caixa(
    tarefa='2', dados_producao='producao/Pituba_Base_Mensal.xlsx')
# Tarefas 02 - Up:
tarefa_02_up = Caixa(
    tarefa='2', dados_producao='producao/Pituba_Up_Mensal.xlsx',
    modelo='Up')

tma = np.arange(0, .3, 0.02)
vpls_down = [tarefa_02_down(tma=rate) for rate in tma]
vpls_base = [tarefa_02_base(tma=rate) for rate in tma]
vpls_up = [tarefa_02_up(tma=rate) for rate in tma]

df = pd.DataFrame({
    'vpls_down': vpls_down,
    'vpls_base': vpls_base,
    'vpls_up': vpls_up,
    'tma': tma
})

df = pd.melt(df, id_vars=['tma'], value_vars=['vpls_down', 'vpls_base', 'vpls_up'])

ax = sns.lineplot(x = 'tma', y = 'value', data=df)
sns.scatterplot(x = 'tma', y = 'value', data=df, hue='variable')
ax.set(ylabel=r'NPV (\$)')

