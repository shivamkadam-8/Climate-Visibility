import boto3
import os
import sys

from src.exception import VisibilityException
from src.logger import logging


class B2Client:
    """
    Backblaze B2 client using S3-compatible API (boto3)
    """

    def __init__(self):
        try:
            self.endpoint_url = "https://s3.us-west-002.backblazeb2.com"
            self.region_name = "us-west-002"

            self.access_key_id = os.getenv("B2_ACCOUNT_ID")
            self.secret_access_key = os.getenv("B2_ACCOUNT_KEY")

            if not self.access_key_id:
                raise Exception("Environment variable B2_ACCOUNT_ID is not set")

            if not self.secret_access_key:
                raise Exception("Environment variable B2_ACCOUNT_KEY is not set")

            self.s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region_name,
            )

            logging.info("Backblaze B2 client initialized successfully")

        except Exception as e:
            raise VisibilityException(e, sys)

    # --------------------------------------------------
    # Upload file
    # --------------------------------------------------
    def upload_file(self, bucket_name: str, local_path: str, b2_path: str):
        try:
            self.s3_client.upload_file(local_path, bucket_name, b2_path)
            logging.info(f"Uploaded file to B2: {b2_path}")
        except Exception as e:
            raise VisibilityException(e, sys)

    # --------------------------------------------------
    # Download file
    # --------------------------------------------------
    def download_file(self, bucket_name: str, b2_path: str, local_path: str):
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            self.s3_client.download_file(bucket_name, b2_path, local_path)
            logging.info(f"Downloaded file from B2: {b2_path}")
        except Exception as e:
            raise VisibilityException(e, sys)
