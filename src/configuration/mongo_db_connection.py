import os
import sys
import certifi
import pymongo

from src.constant import MONGO_DATABASE_NAME
from src.exception import VisibilityException
from src.logger import logging


class MongoDBClient:
    """
    Singleton MongoDB client
    """

    _client = None

    def __init__(self, database_name=MONGO_DATABASE_NAME):
        try:
            if MongoDBClient._client is None:
                mongo_db_url = os.getenv("MONGO_DB_URL")

                if not mongo_db_url:
                    raise Exception("Environment variable MONGO_DB_URL is not set")

                MongoDBClient._client = pymongo.MongoClient(
                    mongo_db_url,
                    tlsCAFile=certifi.where()
                )

                logging.info("MongoDB connection established")

            self.client = MongoDBClient._client
            self.database = self.client[database_name]
            self.database_name = database_name

        except Exception as e:
            raise VisibilityException(e, sys)
