from perfuracao import Perfuracao
import pytest

def test_create_object():
    objeto = Perfuracao('dados_perfuracao.xlsx', 1_000)
    assert objeto is not None

def test_tempo_de_manobra():
    objeto = Perfuracao('dados_perfuracao.xlsx', 1_000)
    tempo_gerado = objeto.tempo_de_manobra()
    assert pytest.approx(tempo_gerado, 0.1) == 81.64