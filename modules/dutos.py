import pandas as pd
import yaml
from util.opex import OpexRigido, OpexFlexivel
from util.capex import FlowlineRigido, FlowlineFlexivel, Umbilical, GasLift, Riser


class Dutos:

    def __init__(self, config, tipo: str) -> None:
        self.dados = self.read(config)
        self.tipo = tipo  # 'A'-flexível, 'B'-rígido
        self.capex_flow, self.opex_flow = self.select_capex()
        self._opex_flexivel = OpexFlexivel(self.dados)
        self._opex_umbilical = OpexFlexivel(self.dados, tipo='umbilical')
        self.hub_opex = self.opex()
        self.total_opex = self.hub_opex.sum(axis=1)


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
        flowline = self.capex_flow.capex()
        return umbilical + gaslift + riser + flowline

    def opex(self):
        umbilical = self._opex_umbilical.opex_inspecao_dutos()
        gaslift = self._opex_flexivel.opex_inspecao_dutos()
        riser = self._opex_flexivel.opex_inspecao_dutos()
        if self.tipo == '4A':
            flowline = self.opex_flow.opex_inspecao_dutos()
            equipamentos = self.opex_flow.opex_inspecao_equip()
            intervencao = self.opex_flow.opex_intervencao()
            lista = [umbilical, gaslift, riser, flowline, equipamentos, intervencao]
            hub_opex = pd.concat(lista, axis=1)
            hub_opex.columns = ['umbilical', 'gaslift', 'riser', 'flowline', 'equipamentos', 'intervencao']
            return hub_opex
        elif self.tipo == '4B':
            flowline = self.opex_flow.opex_inspecao_dutos()
            equipamentos = self.opex_flow.opex_inspecao_equip()
            intervencao = self.opex_flow.opex_intervencao()
            inibidores = self.opex_flow.opex_inibidores()
            lista = [umbilical, gaslift, riser, flowline, equipamentos, intervencao, inibidores]
            hub_opex = pd.concat(lista, axis=1)
            hub_opex.columns = ['umbilical', 'gaslift', 'riser', 'flowline', 'equipamentos', 'intervencao', 'inibidores']
            return hub_opex
        else:
            raise ValueError(
                f'Parâmetro {self.tipo} eh invalido, apenas A para flexivel e B para rigido.')

    def opex_trimestral(self):
        opex_p16 = self.total_opex.repeat(4) / 4
        opex_p16.index = self.opex_flow._quarter_series().index
        return opex_p16

    def descomissionamento(self):
        return self.opex_flow.opex_descomissionamento()
