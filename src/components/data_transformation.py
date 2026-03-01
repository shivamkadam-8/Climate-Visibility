import sys
import os
import numpy as np
import pandas as pd

from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from src.constant import (
    ARTIFACT_TIMESTAMP_DIR,
    TARGET_COLUMN,
    FEATURE_COLUMNS
)
from src.exception import VisibilityException
from src.logger import logging
from src.utils.main_utils import MainUtils


# ----------------------------------------
# CONFIG
# ----------------------------------------

@dataclass
class DataTransformationConfig:
    transformed_dir: str = os.path.join(
        ARTIFACT_TIMESTAMP_DIR, "data_transformation"
    )
    preprocessor_path: str = os.path.join(
        transformed_dir, "preprocessor.pkl"
    )


# ----------------------------------------
# TRANSFORMATION
# ----------------------------------------

class DataTransformation:

    def __init__(self, valid_data_dir: str = None, dataframe: pd.DataFrame = None):
        try:
            self.config = DataTransformationConfig()
            self.utils = MainUtils()

            self.valid_data_dir = valid_data_dir
            self.dataframe = dataframe

            os.makedirs(self.config.transformed_dir, exist_ok=True)

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------------
    # Load data
    # ----------------------------------------

    def _load_data(self) -> pd.DataFrame:
        try:
            if self.dataframe is not None:
                return self.dataframe

            csv_files = [
                os.path.join(self.valid_data_dir, f)
                for f in os.listdir(self.valid_data_dir)
                if f.endswith(".csv")
            ]

            if not csv_files:
                raise Exception("No validated CSV files found")

            df_list = [pd.read_csv(f) for f in csv_files]
            return pd.concat(df_list, ignore_index=True)

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------------
    # Preprocessor
    # ----------------------------------------

    def _get_preprocessor(self):
        return Pipeline(
            steps=[
                ("scaler", StandardScaler())
            ]
        )

    # ----------------------------------------
    # Main method
    # ----------------------------------------

    def initiate_data_transformation(self):
        try:
            logging.info("🔄 Starting data transformation")

            df = self._load_data()

            X = df[FEATURE_COLUMNS]
            y = df[TARGET_COLUMN]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            preprocessor = self._get_preprocessor()
            X_train_scaled = preprocessor.fit_transform(X_train)
            X_test_scaled = preprocessor.transform(X_test)

            train_arr = np.c_[X_train_scaled, y_train.values]
            test_arr = np.c_[X_test_scaled, y_test.values]

            self.utils.save_object(
                self.config.preprocessor_path, preprocessor
            )

            logging.info("✅ Data transformation completed")

            return train_arr, test_arr, self.config.preprocessor_path

        except Exception as e:
            raise VisibilityException(e, sys)
