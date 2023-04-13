import pandas as pd
from pathlib import Path

class Results:

    def __init__(self, projeto) -> None:
        self.projeto = projeto

    def _hub_financial(self):
        receita = self.projeto.receitas.rename('receita')
        despesas = self.projeto.despesas
        lucro_bruto = self.projeto.lucro_bruto().rename('lucro_bruto')
        deprec = self.projeto.depreciacao().rename('depreciacao')
        residual = self.projeto.valor_residual().rename('residual')
        lucro_trib = self.projeto.net_income_before_tax().rename('lucro_tributavel')
        ir = self.projeto.net_profit_tax().rename('ir_csll')
        lucro_liq = self.projeto.net_income_after_tax().rename('lucro_liquido')
        capex = self.projeto.capex().rename('capex_prod')
        flc = self.projeto.cash_flow().rename('cash_flow')
        flc_disc = self.projeto.discounted_cash_flow()
        data_frames = [receita, despesas, lucro_bruto, deprec, residual, lucro_trib, ir, lucro_liq, capex, flc, flc_disc] 
        return pd.concat(data_frames, join='outer', axis=1)
    
    def write_results(self):
        Path("out/").mkdir(parents=True, exist_ok=True)
        output_name = 'out/' + self.projeto.prod._file_name[0] + '_AEPP' + self.projeto.prod._file_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.projeto.prod.prod_anual.to_excel(writer, sheet_name='Prod_Anual')
        self.projeto.prod.prod_trim.to_excel(writer, sheet_name='Prod_Tri_PE')
        self.projeto.payment_loan_sac().to_excel(writer, sheet_name='Financiamento')
        self._hub_financial().to_excel(writer, sheet_name='Fluxo_Caixa')
        writer.close()
        print('Resultados gerados! Veja a pasta @out.')
