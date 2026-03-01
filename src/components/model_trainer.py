import sys
import os
import numpy as np
from dataclasses import dataclass
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from src.utils.main_utils import MainUtils
from src.ml.model.estimator import VisibilityModel
from src.exception import VisibilityException
from src.logger import logging


@dataclass
class ModelTrainerConfig:
    trained_model_path: str = os.path.join(
        "artifacts", "prediction_model", "model.pkl"
    )
    expected_accuracy: float = 0.45


class ModelTrainer:

    def __init__(self):
        self.config = ModelTrainerConfig()
        self.utils = MainUtils()

    def initiate_model_trainer(self, train_arr, test_arr, preprocessor_path):
        try:
            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            models = {
                "LinearRegression": LinearRegression(),
                "Ridge": Ridge(),
                "Lasso": Lasso(),
                "RandomForest": RandomForestRegressor(n_estimators=50),
                "GradientBoosting": GradientBoostingRegressor()
            }

            best_model, best_score = None, -1

            for name, model in models.items():
                model.fit(X_train, y_train)
                score = r2_score(y_test, model.predict(X_test))
                logging.info(f"{name} score: {score}")

                if score > best_score:
                    best_model = model
                    best_score = score

            if best_score < self.config.expected_accuracy:
                raise Exception("Model accuracy too low")

            preprocessor = self.utils.load_object(preprocessor_path)
            final_model = VisibilityModel(preprocessor, best_model)

            os.makedirs(
                os.path.dirname(self.config.trained_model_path),
                exist_ok=True
            )

            self.utils.save_object(
                self.config.trained_model_path,
                final_model
            )

            return self.config.trained_model_path

        except Exception as e:
            raise VisibilityException(e, sys)
