import os


def set_google_credentials():
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    WAREHOUSE_NAME = os.getenv("WAREHOUSE_NAME")
    LOCATION = os.getenv("LOCATION")
    if not GOOGLE_CLOUD_PROJECT:
        raise ValueError("GOOGLE_CLOUD_PROJECT credentials were not provided in .env file.")
    if not BUCKET_NAME:
        raise ValueError("BUCKET_URI was not provided in .env file.")
    if not WAREHOUSE_NAME:
        raise ValueError("WAREHOUSE_NAME was not provided in .env file.")
    if not LOCATION:
        raise ValueError("LOCATION was not provided in .env file.")

