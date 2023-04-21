import pandas as pd
from modules.caixa import Caixa
import cProfile
import pstats


if __name__ == '__main__':
    with cProfile.Profile() as profile:
        # Tarefas 02 - Down:
        tarefa_02_down = Caixa(
        tarefa='2', dados_producao='producao/Pituba_Down_Mensal.xlsx', modelo='Down')
        tarefa_02_down()
