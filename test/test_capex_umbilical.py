from util.capex import Umbilical
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'A')
    return Umbilical(dutos.dados)

def test_capex_comp_total_umbilical():
    umbilical = create_opcao_a()
    comp = umbilical._comp_total
    assert pytest.approx(comp) == 45

def test_capex_num_tramos_umbilical():
    umbilical = create_opcao_a()
    comp = umbilical._num_tramos
    assert pytest.approx(comp) == 4

def test_custo_duto_umbilical():
    umbilical = create_opcao_a()
    comp = umbilical._custo_duto()
    assert pytest.approx(comp) == (45 + 2*4 + 10)

def test_custo_plsv_umbilical():
    umbilical = create_opcao_a()
    comp = umbilical._custo_plsv()
    assert pytest.approx(comp) == ((10+3+0.5+18/24+0.5)*10 + 2*(10+0.5+18/24+0.5))

def test_custo_pidf_umbilical():
    umbilical = create_opcao_a()
    comp = umbilical._custo_pidf()
    assert pytest.approx(comp) == 50

def test_capex():
    umbilical = create_opcao_a()
    comp = umbilical.capex()
    assert pytest.approx(comp) == 50 + ((10+3+0.5+18/24+0.5)*10 + 2*(10+0.5+18/24+0.5)) + (45 + 2*4 + 10)
