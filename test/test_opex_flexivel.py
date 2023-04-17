from util.opex import OpexFlexivel
from modules.dutos import Dutos
import pytest

def create_opcao_a():
    dutos = Dutos('config/config_tarefa_4_test.yaml', 'A')
    return OpexFlexivel(dutos.dados)

def test_pidf3():
    opex = create_opcao_a()
    assert pytest.approx(opex._pidf3()) == 40

def test_pidf2():
    opex = create_opcao_a()
    assert pytest.approx(opex._pidf2()) == 80

def test_pidf1():
    opex = create_opcao_a()
    assert pytest.approx(opex._pidf1()) == 100

def test_inspecao_dutos():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_inspecao_dutos()) == 100 + 80 + 40

def test_inspecao_equipamentos():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_inspecao_equip()) == 4

def test_intervencao():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex_intervencao()) == 8 + 5

def test_opex():
    opex = create_opcao_a()
    assert pytest.approx(opex.opex()) == 13 + 4 + 220