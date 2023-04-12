from modules.perfuracao import Perfuracao
import pytest
import pandas as pd

def create_object():
    objeto = Perfuracao(3, r'config/dados_trabalho.xlsx')
    return objeto

def test_tempo_de_manobra():
    objeto = create_object()
    tempo_gerado = objeto._tempo_de_manobra()
    assert pytest.approx(tempo_gerado) == 103.9650

def test_tempo_de_perfuracao():
    objeto = create_object()
    tempo_gerado = objeto._tempo_de_perfuracao()
    assert pytest.approx(tempo_gerado) == 105.9875

def test_custo_broca():
    objeto = create_object()
    assert pytest.approx(objeto._custo_broca()) == 440_000

def test_custo_poco_data_frame():
    perf = create_object()
    isinstance(perf.pocos.custo, pd.DataFrame)

def test_custo_poco():
    perf = create_object()
    assert pytest.approx(perf.pocos.custo.iloc[0]) == 48_322_962.34      
    assert pytest.approx(perf.pocos.custo.iloc[-1]) == 16_555_696.17       

