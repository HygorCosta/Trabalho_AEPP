import pandas as pd
from pathlib import Path

class Results:

    def __init__(self, projeto) -> None:
        self.projeto = projeto

    def hub_financial(self):
        pass
    
    def write_results(self):
        Path("out/").mkdir(parents=True, exist_ok=True)
        output_name = 'out/' + self.prod._file_name[0] + '_AEPP' + self.prod._file_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.prod.prod_anual.to_excel(writer, sheet_name='Prod_Anual')
        self.prod.prod_trim.to_excel(writer, sheet_name='Prod_Trimestral_PE')
        self.payment_loan_sac().to_excel(writer, sheet_name='Financiamento')
        writer.close()
