# src/data_access/visibility_data.py

import sys
import os
from typing import List, Generator, Tuple

import numpy as np
import pandas as pd
import certifi
from pymongo.collection import Collection

from src.constant import MONGO_DATABASE_NAME
from src.configuration.mongo_db_connection import MongoDBClient
from src.exception import VisibilityException


class VisibilityData:
    """
    Handles exporting MongoDB collections as Pandas DataFrames
    """

    def __init__(self, database_name: str = MONGO_DATABASE_NAME):
        try:
            self.database_name = database_name

            mongo_url = os.getenv("MONGO_DB_URL")
            if not mongo_url:
                raise Exception("Environment variable MONGO_DB_URL is not set")

            # Use SINGLE Mongo client abstraction
            self.mongo_client = MongoDBClient(database_name=self.database_name)

        except Exception as e:
            raise VisibilityException(e, sys)

    # -----------------------------------------
    # COLLECTION LIST
    # -----------------------------------------

    def get_collection_names(self) -> List[str]:
        try:
            return self.mongo_client.database.list_collection_names()
        except Exception as e:
            raise VisibilityException(e, sys)

    # -----------------------------------------
    # COLLECTION → DATAFRAME
    # -----------------------------------------

    def get_collection_dataframe(self, collection_name: str) -> pd.DataFrame:
        try:
            collection: Collection = self.mongo_client.database[collection_name]
            records = list(collection.find())

            if not records:
                return pd.DataFrame()

            df = pd.DataFrame(records)

            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            df.replace({"na": np.nan}, inplace=True)
            return df

        except Exception as e:
            raise VisibilityException(e, sys)

    # -----------------------------------------
    # EXPORT ALL COLLECTIONS
    # -----------------------------------------

    def export_collections_as_dataframe(
        self,
    ) -> Generator[Tuple[str, pd.DataFrame], None, None]:
        """
        Yields:
            (collection_name, dataframe)
        """
        try:
            collections = self.get_collection_names()

            for collection_name in collections:
                df = self.get_collection_dataframe(collection_name)
                yield collection_name, df

        except Exception as e:
            raise VisibilityException(e, sys)
