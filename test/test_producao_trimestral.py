from producao_trimestral import Producao

def test_prod_trimestral_is_not_None():
    df = Producao('Produção_Pituba_Base_LS.xlsx', 'dados_gerais.xlsx')
    df.write_file()
    assert df.prod_trimestral is not None