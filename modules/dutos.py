import pandas as pd
import yaml
from util.opex import OpexRigido, OpexFlexivel
from util.capex import FlowlineRigido, FlowlineFlexivel, Umbilical, GasLift, Riser


class Dutos:

    def __init__(self, config, tipo: str) -> None:
        self.dados = self.read(config)
        self.tipo = tipo  # 'A'-flexível, 'B'-rígido
        self.capex_flow, self.opex_flow = self.select_capex()

    def read(self, config):
        with open(config, 'r') as f:
            dados = yaml.safe_load(f)
        return dados

    def select_capex(self):
        if self.tipo == '4A':
            return FlowlineFlexivel(self.dados), OpexFlexivel(self.dados)
        elif self.tipo == '4B':
            return FlowlineRigido(self.dados), OpexRigido(self.dados)
        else:
            raise ValueError(
                f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')

    def capex(self):
        umbilical = Umbilical(self.dados).capex()
        gaslift = GasLift(self.dados).capex()
        riser = Riser(self.dados).capex()
        return umbilical + gaslift + riser + self.capex_flow.capex()

    def opex(self):
        umbilical = OpexFlexivel(
            self.dados, tipo='umbilical').opex_inspecao_dutos()
        gaslift = self.opex_flow.opex_inspecao_dutos()
        riser = self.opex_flow.opex_inspecao_dutos()
        if self.tipo == '4A':
            flowline = self.opex_flow.opex_inspecao_dutos()
            equipamentos = self.opex_flow.opex_inspecao_equip()
            intervencao = self.opex_flow.opex_intervencao()
            return umbilical + gaslift + riser + flowline + equipamentos + intervencao
        elif self.tipo == '4B':
            flowline = self.opex_flow(self.dados).opex_inspecao_dutos()
            equipamentos = self.opex_flow(self.dados).opex_inspecao_equip()
            intervencao = self.opex_flow(self.dados).opex_intervencao()
            inibidores = self.opex_flow(self.dados).opex_inibidores()
            return umbilical + gaslift + riser + flowline + equipamentos + intervencao + inibidores
        else:
            raise ValueError(
                f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')

    def opex_trimestral(self):
        opex_p16 = self.opex().repeat(4) / 4
        opex_p16.index = self.opex_flow._quarter_series().index
        return opex_p16

    def descomissionamento(self):
        return self.opex_flow.opex_descomissionamento()
