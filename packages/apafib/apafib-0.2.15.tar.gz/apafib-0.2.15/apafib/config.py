"""
.. module:: config.py

setup.py
******

:Description: config.py

    Configuration file for apafib python package

:Authors:
    bejar

:Version: 

:Date:  06/05/2022
"""

DATALINK = "http://www.cs.upc.edu/~bejar/datasets/"

datasets = {
    "Concrete Slump Test": (10, "slump_test"),
    "auto mpg": (10, "auto-mpg"),
    "HCV data": (10, "hcvdat"),
    "ILPD": (10, "ILPD"),
    "apendicitis": (10, "apendicitis"),
    "glass2": (10, "glass"),
    "rmftsa_ladata": (10, "rmftsa_ladata"),
    "telco-customer-churn": (10, "telco-customer-churn"),
}

barna_datasets = {
    "LlegadasInterior": ([13, 14, 15, 16, 17, 28, 29, 30, 31], [43, 44, 45, 46, 47]),
    "LlegadasExterior": ([13, 14, 15, 16, 17, 28, 29, 30, 31], [38.39, 40, 41, 42]),
    "ReservasInternacionales": ([6, 7, 8, 9, 10, 11, 12, 25, 26, 27, 35, 21], [19]),
    "PrecioElectricidad": ([1, 4, 5, 6, 7, 8, 20, 28, 29, 30, 31, 14], [35]),
    "Gasolina": ([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 22, 23, 24], [1]),
}
