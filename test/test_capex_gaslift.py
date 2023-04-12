from util.capex import GasLift
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'A')
    return GasLift(dutos.dados)

def test_capex_comp_total_gaslift():
    gaslift = create_opcao_a()
    comp = gaslift._comp_total
    assert pytest.approx(comp) == 45

def test_capex_num_tramos_gaslift():
    gaslift = create_opcao_a()
    comp = gaslift._num_tramos
    assert pytest.approx(comp) == 4

def test_custo_duto_gaslift():
    gaslift = create_opcao_a()
    comp = gaslift._custo_duto()
    assert pytest.approx(comp) == (90 + 2*4 + 10)

def test_custo_plsv_gaslift():
    gaslift = create_opcao_a()
    comp = gaslift._custo_plsv()
    assert pytest.approx(comp) == ((10+3+0.5+18/24+0.5)*10 + 2*(10+0.5+18/24+0.5))

def test_custo_pidf_gaslift():
    gaslift = create_opcao_a()
    comp = gaslift._custo_pidf()
    assert pytest.approx(comp) == 50

def test_capex():
    gaslift = create_opcao_a()
    comp = gaslift.capex()
    assert pytest.approx(comp) == 50 + ((10+3+0.5+18/24+0.5)*10 + 2*(10+0.5+18/24+0.5)) + (90 + 2*4 + 10)