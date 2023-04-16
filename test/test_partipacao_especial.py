from modules.partipacao_especial import PartipacaoEspecial
from modules.caixa import Caixa
import pytest


def create_part_esp():
    caixa = Caixa('1', modelo='Up')
    return caixa.part_esp


def test_receitas():
    rec = create_part_esp().receita_bruta
    assert pytest.approx(rec.iloc[0]) == 0
    assert pytest.approx(rec.iloc[3*4]) == 561_340_405.40541  / 4
    assert pytest.approx(rec.iloc[4*4]) == 1_125_756_648.64865  / 4 
    assert pytest.approx(rec.iloc[6*4]) == 2_245_361_621.62162  / 4  
    assert pytest.approx(rec.iloc[7*4]) == 2_245_361_621.62162  / 4  
    assert pytest.approx(rec.iloc[-1]) ==  593_847_092.31422  / 4 


def test_data_lanc():
    rec = create_part_esp().total_cost()
    assert pytest.approx(rec.imposto.iloc[11]) == 0
    assert pytest.approx(rec.imposto.iloc[12]) != 0
    assert pytest.approx(rec.descom.iloc[-5]) == 0
    assert pytest.approx(rec.descom.iloc[-4]) != 0
    