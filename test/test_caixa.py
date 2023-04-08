from caixa import Caixa
import pandas as pd
import pytest

def create_obj():
    flow = Caixa(3, 'Base', 'dados_trabalho.xlsx', 'Produção_Pituba_Base_LS.xlsx')
    return flow

def test_create():
    flow = create_obj()
    assert flow is not None

def test_calcular_receita():
    flow = create_obj()
    receita = flow.receitas.iloc[4]
    assert pytest.approx(receita, 0.005) ==  535_544_292.04 

# def test_aliquota_partipacao_especial():
#     flow = create_obj()
#     aliquota = flow._aliquota_partipacao_especial().iloc[28]
#     assert pytest.approx(aliquota, 0.001) ==  0.1

def test_pe_redutor():
    flow = create_obj()
    flow._aliquota_partipacao_especial()
    flow._pe_redutor()
    redutor = flow.prod.prod_trim.redutor.iloc[28]
    assert pytest.approx(redutor, 0.001) ==  450

def test_calcular_part_especial():
    flow = create_obj()
    flow._calcular_part_especial()
    pe = flow.prod.prod_trim.part_esp.iloc[28]
    assert pytest.approx(pe, 0.001) ==  12_586_766.00 

def test_imposto_producao():
    flow = create_obj()
    flow._calcular_part_especial()
    imposto = flow._calcular_imposto_producao().iloc[4]
    assert pytest.approx(imposto, 0.001) == 103_092_276.22  