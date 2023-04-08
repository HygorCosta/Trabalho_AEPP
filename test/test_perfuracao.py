from perfuracao import Perfuracao
import pytest
import pandas as pd

def test_create_object():
    objeto = Perfuracao('dados_trabalho.xlsx')
    assert objeto is not None

def test_tempo_de_manobra():
    objeto = Perfuracao('dados_trabalho.xlsx')
    tempo_gerado = objeto._calcular_tempo_de_perfuracao()
    assert pytest.approx(tempo_gerado, 0.01) == 106

def test_custo_broca():
    objeto = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(objeto._custo_broca(), 0.01) == 440_000

def test_custo_poco_data_frame():
    perf = Perfuracao('dados_trabalho.xlsx')
    isinstance(perf.pocos.custo, pd.DataFrame)

def test_custo_poco_down_last():
    perf = Perfuracao('dados_trabalho.xlsx', modelo='Down')
    assert pytest.approx(perf.pocos.custo.loc[28], 0.01) ==  17_338_890.83

def test_custo_poco_down_first():
    perf = Perfuracao('dados_trabalho.xlsx', modelo='Down')
    assert pytest.approx(perf.pocos.custo.loc[0], 0.01) == 47_904_321.71 

def test_calcular_capex_pocos():
    perf = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(perf._calcular_capex_pocos(), 0.01) == 354_229_844.53  

def test_calcular_capex_subsea():
    perf = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(perf._calcular_capex_subsea(), 0.01) ==  1_276_787_136.76   

def test_calcular_capex_fpso():
    perf = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(perf._calcular_capex_fpso(), 0.01) == 722_059_523.70     

def test_calcular_capex_total():
    perf = Perfuracao('dados_trabalho.xlsx')
    assert pytest.approx(perf._capex_prod(), 0.01) == 3_683_612_167.73    

