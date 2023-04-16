from modules.producao import ProducaoTarefa01
import pytest
import pandas as pd


def bdp_to_qmm3(x):
    return x * 365 / (4 * 1000 * 6.29)


def test_prod_oil():
    prod = ProducaoTarefa01()
    oil = prod._prod_oil_t1()
    assert pytest.approx(oil[0]) == 0
    assert pytest.approx(oil[3]) == 21250
    assert pytest.approx(oil[4]) == 42500
    assert pytest.approx(oil[5]) == 63750
    assert pytest.approx(oil[6]) == 85000
    assert pytest.approx(oil[-1]) == 22480.56721


def test_prod_water():
    prod = ProducaoTarefa01()
    water = prod._prod_water_t1()
    assert pytest.approx(water[0]) == 0
    assert pytest.approx(water[3]) == 582.03375
    assert pytest.approx(water[4]) == 948.54379
    assert pytest.approx(water[5]) == 1534.70126
    assert pytest.approx(water[6]) == 2454.77071
    assert pytest.approx(water[-1]) == 32356.006952


def test_inj_water():
    prod = ProducaoTarefa01()
    water = prod._inj_water_t1()
    assert pytest.approx(water[0]) == 0
    assert pytest.approx(water[3]) == 35450.00
    assert pytest.approx(water[4]) == 70900.00
    assert pytest.approx(water[5]) == 106350.00
    assert pytest.approx(water[6]) == 141800.00
    assert pytest.approx(water[-1]) == 88706.55225


def test_inj_water_anual():
    prod = ProducaoTarefa01()
    water = prod.prod_anual.water_inj
    assert pytest.approx(water[0]) == 0 * 365
    assert pytest.approx(water[3]) == 35450.00 * 365
    assert pytest.approx(water[4]) == 70900.00 * 365
    assert pytest.approx(water[5]) == 106350.00 * 365
    assert pytest.approx(water[6]) == 141800.00 * 365
    assert pytest.approx(water[-1]) == 88706.55225 * 365


def test_trimestral_inj_water():
    prod = ProducaoTarefa01()
    water_inj = prod.prod_trim.water_inj
    assert pytest.approx(water_inj.iloc[0*4]) == 0
    assert pytest.approx(water_inj.iloc[3*4]) == bdp_to_qmm3(35450.00)
    assert pytest.approx(water_inj.iloc[4*4]) == bdp_to_qmm3(70900.00)
    assert pytest.approx(water_inj.iloc[5*4]) == bdp_to_qmm3(106350.00)
    assert pytest.approx(water_inj.iloc[6*4]) == bdp_to_qmm3(141800.00)
    assert pytest.approx(water_inj.iloc[-1]) == bdp_to_qmm3(88706.55225)


def test_trimestral_to_anual_oil():
    prod = ProducaoTarefa01()
    trim = prod.prod_trim.oil_prod
    grupo = pd.Grouper(level='date', axis=0, freq='Y')
    trim.index.name = 'date'
    trim_to_anual = trim.groupby(grupo).sum()
    assert pytest.approx(trim_to_anual.iloc[0]*1000*6.29) == 0
    assert pytest.approx(trim_to_anual.iloc[3]*1000*6.29) == 365 * 21250
    assert pytest.approx(trim_to_anual.iloc[4]*1000*6.29) == 365 * 42500
    assert pytest.approx(trim_to_anual.iloc[5]*1000*6.29) == 365 * 63750
    assert pytest.approx(trim_to_anual.iloc[6]*1000*6.29) == 365 * 85000
    assert pytest.approx(trim_to_anual.iloc[-1]*1000*6.29) == 365 * 22480.56721
