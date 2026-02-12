import os


_REQUIRED_KEYS = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_PHONE"]


def load_config():
    for key in _REQUIRED_KEYS:
        if key not in os.environ:
            raise ValueError(f"Required environment variable missing: {key}")

    return {
        "api_id": os.environ["TELEGRAM_API_ID"],
        "api_hash": os.environ["TELEGRAM_API_HASH"],
        "phone": os.environ["TELEGRAM_PHONE"],
        "download_media": os.environ.get("DOWNLOAD_MEDIA", "true").lower() == "true",
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        "data_dir": os.environ.get("DATA_DIR", "data"),
        "media_max_size_mb": int(os.environ.get("MEDIA_MAX_SIZE_MB", "50")),
        "batch_interval_sec": int(os.environ.get("BATCH_INTERVAL_SEC", "300")),
    }
