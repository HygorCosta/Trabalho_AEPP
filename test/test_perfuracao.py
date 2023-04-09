from perfuracao import Perfuracao
import pytest
import pandas as pd

def test_create_object():
    objeto = Perfuracao('dados_trabalho.xlsx')
    assert objeto is not None

def test_tempo_de_manobra():
    objeto = Perfuracao('dados_trabalho.xlsx')
    tempo_gerado = objeto._tempo_de_manobra()
    assert pytest.approx(tempo_gerado) == 103.9650

def test_tempo_de_perfuracao():
    objeto = Perfuracao('dados_trabalho.xlsx')
    tempo_gerado = objeto._tempo_de_perfuracao()
    assert pytest.approx(tempo_gerado) == 105.9875

def test_custo_broca():
    objeto = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(objeto._custo_broca()) == 440_000

def test_custo_poco_data_frame():
    perf = Perfuracao('dados_trabalho.xlsx')
    isinstance(perf.pocos.custo, pd.DataFrame)

def test_custo_poco():
    perf = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(perf.pocos.custo.iloc[0]) == 48_322_962.34      
    assert pytest.approx(perf.pocos.custo.iloc[-1]) == 16_555_696.17       

