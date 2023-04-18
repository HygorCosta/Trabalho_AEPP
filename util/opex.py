import math
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date
import calendar


class OpexFlexivel:

    def __init__(self, dados, tipo='flexivel') -> None:
        self.dados = dados
        self.tipo = tipo
        self.pidf = dados['opex']['inspecao']['pidf']
        self.equip = dados['opex']['inspecao']['equipamentos']
        self.anos_restantes = self.dados['capex']['ano_fim'] - \
            self.pidf['ano_lanc']

    @property
    def _ano_inicial_opex(self):
        return date(self.pidf['ano_lanc'], 12, 31)

    def _anual_index(self):
        start_date = date(self.dados['capex']['ano_lancamento'], 12, 31)
        end_date = date(self.dados['capex']['ano_fim'], 12, 31)
        ano = pd.date_range(pd.to_datetime(start_date),
                            pd.to_datetime(end_date), freq='Y', name='date')
        return ano

    def _quarter_series(self):
        start_date = date(self.dados['capex']['ano_lancamento'], 1, 1)
        end_date = date(self.dados['capex']['ano_fim'], 12, 31)
        ano = pd.date_range(pd.to_datetime(start_date),
                            pd.to_datetime(end_date), freq='Q', name='date')
        return pd.Series(0, index=ano)

    def _init_series(self):
        return pd.Series(0, index=self._anual_index())

    def _pidf3(self):
        pidf3 = self._init_series()
        periodicidade = self.pidf['v3']['periodicidade']
        periodo = str(periodicidade) + 'Y'
        num_insp = math.floor(self.anos_restantes / periodicidade)
        anos = pd.date_range(self._ano_inicial_opex,
                             periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.pidf['v3']['duracao'] * self.pidf['v3']['diaria']
        pidf3[anos] = valor_inspecao
        return pidf3

    def _pidf2(self):
        pidf2 = self._init_series()
        periodicidade = self.pidf['v2']['periodicidade']
        periodo = str(periodicidade) + 'Y'
        num_insp = math.floor(self.anos_restantes / periodicidade)
        anos = pd.date_range(self._ano_inicial_opex,
                             periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.pidf['v2']['duracao'] * self.pidf['v2']['diaria']
        pidf2[anos] = valor_inspecao
        return pidf2

    def _pidf1(self):
        pidf1 = self._init_series()
        periodicidade = self.pidf['v1']['periodicidade'][self.tipo]
        num_insp = math.floor(self.anos_restantes / periodicidade)
        periodo = str(periodicidade) + 'Y'
        anos = pd.date_range(self._ano_inicial_opex,
                             periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.pidf['v1']['duracao'] * self.pidf['v1']['diaria']
        pidf1[anos] = valor_inspecao
        return pidf1

    def opex_inspecao_dutos(self):
        return self._pidf1() + self._pidf2() + self._pidf3()

    def opex_inspecao_equip(self):
        equip = InspecEquipamentos(
            self.equip, self._ano_inicial_opex, self.anos_restantes, self._anual_index())
        return equip.opex_inspec_anm()

    def opex_intervencao(self):
        interv = Intervencao(self.dados, self._ano_inicial_opex, self.anos_restantes, self._anual_index())
        return interv.opex()

    def opex(self):
        dutos = self.opex_inspecao_dutos()
        equip = self.opex_inspecao_equip()
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
        self.anos_restantes = self.dados['capex']['ano_fim'] - \
            self.pidr['ano_lanc']
    
    def _quarter_series(self):
        start_date = date(self.dados['capex']['ano_lancamento'], 1, 1)
        end_date = date(self.dados['capex']['ano_fim'], 12, 31)
        ano = pd.date_range(pd.to_datetime(start_date),
                            pd.to_datetime(end_date), freq='Q', name='date')
        return pd.Series(0, index=ano)

    @property
    def _ano_inicial_opex(self):
        return date(self.pidr['ano_lanc'], 12, 31)

    def _anual_index(self):
        start_date = date(self.dados['capex']['ano_lancamento'], 12, 31)
        end_date = date(self.dados['capex']['ano_fim'], 12, 31)
        ano = pd.date_range(pd.to_datetime(start_date),
                            pd.to_datetime(end_date), freq='Y', name='date')
        return ano

    def _init_series(self):
        return pd.Series(0, index=self._anual_index())

    def custo_pidr(self):
        pidr = self._init_series()
        periodicidade = self.pidr['periodicidade']
        num_insp = math.floor(self.anos_restantes / periodicidade)
        periodo = str(periodicidade) + 'Y'
        anos = pd.date_range(self._ano_inicial_opex,
                             periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.pidr['duracao'] * self.pidr['diaria']
        pidr[anos] = valor_inspecao
        return pidr

    def custo_insp_interna(self):
        insp_interna = self._init_series()
        periodicidade = self.interna['periodicidade']
        num_insp = math.floor(self.anos_restantes / periodicidade)
        periodo = str(periodicidade) + 'Y'
        anos = pd.date_range(self._ano_inicial_opex,
                             periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.interna['num_corridas'] * self.interna['pig']
        insp_interna[anos] = valor_inspecao
        return insp_interna

    def opex_inspecao_dutos(self):
        return self.custo_pidr() + self.custo_insp_interna()

    def opex_inspecao_equip(self):
        equip = InspecEquipamentos(self.equip, self._ano_inicial_opex, self.anos_restantes, self._anual_index())
        return equip.opex_inspec_anm() + equip.opex_inspec_plet()

    def opex_intervencao(self):
        interv = Intervencao(self.dados, self._ano_inicial_opex, self.anos_restantes, self._anual_index())
        return interv.opex()

    def opex_inibidores(self):
        inibidores = self._init_series()
        anos = pd.date_range(
            self._ano_inicial_opex, periods=self.anos_restantes+1, inclusive='both', freq='1Y')
        custo_por_dia = self.dados['opex']['inibidores']['custo'] * \
            self.dados['opex']['inibidores']['vazao']
        inibidores[anos] = custo_por_dia
        num_days = lambda x: 366 if calendar.isleap(x) else 365
        multipl = np.array([num_days(days) for days in inibidores.index.year.values])
        inibidores = inibidores.mul(multipl)
        return inibidores

    def opex(self):
        dutos = self.opex_inspecao_dutos()
        equip = self.opex_inspecao_equip()
        interv = self.opex_intervencao()
        inibidores = self.opex_inibidores()
        return dutos + equip + interv + inibidores

    def opex_descomissionamento(self):
        return self.dados['opex']['descomissionamento']['B']


class InspecEquipamentos:

    def __init__(self, equip, ano_inicial_opex, anos_restantes, index) -> None:
        self.equip = equip
        self.ano_inicial_opex = ano_inicial_opex
        self.anos_restantes = anos_restantes
        self.index = index

    def _init_series(self):
        return pd.Series(0, index=self.index)

    def opex_inspec_anm(self):
        inspec_anm = self._init_series()
        periodicidade = self.equip['anm']['periodicidade']
        num_insp = math.floor(self.anos_restantes /
                              periodicidade)
        periodo = str(periodicidade) + 'Y'
        anos = pd.date_range(
            self.ano_inicial_opex, periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.equip['anm']['duracao'] * self.equip['anm']['diaria']
        inspec_anm[anos] = valor_inspecao
        return inspec_anm

    def opex_inspec_plet(self):
        inspec_plet = self._init_series()
        periodicidade = self.equip['plets']['periodicidade']
        num_insp = math.floor(self.anos_restantes / periodicidade)
        periodo = str(periodicidade) + 'Y'
        anos = pd.date_range(
            self.ano_inicial_opex, periods=num_insp+1, inclusive='right', freq=periodo)
        valor_inspecao = self.equip['plets']['num'] * (
            self.equip['plets']['duracao'] / 24) * self.equip['plets']['diaria']
        inspec_plet[anos] = valor_inspecao
        return inspec_plet


class Intervencao:

    def __init__(self, dados, ano_inicial_opex, anos_restantes, index) -> None:
        self.interv = dados['opex']['intervencao']
        self.ano_inicial_opex = ano_inicial_opex
        self.anos_restantes = anos_restantes
        self.index = index

    def _init_series(self):
        return pd.Series(0, index=self.index)

    def opex(self):
        interv = self._init_series()
        periodicidade = self.interv['periodicidade']
        num_interv = math.floor(self.anos_restantes / periodicidade)
        periodo = str(periodicidade) + 'Y'
        anos = pd.date_range(
            self.ano_inicial_opex, periods=num_interv+1, inclusive='right', freq=periodo)
        sonda_por_dia = self.interv['sonda']['diaria'] + \
            self.interv['sonda']['servico']
        valor_interv = sonda_por_dia * \
            self.interv['duracao'] + self.interv['material']
        interv[anos] = valor_interv
        return interv
