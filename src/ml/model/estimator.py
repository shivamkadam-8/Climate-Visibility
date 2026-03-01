import sys
from src.exception import VisibilityException
from src.logger import logging


class VisibilityModel:
    """
    Combines:
    - preprocessor
    - trained ML model
    """

    def __init__(self, preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model

    def predict(self, X):
        try:
            X_transformed = self.preprocessor.transform(X)
            return self.model.predict(X_transformed)
        except Exception as e:
            raise VisibilityException(e, sys)
