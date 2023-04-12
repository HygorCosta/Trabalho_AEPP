from util.opex import OpexRigido
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'A')
    return OpexRigido(dutos.dados)

def test_custo_pidr():
    opex = create_opcao_a()
    assert pytest.approx(opex.custo_pidr()) == 2

def test_custo_insp_interna():
    opex = create_opcao_a()
    assert pytest.approx(opex.custo_insp_interna()) == 4

def test_opex_inspecao_dutos():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_inspecao_dutos()) == 6

def test_opex_inspecao_equipamentos():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_inspecao_equipamentos()) == 2 + 2

def test_intervencao():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_intervencao()) == 4 + 5

def test_opex_inibidores():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_inibidores()) == 6 * 365 * 2

def test_opex():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex()) == (6*365*2 + 9 + 6 + 4)  