import subprocess
import os
from src.logger import logging


class B2Sync:
    """
    Backblaze B2 sync handler using rclone
    Assumes rclone is installed and configured with remote name 'backblaze'
    """

    def sync_folder_to_b2(self, folder: str, bucket_name: str):
        """
        Upload local folder to B2 bucket
        """
        try:
            logging.info(f"Uploading folder to B2: {folder}")
            cmd = ["rclone", "copy", folder, f"backblaze:{bucket_name}"]
            subprocess.run(cmd, check=True)
        except Exception as e:
            logging.error("B2 folder upload failed")
            raise e

    def sync_folder_from_b2(self, folder: str, bucket_name: str):
        """
        Download entire B2 bucket to local folder
        """
        try:
            logging.info(f"Downloading bucket from B2 to: {folder}")
            os.makedirs(folder, exist_ok=True)
            cmd = ["rclone", "copy", f"backblaze:{bucket_name}", folder]
            subprocess.run(cmd, check=True)
        except Exception as e:
            logging.error("B2 folder download failed")
            raise e

    def download_file(self, bucket_name: str, remote_file_path: str, local_file_path: str):
        """
        Download a single file from B2

        Example:
        remote_file_path = "prediction_model/model.pkl"
        local_file_path  = "artifacts/prediction_model/model.pkl"
        """
        try:
            logging.info(f"Downloading file from B2: {remote_file_path}")
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            cmd = [
                "rclone",
                "copy",
                f"backblaze:{bucket_name}/{remote_file_path}",
                os.path.dirname(local_file_path),
            ]
            subprocess.run(cmd, check=True)
        except Exception as e:
            logging.error("B2 file download failed")
            raise e
