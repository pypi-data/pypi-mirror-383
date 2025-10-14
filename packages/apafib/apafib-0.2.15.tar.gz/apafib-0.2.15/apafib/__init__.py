"""
.. module:: __init__.py

__init__.py
*************

:Description: __init__.py


:Authors: bejar
    

:Version: 

:Created on: 06/05/2022 10:53

"""

from apafib.datasets import (
    fetch_apa_data,
    load_BCN_IBEX,
    load_BCN_UK,
    load_BCN_vuelos2021,
    load_medical_costs,
    load_stroke,
    load_wind_prediction,
    load_titanic,
    load_crabs,
    load_life_expectancy,
    load_electric_devices,
    load_energy,
    load_arxiv,
    load_attrition,
    load_literature,
    load_translation,
    load_heart_failure,
    load_MNIST,
    load_darwin,
    load_bands,
    load_NASDAQ,
    load_sentiment,
    load_BCN_cesta,
    load_BCN_ruido,
    load_credit_scoring,
    load_king_county_houses,
    load_wages,
    load_column,
    load_BCN_calor,
    load_BCN_museos,
    load_BCN_NO2,
    load_BCN_precios,
    load_BCN_sanciones,
    load_food,
    load_stress,
    load_health_news,
    load_MITBIH,
    load_sms_spam,
    load_travel_review,
    load_BCN_air,
    load_BCN_Francia,
    load_smile,
    load_vehiculos,
    load_Google,
    load_alzheimer,
    load_BCN_conmuters,
    load_BCN_ruidosos,
    load_BCN_vuelos,
    load_clientes,
    load_cupid,
    load_dormir,
    load_fraude,
    load_car_sales,
    load_world_music,
    load_mpg,
    load_CIS_Impuestos,
    load_CIS_ICC,
    load_CIS_cultura,
    load_potability,
    load_papers
)

from apafib.classifiers import BlackBoxClassifier, BlackBoxRegressor

__version__ = "0.2.15"

__all__ = [
    "fetch_apa_data",
    "BlackBoxClassifier",
    "BlackBoxRegressor",
    "load_BCN_IBEX",
    "load_BCN_UK",
    "load_BCN_vuelos2021",
    "load_medical_costs",
    "load_wind_prediction",
    "load_stroke",
    "load_titanic",
    "load_crabs",
    "load_life_expectancy",
    "load_electric_devices",
    "load_energy",
    "load_arxiv",
    "load_attrition",
    "load_literature",
    "load_translation",
    "load_heart_failure",
    "load_MNIST",
    "load_darwin",
    "load_bands",
    "load_NASDAQ",
    "load_sentiment",
    "load_BCN_cesta",
    "load_BCN_ruido",
    "load_BCN_calor",
    "load_BCN_museos",
    "load_BCN_NO2",
    "load_BCN_precios",
    "load_BCN_sanciones",
    "load_credit_scoring",
    "load_king_county_houses",
    "load_wages",
    "load_column",
    "load_food",
    "load_stress",
    "load_health_news",
    "load_MITBIH",
    "load_sms_spam",
    "load_travel_review",
    "load_BCN_air",
    "load_BCN_Francia",
    "load_smile",
    "load_vehiculos",
    "load_Google",
    "load_alzheimer",
    "load_BCN_conmuters",
    "load_BCN_ruidosos",
    "load_BCN_vuelos",
    "load_clientes",
    "load_cupid",
    "load_dormir",
    "load_fraude",
    "load_car_sales",
    "load_world_music",
    "load_mpg",
    "load_CIS_Impuestos",
    "load_CIS_ICC",
    "load_CIS_cultura",
    "load_potability",
    "load_papers"
]
