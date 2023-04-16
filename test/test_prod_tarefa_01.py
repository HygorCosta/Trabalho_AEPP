from modules.producao import ProducaoTarefa01
import pytest
import pandas as pd


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
    assert pytest.approx(water[4]) == 70900.00 * 366
    assert pytest.approx(water[5]) == 106350.00 * 365
    assert pytest.approx(water[6]) == 141800.00 * 365
    assert pytest.approx(water[-1]) == 88706.55225 * 365


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


def test_day_to_anual_prod_oil():
    prod = ProducaoTarefa01()
    oil = prod.prod_anual.oil_prod
    assert pytest.approx(oil.iloc[0]) == 0
    assert pytest.approx(oil.iloc[3]) == 21250 * 365
    assert pytest.approx(oil.iloc[4]) == 42500 * 366
    assert pytest.approx(oil.iloc[5]) == 63750 * 365
    assert pytest.approx(oil.iloc[6]) == 85000 * 365
    assert pytest.approx(oil.iloc[-2]) == 24110.59225 * 366


def test_trimestral_to_anual_oil():
    prod = ProducaoTarefa01()
    equiv_oil = prod.prod_trim.equiv_oil
    assert pytest.approx(equiv_oil.iloc[0]) == 0
    assert pytest.approx(equiv_oil.iloc[3*4]) == 1354.29427 / 4
    assert pytest.approx(equiv_oil.iloc[4*4]) == 2716.00934 / 4
    assert pytest.approx(equiv_oil.iloc[5*4]) == 4062.882821 / 4
    assert pytest.approx(equiv_oil.iloc[6*4]) == 5417.17709 / 4
    assert pytest.approx(equiv_oil.iloc[-1]) == 358.18004
