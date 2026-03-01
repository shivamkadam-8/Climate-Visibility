import sys
import os
import pandas as pd
from dataclasses import dataclass
from flask import Request  # ✅ Correct import for type hint

from src.utils.main_utils import MainUtils
from src.exception import VisibilityException
from src.logger import logging


@dataclass
class PredictionPipelineConfig:
    model_path: str = os.path.join(
        "artifacts", "prediction_model", "model.pkl"
    )


class PredictionPipeline:

    def __init__(self, request: Request):  # ✅ Fixed type hint
        self.request = request
        self.utils = MainUtils()
        self.config = PredictionPipelineConfig()

        self.feature_order = [
            "DRYBULBTEMPF",
            "RelativeHumidity",
            "WindSpeed",
            "WindDirection",
            "SeaLevelPressure"
        ]

    def run_pipeline(self):
        try:
            form_data = self.request.form.to_dict()

            input_values = [
                float(form_data[f]) for f in self.feature_order
            ]

            input_df = pd.DataFrame(
                [input_values],
                columns=self.feature_order
            )

            model = self.utils.load_object(self.config.model_path)
            prediction = model.predict(input_df)[0]

            return prediction

        except Exception as e:
            raise VisibilityException(e, sys)
