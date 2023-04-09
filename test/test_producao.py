from producao import Producao
import pytest

# def test_prod_trimestral_is_not_None():
#     df = PartipacaoEspecial('Produção_Pituba_Base_LS.xlsx', 'dados_gerais.xlsx')
#     df.write_file()
#     assert df.prod_trimestral is not None

def test_price():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'dados_trabalho.xlsx')
    assert df.price.iloc[0].values == 70
    assert df.price.iloc[1].values == 67
    assert df.price.iloc[2].values == 72

def test_prod_anual_oil():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.oil_prod.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.oil_prod.iloc[4]) ==  6_964_300.78 
    assert pytest.approx(df.prod_anual.oil_prod.iloc[-1]) ==  6_796_757.09  

def test_prod_anual_gas():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.gas_prod.iloc[4]) == 557_205_737.90 
    assert pytest.approx(df.prod_anual.gas_prod.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.gas_prod.iloc[-1]) == 664_689_353.40   

def test_prod_anual_water():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.water_prod.iloc[4]) == 0 
    assert pytest.approx(df.prod_anual.water_prod.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.water_prod.iloc[-1]) == 20_826_676.25  

def test_prod_anual_water_inj():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'dados_trabalho.xlsx')
    assert pytest.approx(df.prod_anual.water_inj.iloc[4]) == 961_013.59  
    assert pytest.approx(df.prod_anual.water_inj.iloc[0]) == 0
    assert pytest.approx(df.prod_anual.water_inj.iloc[-1]) ==  30_029_317.85   

