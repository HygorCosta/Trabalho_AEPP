from capex import Capex

def test_create_exist():
    capex = Capex('config_tarefa_4.yaml')
    assert capex is not None