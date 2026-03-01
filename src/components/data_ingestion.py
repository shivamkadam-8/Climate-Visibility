import sys
import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from dataclasses import dataclass

from src.constant import (
    MONGO_DATABASE_NAME,
    ARTIFACT_TIMESTAMP_DIR
)
from src.exception import VisibilityException
from src.logger import logging
from src.data_access.visibility_data import VisibilityData
from src.utils.main_utils import MainUtils


# ==========================================
# CONFIG
# ==========================================

@dataclass
class DataIngestionConfig:
    data_ingestion_dir: str = os.path.join(
        ARTIFACT_TIMESTAMP_DIR, "data_ingestion"
    )
    raw_data_dir: str = os.path.join(
        data_ingestion_dir, "raw"
    )


# ==========================================
# DATA INGESTION
# ==========================================

class DataIngestion:
    def __init__(self):
        try:
            self.config = DataIngestionConfig()
            self.utils = MainUtils()

            os.makedirs(self.config.raw_data_dir, exist_ok=True)

            logging.info(
                f"Data ingestion directory created at: {self.config.raw_data_dir}"
            )

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------

    @staticmethod
    def export_collection_as_dataframe(collection_name, db_name):
        try:
            mongo_client = MongoClient(os.getenv("MONGO_DB_URL"))
            collection = mongo_client[db_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            mongo_client.close()

            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------

    def export_data_into_raw_data_dir(self):
        try:
            logging.info("📥 Exporting data from MongoDB")

            visibility_data = VisibilityData(
                database_name=MONGO_DATABASE_NAME
            )

            for collection_name, dataset in visibility_data.export_collections_as_dataframe():
                logging.info(
                    f"{collection_name} data shape: {dataset.shape}"
                )

                file_path = os.path.join(
                    self.config.raw_data_dir,
                    f"{collection_name}.csv"
                )

                dataset.to_csv(file_path, index=False)

        except Exception as e:
            raise VisibilityException(e, sys)

    # ----------------------------------

    def initiate_data_ingestion(self) -> str:
        try:
            self.export_data_into_raw_data_dir()
            logging.info("✅ Data ingestion completed successfully")

            return self.config.raw_data_dir

        except Exception as e:
            raise VisibilityException(e, sys)
