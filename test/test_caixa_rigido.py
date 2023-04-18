from modules.caixa import Caixa
from modules.results import Results
import pytest

def create_projeto():
    tarefa_04_rigido = Caixa(
        tarefa='4B', dados_producao='producao/Producao_P16R.xlsx')
    return tarefa_04_rigido

def test_participacao_especial():
    projeto = create_projeto()
    Results(projeto).write_results()
    

