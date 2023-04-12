import math

class OpexFlexivel:
    
    def __init__(self, dados) -> None:
        self.dados = dados
        self.pidf = dados['opex']['inspecao']['pidf']
        self.equip = dados['opex']['inspecao']['equipamentos']
    
    def _pidf3(self):
        num_insp = math.floor(self.pidf['anos_restante'] / self.pidf['v3']['periodicidade'])
        return num_insp * self.pidf['v3']['duracao'] * self.pidf['v3']['diaria']
    
    def _pidf2(self):
        num_insp = math.floor(self.pidf['anos_restante'] / self.pidf['v2']['periodicidade'])
        return num_insp * self.pidf['v2']['duracao'] * self.pidf['v2']['diaria']
    
    def _pidf1(self):
        num_insp = math.floor(self.pidf['anos_restante'] / self.pidf['v1']['periodicidade']['umbilical'])
        return num_insp * self.pidf['v1']['duracao'] * self.pidf['v1']['diaria']

    def opex_inspecao_dutos(self):
        return self._pidf1() + self._pidf2() + self._pidf3()
    
    def opex_inspecao_equipamentos(self):
        equip = InspecEquipamentos(self.equip, self.pidf)
        return equip.opex_inspec_anm()
    
    def opex_intervencao(self):
        interv = Intervencao(self.dados, self.pidf)
        return interv.opex()
    
    def opex(self):
        dutos = self.opex_inspecao_dutos()
        equip = self.opex_inspecao_equipamentos()
        interv = self.opex_intervencao()
        return dutos + equip + interv
    
    def opex_descomissionamento(self):
        return self.dados['opex']['descomissionamento']['A']


class OpexRigido:
        
    def __init__(self, dados) -> None:
        self.dados = dados
        self.pidr = dados['opex']['inspecao']['pidr']
        self.interna = dados['opex']['inspecao']['pidr']['interna']
        self.equip = dados['opex']['inspecao']['equipamentos']

    def custo_pidr(self):
        num_insp = math.floor(self.pidr['anos_restante'] / self.pidr['periodicidade'])
        return num_insp * self.pidr['duracao'] * self.pidr['diaria']
    
    def custo_insp_interna(self):
        num_insp = math.floor(self.pidr['anos_restante'] / self.interna['periodicidade'])
        return num_insp * self.interna['num_corridas'] * self.interna['pig']
    
    def opex_inspecao_dutos(self):
        return self.custo_pidr() + self.custo_insp_interna()
    
    def opex_inspecao_equipamentos(self):
        equip = InspecEquipamentos(self.equip, self.pidr)
        return equip.opex_inspec_anm() + equip.opex_inspec_plet()
    
    def opex_intervencao(self):
        interv = Intervencao(self.dados, self.pidr)
        return interv.opex()
    
    def opex_inibidores(self):
        num_dias = self.pidr['anos_restante'] * 365
        custo = self.dados['opex']['inibidores']['custo']
        vazao = self.dados['opex']['inibidores']['vazao']
        return num_dias * custo * vazao
    
    def opex(self):
        dutos = self.opex_inspecao_dutos()
        equip = self.opex_inspecao_equipamentos()
        interv = self.opex_intervencao()
        inibidores = self.opex_inibidores()
        return dutos + equip + interv + inibidores
           
    def opex_descomissionamento(self):
        return self.dados['opex']['descomissionamento']['B']
        
    
class InspecEquipamentos:

    def __init__(self, equip, pi) -> None:
        self.equip = equip
        self.pi = pi

    def opex_inspec_anm(self):
        num_insp = math.floor(self.pi['anos_restante'] / self.equip['anm']['periodicidade'])
        return num_insp * self.equip['anm']['duracao'] * self.equip['anm']['diaria']

    def opex_inspec_plet(self):
        plets = self.equip['plets']
        num_insp = math.floor(self.pi['anos_restante'] / plets['periodicidade'])
        return num_insp * plets['num'] * (plets['duracao'] / 24) * plets['diaria']
    

class Intervencao:
   
    def __init__(self, dados, pi) -> None:
        self.interv = dados['opex']['intervencao']
        self.pi = pi

    def opex(self):
        num_interv = math.floor(self.pi['anos_restante'] / self.interv['periodicidade'])
        sonda_por_dia = self.interv['sonda']['diaria'] + self.interv['sonda']['diaria']
        return num_interv * sonda_por_dia * self.interv['duracao'] + self.interv['material']