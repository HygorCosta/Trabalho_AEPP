import pandas as pd
from cronograma import Cronograma

cronograma = Cronograma('dados_perfuracao.xlsx')
cronograma.write_base()