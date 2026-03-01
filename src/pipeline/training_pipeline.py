import sys
import os
import traceback

from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.exception import VisibilityException
from src.logger import logging


class TrainingPipeline:

    # ---------------------------------
    # DATA INGESTION
    # ---------------------------------
    def start_data_ingestion(self):
        try:
            logging.info("🚀 Starting Data Ingestion")
            data_ingestion = DataIngestion()
            raw_data_dir = data_ingestion.initiate_data_ingestion()
            return raw_data_dir
        except Exception as e:
            traceback.print_exc()
            raise VisibilityException(e, sys)

    # ---------------------------------
    # DATA VALIDATION
    # ---------------------------------
    def start_data_validation(self, raw_data_dir: str):
        try:
            logging.info("🔍 Starting Data Validation")
            data_validation = DataValidation(raw_data_dir=raw_data_dir)
            valid_data_dir = data_validation.initiate_data_validation()

            if not os.listdir(valid_data_dir):
                raise Exception("Validated data directory is empty")

            return valid_data_dir
        except Exception as e:
            traceback.print_exc()
            raise VisibilityException(e, sys)

    # ---------------------------------
    # DATA TRANSFORMATION
    # ---------------------------------
    def start_data_transformation(self, valid_data_dir=None, dataframe=None):
        try:
            logging.info("🔄 Starting Data Transformation")

            if dataframe is not None:
                transformer = DataTransformation(dataframe=dataframe)
            else:
                transformer = DataTransformation(valid_data_dir=valid_data_dir)

            train_arr, test_arr, preprocessor_path = (
                transformer.initiate_data_transformation()
            )

            return train_arr, test_arr, preprocessor_path

        except Exception as e:
            traceback.print_exc()
            raise VisibilityException(e, sys)

    # ---------------------------------
    # MODEL TRAINING
    # ---------------------------------
    def start_model_training(self, train_arr, test_arr, preprocessor_path):
        try:
            logging.info("🤖 Starting Model Training")
            model_trainer = ModelTrainer()
            model_path = model_trainer.initiate_model_trainer(
                train_arr=train_arr,
                test_arr=test_arr,
                preprocessor_path=preprocessor_path
            )
            return model_path
        except Exception as e:
            traceback.print_exc()
            raise VisibilityException(e, sys)

    # ---------------------------------
    # FULL PIPELINE
    # ---------------------------------
    def run_pipeline(self, input_dataframe=None):
        try:
            logging.info("🔥 Training Pipeline Started")

            if input_dataframe is None:
                # 1️⃣ Ingestion
                raw_data_dir = self.start_data_ingestion()

                # 2️⃣ Validation
                valid_data_dir = self.start_data_validation(raw_data_dir)

                # 3️⃣ Transformation
                train_arr, test_arr, preprocessor_path = (
                    self.start_data_transformation(valid_data_dir=valid_data_dir)
                )
            else:
                train_arr, test_arr, preprocessor_path = (
                    self.start_data_transformation(dataframe=input_dataframe)
                )

            # 4️⃣ Model Training
            model_path = self.start_model_training(
                train_arr, test_arr, preprocessor_path
            )

            logging.info(f"✅ Training completed successfully")
            logging.info(f"📦 Model saved at: {model_path}")

            return model_path

        except Exception as e:
            traceback.print_exc()
            raise VisibilityException(e, sys)


if __name__ == "__main__":
    pipeline = TrainingPipeline()
    pipeline.run_pipeline()
