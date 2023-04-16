from modules.producao import Producao
import pytest

def test_price():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    assert df.price.iloc[0].values == 70
    assert df.price.iloc[1].values == 67
    assert df.price.iloc[2].values == 72

def test_prod_anual_oil():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.oil_prod.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.oil_prod.iloc[4]) ==  6_964_300.78 
    assert pytest.approx(df.prod_anual.oil_prod.iloc[-1]) ==  6_796_757.09  

def test_prod_anual_gas():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.gas_prod.iloc[4]) == 557_205_737.90 
    assert pytest.approx(df.prod_anual.gas_prod.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.gas_prod.iloc[-1]) == 664_689_353.40   

def test_prod_anual_water():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.water_prod.iloc[4]) == 0 
    assert pytest.approx(df.prod_anual.water_prod.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.water_prod.iloc[-1]) == 20_826_676.25  

def test_prod_anual_water_inj():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.water_inj.iloc[4]) == 961_013.59  
    assert pytest.approx(df.prod_anual.water_inj.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.water_inj.iloc[-1]) ==  30_029_317.85   

def test_prod_tarefa_01():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    prod = df._prod_oil_t1()
    assert pytest.approx(prod.iloc[-1]) == 22480.56721
    assert pytest.approx(prod.iloc[4]) == 42500

def test_water_prod_tarefa_01():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx')
    prod = df.prod_tarefa_01()
    assert pytest.approx(prod.iloc[-1]) == 32356.006952
    assert pytest.approx(prod.iloc[4]) == 948.54379

def test_prod_tarefa_01():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'config/dados_trabalho.xlsx', tarefa='1')
    prod = df._prod_year_to_quarter()
    assert prod.oil_prod.approx(prod.iloc[-1]) == 22480.56721
    assert prod.oil_prod.approx(prod.iloc[4]) == 42500