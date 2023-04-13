import pandas as pd
import yaml
from util.opex import OpexRigido, OpexFlexivel
from util.capex import FlowlineRigido, FlowlineFlexivel, Umbilical, GasLift, Riser

class Dutos:   

    def __init__(self, config, tipo: str) -> None:
        self.dados = self.read(config)
        self.tipo = tipo # 'A'-flexível, 'B'-rígido
        self.capex_flow, self.opex_flow = self.select_flowline()
        
    def read(self, config):
        with open(config, 'r') as f:
            dados = yaml.safe_load(f)
        return dados
    
    def select_flowline(self):
        if self.tipo == '4A':
            return FlowlineFlexivel(self.dados), OpexFlexivel(self.dados)
        elif self.tipo == '4B':
            return FlowlineRigido(self.dados), OpexRigido(self.dados)
        else:
            raise ValueError(f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')

    def capex(self):
        umbilical = Umbilical(self.dados).capex()
        gaslift = GasLift(self.dados).capex()
        riser = Riser(self.dados).capex()
        return umbilical + gaslift + riser + self.capex_flow.capex()
        
    def opex(self):
        return self.opex_flow.opex()
        
    def descomissionamento(self):
        return self.opex_flow.opex_descomissionamento()
