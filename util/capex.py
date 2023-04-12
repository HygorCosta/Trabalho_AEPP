import numpy as np


class BaseFlexivel:

    def __init__(self, dado_flexivel, geral):
        self.dados = dado_flexivel
        self.plsv = geral['capex']['pslv']
        self.pidf = geral['capex']['pidf']['v5']
    
    @property
    def comp_flowline(self):
        return self.dados['tramos']['flowline']['num_tramos'] * self.dados['tramos']['flowline']['comp']
    
    @property
    def comp_riser(self):
        return self.dados['tramos']['riser']['num_tramos'] * self.dados['tramos']['riser']['comp']
    
    @property
    def _comp_total(self):
        return self.comp_flowline + self.comp_riser
    
    @property
    def tramos_flowline(self):
        return self.dados['tramos']['flowline']['num_tramos']
    
    @property
    def tramos_riser(self):
        return self.dados['tramos']['riser']['num_tramos']
    
    @property
    def _num_tramos(self):
        return self.tramos_flowline + self.tramos_riser
    
    def custo_duto(self, comprimento, num_tramos):
        custo_extensao_duto = self.dados['duto_por_metro'] * comprimento
        custo_acessorios = self.dados['acessorios'] * num_tramos
        return custo_extensao_duto + custo_acessorios + self.dados['obras_uep']
    
    def custo_plsv(self, comprimento, num_tramos, vel, flut=0):
        dias_lanc = comprimento / vel
        dias_conexao_tramos = (num_tramos - 1) * self.plsv['conexao_tramos'] / 24
        num_diarias = self.plsv['carga'] + dias_lanc + self.plsv['pull_in']/24 + self.plsv['cvd']/24 + dias_conexao_tramos + flut
        num_servico = self.plsv['pull_in']/24 + self.plsv['cvd']/24 + dias_conexao_tramos + dias_lanc + flut
        custo_diarias = num_diarias * self.plsv['diaria']
        custo_servico = num_servico* self.plsv['servico']
        return custo_diarias + custo_servico
    
    def custo_pidf(self, duracao):
        return self.pidf['diaria'] * duracao


class FlowlineFlexivel(BaseFlexivel):

    def __init__(self, dados) -> None:
        super().__init__(dados['capex']['coleta']['flowline']['A'], dados)

    @property
    def _comp_total(self):
        comp_tramo = np.multiply(self.dados['num_tramos'], self.dados['comp'])
        return np.sum(comp_tramo)
    
    @property
    def _num_tramos(self):
        return np.sum(self.dados['num_tramos'])
        
    def _custo_duto(self):
        custo_extensao_duto = self.dados['duto_por_metro'] * self._comp_total
        custo_acessorios = self.dados['acessorios'] * self._num_tramos
        return custo_extensao_duto + custo_acessorios
    
    def _custo_plsv(self):
        return self.custo_plsv(self._comp_total, self._num_tramos, self.plsv['vel']['coleta'])
        
    def _custo_pidf(self):
        return self.custo_pidf(self.pidf['duracao']['coleta']['flow'])
    
    def capex(self):
        custo_duto = self._custo_duto()
        custo_plsv = self._custo_plsv()
        custo_pidf = self._custo_pidf()
        anm = self.dados['anm']
        return custo_duto + custo_plsv + custo_pidf + anm


class FlowlineRigido:

    def __init__(self, dados) -> None:
        self.dados = dados
        self.flowline = dados['capex']['coleta']['flowline']
        self.pidf = dados['capex']['pidf']['v5']

    @property
    def _comp_total(self):
        dados = self.flowline['A']
        comp_tramo = np.multiply(dados['num_tramos'], dados['comp'])
        return np.sum(comp_tramo)
        
    def custo_duto(self):
        dados = self.flowline['B']
        custo_extensao_duto = dados['duto_por_metro'] * self._comp_total
        return custo_extensao_duto
    
    def custo_embarcacao(self):
        embarcacao = self.flowline['B']['embarcacao']
        lancamento = self._comp_total / embarcacao['vel']
        plets = self.flowline['B']['plet']
        inst_plet = plets['num'] * plets['vel'] / 24
        tempo = lancamento + inst_plet
        diaria = (embarcacao['diaria'] + embarcacao['servico']) * tempo
        return diaria + embarcacao['contratacao']
    
    def custo_equipamentos(self):
        anm = self.flowline['B']['anm']
        plet = self.flowline['B']['plet']['num'] * self.flowline['B']['plet']['custo']
        jumper = self.flowline['B']['jumper']['custo'] + self.flowline['B']['jumper']['instalacao']
        return anm + plet + jumper

    def custo_pidf(self):
        return self.pidf['diaria'] * self.pidf['duracao']['coleta']['flow']
            
    def capex(self):
        custo_duto = self.custo_duto()
        custo_plsv = self.custo_embarcacao()
        custo_equip = self.custo_equipamentos()
        custo_pidf = self.custo_pidf()
        return custo_duto + custo_plsv + custo_pidf + custo_equip
    

class GasLift(BaseFlexivel):

    def __init__(self, dados) -> None:
        super().__init__(dados['capex']['gas_lift'], dados)

    def _custo_duto(self):
        return self.custo_duto(self._comp_total, self._num_tramos)
    
    def _custo_plsv(self):
        return self.custo_plsv(self._comp_total, self._num_tramos, self.plsv['vel']['base'])
    
    def _custo_pidf(self):
        return self.custo_pidf(self.pidf['duracao']['base'])

    def capex(self):
        custo_duto = self._custo_duto()
        custo_plsv = self._custo_plsv()
        custo_pidf = self._custo_pidf()
        return custo_duto + custo_plsv + custo_pidf
    

class Riser(BaseFlexivel):

    def __init__(self, dados) -> None:
        super().__init__(dados['capex']['coleta']['riser'], dados)
    
    @property
    def _comp_total_riser(self):
        return self.dados['num_tramos'] * self.dados['comp']
    
    @property
    def _num_tramos_riser(self):
        return self.dados['num_tramos']
    
    def _custo_duto(self):
        return self.custo_duto(self._comp_total_riser, self._num_tramos_riser)

    def tempo_flutuadores(self):
        return  self.dados['flut'] * self.plsv['vel_flut'] / 24
    
    def _custo_plsv(self):
        return self.custo_plsv(self._comp_total_riser, self._num_tramos_riser, self.plsv['vel']['coleta'], self.tempo_flutuadores())
    
    def _custo_pidf(self):
        return self.custo_pidf(self.pidf['duracao']['coleta']['riser'])
    
    def capex(self):
        custo_duto = self._custo_duto()
        custo_plsv = self._custo_plsv()
        custo_pidf = self._custo_pidf()
        return custo_duto + custo_plsv + custo_pidf
    

class Umbilical(BaseFlexivel):

    def __init__(self, dados) -> None:
        super().__init__(dados['capex']['umbilical'], dados)

    def _custo_duto(self):
        return self.custo_duto(self._comp_total, self._num_tramos)
    
    def _custo_plsv(self):
        return self.custo_plsv(self._comp_total, self._num_tramos, self.plsv['vel']['base'])
    
    def _custo_pidf(self):
        return self.custo_pidf(self.pidf['duracao']['base'])

    def capex(self):
        custo_duto = self._custo_duto()
        custo_plsv = self._custo_plsv()
        custo_pidf = self._custo_pidf()
        return custo_duto + custo_plsv + custo_pidf