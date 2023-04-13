from modules.caixa import Caixa
import pytest

def create_obj():
    flow = Caixa(3, 'Base', 'config/dados_trabalho.xlsx', 'Produção_Pituba_Base_LS.xlsx')
    return flow

def test_calcular_receita():
    flow = create_obj()
    assert pytest.approx(flow.receitas.iloc[6]) == 1_106_403_312.53 
    assert pytest.approx(flow.receitas.iloc[4]) == 535_543_519.224
    assert pytest.approx(flow.receitas.iloc[0]) == 0
    assert pytest.approx(flow.receitas.iloc[-1]) == 525_528_033.123 

def test_calcular_despesas_opex_var():
    flow = create_obj().despesas
    assert pytest.approx(flow.opex_var.iloc[6]) == 81_126_557.93   
    assert pytest.approx(flow.opex_var.iloc[4]) == 23_910_139.69  
    assert pytest.approx(flow.opex_var.iloc[0]) == 0
    assert pytest.approx(flow.opex_var.iloc[-1]) == 123_408_732.97  

def test_calcular_aliquota_pe():
    flow = create_obj().prod.prod_trim
    assert pytest.approx(flow.aliquota.iloc[28]) == 0.1 
    assert pytest.approx(flow.aliquota.iloc[31]) == 0.2   

def test_calcular_redutor_pe():
    flow = create_obj().prod.prod_trim
    assert pytest.approx(flow.redutor.iloc[28]) == 450
    assert pytest.approx(flow.redutor.iloc[31]) == 675   

def test_calcular_despesas_descomissionamento():
    flow = create_obj().despesas
    assert pytest.approx(flow.descom.iloc[0]) == 0
    assert pytest.approx(flow.descom.iloc[-1]) == 771_738_362.20   

def test_capex_prod():
    flow = create_obj()
    assert pytest.approx(flow.capex_prod) == 3_858_691_811.02

def test_calcular_part_especial():
    flow = create_obj()
    flow.partipacao_especial()
    pe = flow.prod.prod_trim.part_esp
    assert pytest.approx(pe.iloc[28]) == 12_586_404.85  
    assert pytest.approx(pe.iloc[31]) == 26_859_785.78   

def test_imposto_producao():
    flow = create_obj()
    flow.partipacao_especial()
    imposto = flow.imposto_producao()
    assert pytest.approx(imposto.iloc[6]) == 212_982_637.66   
    assert pytest.approx(imposto.iloc[4]) == 103_092_127.45   
    assert pytest.approx(imposto.iloc[0]) == 0   
    assert pytest.approx(imposto.iloc[-1]) == 101_164_146.38   

def test_calcular_liquido_bruto():
    flow = create_obj()
    bruto = flow.lucro_bruto()
    assert pytest.approx(bruto.iloc[6]) == 715_826_821.67 
    assert pytest.approx(bruto.iloc[4]) == 312_073_956.81
    assert pytest.approx(bruto.iloc[0]) == 0
    assert pytest.approx(bruto.iloc[-1]) == -567_250_503.70  

def test_calcular_liquido_tributavel():
    flow = create_obj()
    ltri = flow.net_income_before_tax()
    assert pytest.approx(ltri.iloc[6]) == 600_066_067.34 
    assert pytest.approx(ltri.iloc[4]) == 196_313_202.48 
    assert pytest.approx(ltri.iloc[0]) == 0
    assert pytest.approx(ltri.iloc[-1]) == -567_250_503.70  

def test_calcular_imposto_lucro_liquido_tributavel():
    flow = create_obj()
    ltri = flow.net_profit_tax()
    assert pytest.approx(ltri.iloc[4]) == 66_746_488.84  
    assert pytest.approx(ltri.iloc[0]) == 0  
    assert pytest.approx(ltri.iloc[-1]) == 0 
    assert pytest.approx(ltri.iloc[-2]) == 78_027_319.76

def test_calcular_parcelas_sac():
    flow = create_obj()
    parcela = flow.payment_loan_sac()['Pagamento']
    assert pytest.approx(parcela.iloc[0]) == 363_643_116.27  
    assert pytest.approx(parcela.iloc[1]) == 353_178_344.08  
    assert pytest.approx(parcela.iloc[-1]) == 0 

def test_calcular_capex():
    flow = create_obj()
    parcela = flow.capex()
    assert pytest.approx(parcela.iloc[1]) == 353_178_344.08    
    assert pytest.approx(parcela.iloc[6]) == 300_854_483.12    
    assert pytest.approx(parcela.iloc[19]) == 164_812_444.63    

def test_flow_cash():
    flow = create_obj()
    parcela = flow.cash_flow()
    assert pytest.approx(parcela.iloc[6]) == 210_949_875.65   
    assert pytest.approx(parcela.iloc[4]) == -76_456_559.54   
    assert pytest.approx(parcela.iloc[1]) == -353_178_344.08   
    assert pytest.approx(parcela.iloc[-1]) == -567_250_503.70    

def test_calcular_discounted_cash_flow():
    flow = create_obj()
    parcela = flow.discounted_cash_flow()
    assert pytest.approx(parcela.iloc[6]) == 108_250_641.23  
    assert pytest.approx(parcela.iloc[4]) == -47_473_508.10   
    assert pytest.approx(parcela.iloc[1]) == -291_882_928.99   
    assert pytest.approx(parcela.iloc[0]) == -1_102_323_013.36    
    assert pytest.approx(parcela.iloc[-1]) == -32_508_305.73 
    assert pytest.approx(parcela.iloc[-2]) == 9_548_251.24  

def test_npv():
    flow = create_obj()
    parcela = flow.vpl()
    assert pytest.approx(parcela) == 892_060_950.03

def test_tgr():
    flow = create_obj()
    parcela = flow.tgr()
    assert pytest.approx(parcela) == 0.1101712