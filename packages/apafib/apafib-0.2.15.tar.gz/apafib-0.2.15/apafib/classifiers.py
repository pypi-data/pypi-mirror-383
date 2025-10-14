"""
.. module:: Classifers.py

setup.py
******

:Description: Classifiers.py

    Mock classifiers for testing purposes

:Authors:
    bejar

:Version: 

:Date:  06/05/2022
"""

from sklearn.base import BaseEstimator
from sklearn.svm import SVC, SVR
import numpy as np


class BlackBoxClassifier(BaseEstimator):
    """_BlackBoxClassifier_

    Black blox classifier for testing purposes, not to use for real data analysis

    """

    kernel = {"red": "linear", "green": "poly", "blue": "rbf"}

    def __init__(self, spin: int, charm: int, color: str) -> None:
        """_Class initializer_

        Args:
            par1 (int): _Parameter _
            par2 (string): _description_
        """
        if spin < -1 or spin > 1:
            raise ValueError("Spin parameter has to be a value in [-1,1]")
        if charm not in [1, 2, 3, 4]:
            raise ValueError("Spin parameter has to be a value in [-1,1]")
        if color not in ["red", "green", "blue"]:
            raise ValueError("Color parameter has to be one of red, green, blue")

        self.spin = spin
        self.color = color
        self.charm = charm
        self.classifier = SVC(
            C=np.power(10, 5 * self.color),
            kernel=self.kernel[self.color],
            degree=self.charm,
        )

    def fit(self, X, y):
        """_fitting function_

        Args:
            X (_type_): _Input variables_
            y (_type_): _Output variable_
        """
        self.classifier.fit(X, y)

    def predict(self, X):
        """_predicting function_

        Args:
            X (_type_): _description_
        """
        return self.classifier.predict(X)

    def score(self, X, y):
        """_Return accuracy of the classifier_

        Args:
            X (_type_): _description_
            y (_type_): _description_
        """
        return self.classifier.score(X, y)


class BlackBoxRegressor(BaseEstimator):
    """_BlackBoxRegressor_

    Black blox regressor for testing purposes, not to use for real data analysis

    """

    kernel = {"red": "linear", "green": "poly", "blue": "rbf"}

    def __init__(self, spin: int, charm: int, color: str) -> None:
        """_Class initializer_

        Args:
            par1 (int): _Parameter _
            par2 (string): _description_
        """
        if spin < -1 or spin > 1:
            raise ValueError("Spin parameter has to be a value in [-1,1]")
        if charm not in [1, 2, 3, 4]:
            raise ValueError("Spin parameter has to be a value in [-1,1]")
        if color not in ["red", "green", "blue"]:
            raise ValueError("Color parameter has to be one of red, green, blue")

        self.spin = spin
        self.color = color
        self.charm = charm
        self.classifier = SVR(
            C=np.power(10, 5 * self.color),
            kernel=self.kernel[self.color],
            degree=self.charm,
        )

    def fit(self, X, y):
        """_fitting function_

        Args:
            X (_type_): _Input variables_
            y (_type_): _Output variable_
        """
        self.classifier.fit(X, y)

    def predict(self, X):
        """_predicting function_

        Args:
            X (_type_): _description_
        """
        return self.classifier.predict(X)

    def score(self, X, y):
        """_Return accuracy of the classifier_

        Args:
            X (_type_): _description_
            y (_type_): _description_
        """
        return self.classifier.score(X, y)
