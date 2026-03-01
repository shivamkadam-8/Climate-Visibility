import sys
import os
import shutil
from typing import List
import pandas as pd
from dataclasses import dataclass

from src.constant import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    ARTIFACT_TIMESTAMP_DIR
)
from src.exception import VisibilityException
from src.logger import logging


# ==========================================
# CONFIG
# ==========================================

@dataclass
class DataValidationConfig:
    data_validation_dir: str = os.path.join(
        ARTIFACT_TIMESTAMP_DIR, "data_validation"
    )
    valid_data_dir: str = os.path.join(
        data_validation_dir, "validated"
    )
    invalid_data_dir: str = os.path.join(
        data_validation_dir, "invalid"
    )


# ==========================================
# DATA VALIDATION CLASS
# ==========================================

class DataValidation:
    def __init__(self, raw_data_dir: str):
        """
        raw_data_dir should come from data_ingestion output
        """
        try:
            self.raw_data_dir = raw_data_dir
            self.config = DataValidationConfig()

            os.makedirs(self.config.valid_data_dir, exist_ok=True)
            os.makedirs(self.config.invalid_data_dir, exist_ok=True)

            logging.info(f"Raw data directory: {self.raw_data_dir}")
            logging.info(f"Validation directory: {self.config.data_validation_dir}")

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------
    # VALIDATION METHODS
    # ----------------------------------

    def validate_file_name(self, file_path: str) -> bool:
        return file_path.lower().endswith(".csv")

    def validate_schema(self, file_path: str) -> bool:
        """
        Checks:
        - Required feature columns exist
        - Target column exists
        """
        try:
            df = pd.read_csv(file_path, nrows=5)

            expected_columns = set(FEATURE_COLUMNS + [TARGET_COLUMN])
            actual_columns = set(df.columns)

            missing_columns = expected_columns - actual_columns

            if missing_columns:
                logging.error(
                    f"❌ Missing columns in {file_path}: {missing_columns}"
                )
                return False

            return True

        except Exception as e:
            logging.error(f"Schema validation failed for {file_path}: {e}")
            return False

    def validate_missing_values(self, file_path: str) -> bool:
        """
        Reject file if any column is completely null
        """
        try:
            df = pd.read_csv(file_path)

            for col in df.columns:
                if df[col].isna().all():
                    logging.error(
                        f"❌ Column '{col}' has all missing values in {file_path}"
                    )
                    return False

            return True

        except Exception as e:
            logging.error(f"Missing value validation failed for {file_path}: {e}")
            return False

    # ----------------------------------
    # FILE OPERATIONS
    # ----------------------------------

    def get_raw_files(self) -> List[str]:
        try:
            return [
                os.path.join(self.raw_data_dir, file)
                for file in os.listdir(self.raw_data_dir)
                if file.lower().endswith(".csv")
            ]
        except Exception as e:
            raise VisibilityException(e, sys)

    def move_file(self, src: str, dest_dir: str):
        try:
            filename = os.path.basename(src)
            dest_path = os.path.join(dest_dir, filename)

            if os.path.exists(dest_path):
                os.remove(dest_path)

            shutil.move(src, dest_path)

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------
    # MAIN ENTRY
    # ----------------------------------

    def initiate_data_validation(self) -> str:
        try:
            raw_files = self.get_raw_files()

            if not raw_files:
                raise Exception("❌ No raw CSV files found for validation")

            valid_count = 0

            for file_path in raw_files:
                logging.info(f"Validating file: {file_path}")

                if (
                    self.validate_file_name(file_path)
                    and self.validate_schema(file_path)
                    and self.validate_missing_values(file_path)
                ):
                    self.move_file(file_path, self.config.valid_data_dir)
                    valid_count += 1
                else:
                    self.move_file(file_path, self.config.invalid_data_dir)

            if valid_count == 0:
                raise Exception("❌ No valid files after data validation")

            logging.info("✅ Data validation completed successfully")
            return self.config.valid_data_dir

        except Exception as e:
            raise VisibilityException(e, sys)
