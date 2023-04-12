from util.capex import FlowlineRigido
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'B')
    return FlowlineRigido(dutos.dados)

def test_comp_total():
    flow = create_opcao_a()
    comp = flow._comp_total
    assert pytest.approx(comp) == 40

def test_custo_duto():
    flow = create_opcao_a()
    comp = flow.custo_duto()
    assert pytest.approx(comp) == 400

def test_custo_embarcacao():
    flow = create_opcao_a()
    comp = flow.custo_embarcacao()
    assert pytest.approx(comp) == (20 + 1)*(2 + 1) + 10

def test_custo_equipamentos():
    flow = create_opcao_a()
    comp = flow.custo_equipamentos()
    assert pytest.approx(comp) == (20 + 2*5 + 3 + 2)

def test_custo_pidf():
    flow = create_opcao_a()
    comp = flow.custo_pidf()
    assert pytest.approx(comp) == 40

def test_custo_capex():
    flow = create_opcao_a()
    comp = flow.capex()
    assert pytest.approx(comp) == 40 + (20 + 2*5 + 3 + 2) + (20 + 1)*(2 + 1) + 10 + 400