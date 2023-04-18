import pandas as pd
from pathlib import Path
from xlsxwriter.utility import xl_rowcol_to_cell

class Results:

    def __init__(self, projeto) -> None:
        self.projeto = projeto
        self.hub = self._hub_financial()
        self.financiamento = self.projeto.payment_loan_price()
        if self.projeto.tarefa in ('4A', '4B'):
            self.hub_p16 = projeto.dutos.hub_opex


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
    
    def _set_spreadsheet_format_prod_trimestral(self, writer):
        workbook = writer.book
        worksheet = writer.sheets['Prod_Tri_PE']
        worksheet.set_zoom(90)
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        vol_fmt = workbook.add_format({'num_format': '0.0E+00'})
        numb_fmt = workbook.add_format({'num_format': '#,##0'})
        percent_fmt = workbook.add_format({'num_format': '#,#0%'})
        # Account info columns
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:F', 10, numb_fmt)
        worksheet.set_column('G:G', 12, numb_fmt)
        worksheet.set_column('H:H', 10, percent_fmt)
        worksheet.set_column('I:I', 10, numb_fmt)
        worksheet.set_column('J:J', 12, money_fmt)
        # Total formatting
        total_fmt = workbook.add_format({'align': 'right', 'num_format': '##0,00E+00', 'bold': True, 'bottom':6})
        number_rows = len(self.projeto.prod.prod_trim)
        for column in range(1, 10):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(number_rows+1, column)
            # Get the range to use for the sum formula
            start_range = xl_rowcol_to_cell(1, column)
            end_range = xl_rowcol_to_cell(number_rows, column)
            # Construct and write the formula
            formula = "=SUM({:s}:{:s})".format(start_range, end_range)
            worksheet.write_formula(cell_location, formula, total_fmt)
        # Add a total label
        worksheet.write_string(number_rows+1, 0, "Total",total_fmt)
        # Define our range for the color formatting
        color_range = "G2:G{}".format(number_rows+1)
        # Add a format. Light red fill with dark red text.
        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})
        # Add a format. Green fill with dark green text.
        format2 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})
        # Highlight the top 5 values in Green
        worksheet.conditional_format(color_range, {'type': 'top',
                                                'value': '5',
                                                'format': format2})

        # Highlight the bottom 5 values in Red
        worksheet.conditional_format(color_range, {'type': 'bottom',
                                                'value': '5',
                                                'format': format1})
    
    def _set_spreadsheet_format_prod_anual(self, writer):
        workbook = writer.book
        worksheet = writer.sheets['Prod_Anual']
        worksheet.set_zoom(90)
        vol_fmt = workbook.add_format({'num_format': '0,0E+00'})
        numb_fmt = workbook.add_format({'num_format': '#,##0'})
        # Account info columns
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:E', 10, vol_fmt)
        number_rows = len(self.projeto.prod.prod_anual)
        # Total formatting
        total_fmt = workbook.add_format({'align': 'right', 'num_format': '##0,00E+00', 'bold': True, 'bottom':6})
        for column in range(1, 5):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(number_rows+1, column)
            # Get the range to use for the sum formula
            start_range = xl_rowcol_to_cell(1, column)
            end_range = xl_rowcol_to_cell(number_rows, column)
            # Construct and write the formula
            formula = "=SUM({:s}:{:s})".format(start_range, end_range)
            worksheet.write_formula(cell_location, formula, total_fmt)
        # Add a total label
        worksheet.write_string(number_rows+1, 0, "Total",total_fmt) 

    def _set_spreadsheet_format_financ(self, writer):
        workbook = writer.book
        worksheet = writer.sheets['Financiamento']
        worksheet.set_zoom(90)
        vol_fmt = workbook.add_format({'num_format': '0,0E+00'})
        numb_fmt = workbook.add_format({'num_format': '#,##0'})
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        # Account info columns
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:E', 14, money_fmt)
        number_rows = len(self.financiamento)
        # Total formatting
        total_fmt = workbook.add_format({'align': 'right', 'num_format': '##0,00E+00', 'bold': True, 'bottom':6})
        for column in range(2, 5):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(number_rows+1, column)
            # Get the range to use for the sum formula
            start_range = xl_rowcol_to_cell(1, column)
            end_range = xl_rowcol_to_cell(number_rows, column)
            # Construct and write the formula
            formula = "=SUM({:s}:{:s})".format(start_range, end_range)
            worksheet.write_formula(cell_location, formula, total_fmt)
        # Add a total label
        worksheet.write_string(number_rows+1, 1, "Total",total_fmt) 

    def _set_spreadsheet_format_fluxo_caixa(self, writer):
        workbook = writer.book
        worksheet = writer.sheets['Fluxo_Caixa']
        worksheet.set_zoom(90)
        vol_fmt = workbook.add_format({'num_format': '0,0E+00'})
        numb_fmt = workbook.add_format({'num_format': '#,##0'})
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        # Account info columns
        number_rows, number_cols = self.hub.shape
        worksheet.set_column('A:A', 20)
        worksheet.set_column(2, number_cols+1, 14, money_fmt)
        # Total formatting
        total_fmt = workbook.add_format({'align': 'right', 'num_format': '##0,00E+00', 'bold': True, 'bottom':6})
        for column in range(1, number_cols+1):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(number_rows+1, column)
            # Get the range to use for the sum formula
            start_range = xl_rowcol_to_cell(1, column)
            end_range = xl_rowcol_to_cell(number_rows, column)
            # Construct and write the formula
            formula = "=SUM({:s}:{:s})".format(start_range, end_range)
            worksheet.write_formula(cell_location, formula, total_fmt)
        # Add a total label
        worksheet.write_string(number_rows+1, 0, "Total",total_fmt) 
        # Define our range for the color formatting
        color_range = "O2:O{}".format(number_rows+1)
        # Add a format. Light red fill with dark red text.
        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})
        # Add a format. Green fill with dark green text.
        format2 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})
        # Highlight the top 5 values in Green
        worksheet.conditional_format(color_range, {'type': 'top',
                                                'value': '5',
                                                'format': format2})

        # Highlight the bottom 5 values in Red
        worksheet.conditional_format(color_range, {'type': 'bottom',
                                                'value': '5',
                                                'format': format1})

    def _set_spreadsheet_format_p16(self, writer):
        workbook = writer.book
        worksheet = writer.sheets['P16']
        worksheet.set_zoom(90)
        vol_fmt = workbook.add_format({'num_format': '0,0E+00'})
        numb_fmt = workbook.add_format({'num_format': '#,##0'})
        money_fmt = workbook.add_format({'num_format': '$#,##0'})
        # Account info columns
        number_rows, number_cols = self.hub_p16.shape
        worksheet.set_column('A:A', 20)
        worksheet.set_column(2, number_cols+1, 14, money_fmt)
        # Total formatting
        total_fmt = workbook.add_format({'align': 'right', 'num_format': '##0,00E+00', 'bold': True, 'bottom':6})
        for column in range(1, number_cols+1):
            # Determine where we will place the formula
            cell_location = xl_rowcol_to_cell(number_rows+1, column)
            # Get the range to use for the sum formula
            start_range = xl_rowcol_to_cell(1, column)
            end_range = xl_rowcol_to_cell(number_rows, column)
            # Construct and write the formula
            formula = "=SUM({:s}:{:s})".format(start_range, end_range)
            worksheet.write_formula(cell_location, formula, total_fmt)
        # Add a total label
        worksheet.write_string(number_rows+1, 0, "Total",total_fmt) 
        # Define our range for the color formatting
        color_range = "O2:O{}".format(number_rows+1)
        # Add a format. Light red fill with dark red text.
        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})
        # Add a format. Green fill with dark green text.
        format2 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})
        # Highlight the top 5 values in Green
        worksheet.conditional_format(color_range, {'type': 'top',
                                                'value': '5',
                                                'format': format2})

        # Highlight the bottom 5 values in Red
        worksheet.conditional_format(color_range, {'type': 'bottom',
                                                'value': '5',
                                                'format': format1})
            
    def write_results(self):
        Path("out\\").mkdir(parents=True, exist_ok=True)
        output_name = 'out/' + self.projeto.prod._file_name[0] + '_AEPP' + self.projeto.prod._file_name[1]
        writer = pd.ExcelWriter(output_name, engine='xlsxwriter')
        self.projeto.prod.prod_anual.to_excel(writer, sheet_name='Prod_Anual')
        self.projeto.prod.prod_trim.to_excel(writer, sheet_name='Prod_Tri_PE')
        self.financiamento.to_excel(writer, sheet_name='Financiamento')
        if self.projeto.tarefa in ('4A', '4B'):
            self.hub_p16.to_excel(writer, sheet_name='P16')
            self._set_spreadsheet_format_p16(writer)
        self.hub.to_excel(writer, sheet_name='Fluxo_Caixa')
        self._set_spreadsheet_format_prod_anual(writer)
        self._set_spreadsheet_format_prod_trimestral(writer)
        self._set_spreadsheet_format_financ(writer)
        self._set_spreadsheet_format_fluxo_caixa(writer)
        writer.close()
        print('Resultados gerados! Veja a pasta @out.')