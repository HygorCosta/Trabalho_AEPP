from modules.caixa import Caixa
from modules.aepp import AEPP
import pytest

def create_projeto():
    tarefa_01 = Caixa(tarefa='1', modelo='Up')
    return AEPP(tarefa_01)

def test_dispendios_presente():
    aepp = create_projeto()
    aepp._dispendios_presente()

def test_dispendios_presente():
    aepp = create_projeto()
    aepp._receitas_futuro()

def test_dispendios_presente():
    aepp = create_projeto()
    aepp.tgr()

def test_dispendios_presente():
    aepp = create_projeto()
    aepp.roi()

def test_dispendios_presente():
    aepp = create_projeto()
    aepp.lu()