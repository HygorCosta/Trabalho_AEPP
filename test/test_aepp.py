from modules.caixa import Caixa
from modules.aepp import AEPP
import pytest


def create_projeto():
    tarefa_01 = Caixa(tarefa="1", modelo="Up")
    return AEPP(tarefa_01)


def test_dispendios_presente():
    aepp = create_projeto()
    aepp._dispendios_presente()


def test__receitas_futuro():
    aepp = create_projeto()
    aepp._receitas_futuro()


def test_tgr():
    aepp = create_projeto()
    aepp.tgr()


def test_roi():
    aepp = create_projeto()
    aepp.roi()


def test_lu():
    aepp = create_projeto()
    aepp.lu()


def test_dispendios_presente():
    aepp = create_projeto()
    aepp._find_oil_price_vpl_null()


def test_dispendios_cup():
    aepp = create_projeto()
    aepp.cup()


def test_dispendios_cuo():
    aepp = create_projeto()
    aepp.cuo()


def test_dispendios_cui():
    aepp = create_projeto()
    aepp.cui()


def test_dispendios_cup_cuo_cui_cut():
    aepp = create_projeto()
    obtido = aepp.cuo() + aepp.cui() + aepp.cut()
    assert pytest.approx(aepp.cup()) == obtido


def test_dispendios_hub():
    aepp = create_projeto()
    aepp.hub_indicadores_economicos()
