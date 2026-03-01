# src/constant/__init__.py
from datetime import datetime
import os

# ------------------------
# GLOBAL PATHS
# ------------------------
ARTIFACTS_DIR = "artifacts"

TIMESTAMP = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
ARTIFACT_TIMESTAMP_DIR = os.path.join(ARTIFACTS_DIR, TIMESTAMP)

# ------------------------
# DATABASE
# ------------------------
MONGO_DATABASE_NAME = "visibility"

# ------------------------
# MODEL
# ------------------------
TARGET_COLUMN = "VISIBILITY"

MODEL_DIR = os.path.join(ARTIFACTS_DIR, "prediction_model")
MODEL_FILE_NAME = "model.pkl"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE_NAME)

# ------------------------
# FEATURES (VERY IMPORTANT)
# ------------------------
FEATURE_COLUMNS = [
    "DRYBULBTEMPF",
    "RelativeHumidity",
    "WindSpeed",
    "WindDirection",
    "SeaLevelPressure",
]
