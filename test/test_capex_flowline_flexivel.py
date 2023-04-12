from util.capex import FlowlineFlexivel
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'A')
    return FlowlineFlexivel(dutos.dados)

def test_capex_comp_total_flowline():
    flowline = create_opcao_a()
    comp = flowline._comp_total
    assert pytest.approx(comp) == 40

def test_capex_num_tramos_flowline():
    flowline = create_opcao_a()
    comp = flowline._num_tramos
    assert pytest.approx(comp) == 3

def test_custo_duto_flowline():
    flowline = create_opcao_a()
    comp = flowline._custo_duto()
    assert pytest.approx(comp) == (80 + 3)

def test_custo_plsv_flowline():
    flowline = create_opcao_a()
    comp = flowline._custo_plsv()
    assert pytest.approx(comp) == ((40/3+3+0.5+0.5+0.5)*10 + 2*(40/3+0.5+0.5+0.5))

def test_custo_pidf_flowline():
    flowline = create_opcao_a()
    comp = flowline._custo_pidf()
    assert pytest.approx(comp) == 40

def test_capex():
    flowline = create_opcao_a()
    comp = flowline.capex()
    assert pytest.approx(comp) == 40 + ((40/3+3+0.5+0.5+0.5)*10 + 2*(40/3+0.5+0.5+0.5)) + (80 + 3) + 20