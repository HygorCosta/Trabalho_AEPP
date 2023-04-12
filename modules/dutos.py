import pandas as pd
import yaml
from util.opex import OpexRigido, OpexFlexivel
from util.capex import FlowlineRigido, FlowlineFlexivel, Umbilical, GasLift, Riser

class Dutos:   

    def __init__(self, config, tipo: str) -> None:
        self.dados = self.read(config)
        self.tipo = tipo # 'A'-flexível, 'B'-rígido
        
    def read(self, config):
        with open(config, 'r') as f:
            dados = yaml.safe_load(f)
        return dados

    def capex(self):
        if self.tipo == '4A':
            umbilical = Umbilical(self.dados).capex()
            gaslift = GasLift(self.dados).capex()
            riser = Riser(self.dados).capex()
            flowline_flexivel = FlowlineFlexivel(self.dados).capex()
            return umbilical + gaslift + riser + flowline_flexivel
        elif self.tipo == '4B':
            umbilical = Umbilical(self.dados).capex()
            gaslift = GasLift(self.dados).capex()
            riser = Riser(self.dados).capex()
            return FlowlineRigido(self.dados).capex()
        else:
            raise ValueError(f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')
        
    def opex(self):
        if self.tipo == '4A':
            return OpexFlexivel(self.dados).opex()
        elif self.tipo == '4B':
            return OpexRigido(self.dados).opex()
        else:
            raise ValueError(f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')
        
    def descomissionamento(self):
        if self.tipo == '4A':
            return OpexFlexivel(self.dados).opex_descomissionamento()
        elif self.tipo == '4B':
            return OpexRigido(self.dados).opex_descomissionamento()
        else:
            raise ValueError(f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')
