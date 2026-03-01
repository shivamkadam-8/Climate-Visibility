# src/ml/model/s3_estimator.py

import sys
from pandas import DataFrame

from src.cloud_storage.aws_storage import SimpleStorageService
from src.exception import VisibilityException
from src.ml.model.estimator import VisibilityModel
from src.logger import logging


class VisibilityEstimator:
    """
    This class is used to save, load, and use a trained VisibilityModel
    from an S3-compatible bucket.
    """

    def __init__(self, bucket_name: str, model_name: str):
        """
        :param bucket_name: Name of your model bucket
        :param model_name: Path/name of model file in bucket
        """
        self.bucket_name = bucket_name
        self.model_name = model_name
        self.s3 = SimpleStorageService()
        self.loaded_model: VisibilityModel | None = None

    def is_model_present(self) -> bool:
        """
        Check whether model exists in bucket
        """
        try:
            return self.s3.s3_key_path_available(
                bucket_name=self.bucket_name,
                s3_key=self.model_name
            )
        except Exception as e:
            logging.error("Failed while checking model presence")
            return False

    def load_model(self) -> VisibilityModel:
        """
        Load the model from S3 bucket
        """
        try:
            logging.info("Loading model from storage")
            model = self.s3.load_model(
                model_name=self.model_name,
                bucket_name=self.bucket_name
            )
            return model
        except Exception as e:
            raise VisibilityException(e, sys)

    def save_model(self, from_file: str, remove: bool = False) -> None:
        """
        Upload local model file to S3 bucket

        :param from_file: Local path of model file
        :param remove: Remove local file after upload
        """
        try:
            logging.info("Uploading model to storage")

            self.s3.upload_file(
                from_file=from_file,
                to_filename=self.model_name,
                bucket_name=self.bucket_name,
                remove=remove
            )

            logging.info("Model uploaded successfully")

        except Exception as e:
            raise VisibilityException(e, sys)

    def predict(self, dataframe: DataFrame):
        """
        Run prediction using loaded model
        """
        try:
            if self.loaded_model is None:
                logging.info("Model not loaded, loading now")
                self.loaded_model = self.load_model()

            return self.loaded_model.predict(dataframe)

        except Exception as e:
            raise VisibilityException(e, sys)
