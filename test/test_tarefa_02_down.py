import pandas as pd
from modules.caixa import Caixa
from modules.results import Results
import pytest


def create_tarefa():
    projeto = Caixa(tarefa='2', dados_producao='producao/Pituba_Down_Mensal.xlsx', modelo='Down')
    return projeto


def test_producao_oil():
    producao = create_tarefa().prod.prod_anual
    assert pytest.approx(producao.iloc[0]) == 0
    assert pytest.approx(producao.oil_prod.iloc[5], 0.001) == 6580771.5
    assert pytest.approx(producao.oil_prod.iloc[6], 0.001) == 7657605.5
    assert pytest.approx(producao.oil_prod.iloc[-1], 0.001) == 6038289


def test_producao_gas():
    producao = create_tarefa().prod.prod_anual
    assert pytest.approx(producao.iloc[0]) == 0
    assert pytest.approx(producao.gas_prod.iloc[5], 0.001) == 515916928
    assert pytest.approx(producao.gas_prod.iloc[6], 0.001) == 666481088
    assert pytest.approx(producao.gas_prod.iloc[-1], 0.001) == 595929536


def test_producao_receita():
    producao = create_tarefa()
    result = Results(producao).write_results()
    assert pytest.approx(producao.iloc[0]) == 0
    assert pytest.approx(producao.iloc[5], 0.001) == 288_633_331.83
    assert pytest.approx(producao.iloc[6], 0.001) == 337_432_727.91
    assert pytest.approx(producao.iloc[-1], 0.001) == 267_747_489.98
