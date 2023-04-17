import pandas as pd
from modules.caixa import Caixa
from modules.results import Results
import pytest


def create_tarefa():
    projeto = Caixa(tarefa='2', dados_producao='producao/Pituba_Up_Mensal.xlsx', modelo='Up')
    return projeto

def test_receita_trimestral():
    projeto = create_tarefa()
    projeto.prod.prod_trim
