from util.capex import Riser
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'A')
    return Riser(dutos.dados)

def test_capex_comp_total_riser():
    riser = create_opcao_a()
    comp = riser._comp_total_riser
    assert pytest.approx(comp) == 30

def test_capex_num_tramos_riser():
    riser = create_opcao_a()
    comp = riser._num_tramos_riser
    assert pytest.approx(comp) == 3

def test_custo_duto_riser():
    riser = create_opcao_a()
    comp = riser._custo_duto()
    assert pytest.approx(comp) == (60 + 6 + 10)

def test_custo_plsv_riser():
    riser = create_opcao_a()
    comp = riser._custo_plsv()
    assert pytest.approx(comp) == ((10+3+0.5+0.5+0.5+40/24)*10 + 2*(10+0.5+0.5+40/24+0.5))

def test_custo_pidf_riser():
    riser = create_opcao_a()
    comp = riser._custo_pidf()
    assert pytest.approx(comp) == 20

def test_capex():
    riser = create_opcao_a()
    comp = riser.capex()
    assert pytest.approx(comp) == 20 + ((10+3+0.5+0.5+0.5+40/24)*10 + 2*(10+0.5+0.5+40/24+0.5)) + (60 + 6 + 10)