import sys
import os
import pickle
import yaml

from src.exception import VisibilityException
from src.logger import logging


class MainUtils:
    def __init__(self) -> None:
        pass

    # -------------------------------
    # YAML UTILS
    # -------------------------------
    def read_yaml_file(self, filename: str) -> dict:
        try:
            logging.info(f"Reading YAML file: {filename}")

            with open(filename, "r", encoding="utf-8") as yaml_file:
                return yaml.safe_load(yaml_file)

        except Exception as e:
            raise VisibilityException(e, sys) from e

    def read_schema_config_file(self) -> dict:
        try:
            schema_path = os.path.join("config", "schema.yaml")
            return self.read_yaml_file(schema_path)

        except Exception as e:
            raise VisibilityException(e, sys) from e

    # -------------------------------
    # OBJECT SERIALIZATION
    # -------------------------------
    @staticmethod
    def save_object(file_path: str, obj: object) -> None:
        logging.info("Entered save_object method")

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as file_obj:
                pickle.dump(obj, file_obj)

            logging.info(f"Object saved successfully at: {file_path}")

        except Exception as e:
            raise VisibilityException(e, sys) from e

    @staticmethod
    def load_object(file_path: str) -> object:
        logging.info("Entered load_object method")

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, "rb") as file_obj:
                obj = pickle.load(file_obj)

            logging.info("Object loaded successfully")

            return obj

        except Exception as e:
            raise VisibilityException(e, sys) from e
