import os
import subprocess


class RcloneSync:
    """
    Standalone utility class for syncing folders using rclone.exe
    Windows-specific (absolute path supported)
    """

    def __init__(self, rclone_path="rclone"):
        """
        rclone_path:
        - "rclone" if added to PATH
        - OR absolute path to rclone.exe
        """
        self.rclone_path = rclone_path

    def sync_folder_to_b2(self, folder: str, bucket_name: str, remote_name="backblaze"):
        """
        Upload local folder to Backblaze B2
        """
        cmd = [
            self.rclone_path,
            "sync",
            folder,
            f"{remote_name}:{bucket_name}"
        ]
        subprocess.run(cmd, check=True)

    def sync_folder_from_b2(self, folder: str, bucket_name: str, remote_name="backblaze"):
        """
        Download B2 bucket to local folder
        """
        os.makedirs(folder, exist_ok=True)
        cmd = [
            self.rclone_path,
            "sync",
            f"{remote_name}:{bucket_name}",
            folder
        ]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    syncer = RcloneSync()

    syncer.sync_folder_to_b2(
        "D:/climate/Climate-Visibility/data",
        "climate-data-storage"
    )

    syncer.sync_folder_from_b2(
        "D:/climate/Climate-Visibility/restore",
        "climate-data-storage"
    )
