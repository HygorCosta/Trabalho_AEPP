import pandas as pd
import yaml

class Capex:

    def __init__(self, config) -> None:
        self.data = self.read(config)

    def read(self, config):
        with open(config, 'r') as f:
            data = yaml.safe_load(f)
        return data

    def umbilical(self, tramos=4):
        acessorios = 50e3 * tramos
        comprimento = 3*2500 + 1*2255
        duto = 630 * comprimento
        diarias = round(comprimento / 6e3)
        taxa_servico = 30e3
        plsv = (250e3 * diarias)


