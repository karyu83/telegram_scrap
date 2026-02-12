import pytest

from src.config import load_config


def test_load_config_reads_api_id(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "test_hash")
    monkeypatch.setenv("TELEGRAM_PHONE", "+821012345678")

    config = load_config()

    assert config["api_id"] == "12345"


def test_load_config_reads_api_hash(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "abcdef123456")
    monkeypatch.setenv("TELEGRAM_PHONE", "+821012345678")

    config = load_config()

    assert config["api_hash"] == "abcdef123456"


def test_load_config_reads_phone(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "test_hash")
    monkeypatch.setenv("TELEGRAM_PHONE", "+821099998888")

    config = load_config()

    assert config["phone"] == "+821099998888"


def test_load_config_raises_on_missing_required(monkeypatch):
    monkeypatch.delenv("TELEGRAM_API_ID", raising=False)
    monkeypatch.delenv("TELEGRAM_API_HASH", raising=False)
    monkeypatch.delenv("TELEGRAM_PHONE", raising=False)

    with pytest.raises(ValueError, match="TELEGRAM_API_ID"):
        load_config()


def test_load_config_reads_optional_with_defaults(monkeypatch):
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "test_hash")
    monkeypatch.setenv("TELEGRAM_PHONE", "+821012345678")
    monkeypatch.delenv("DOWNLOAD_MEDIA", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.delenv("MEDIA_MAX_SIZE_MB", raising=False)
    monkeypatch.delenv("BATCH_INTERVAL_SEC", raising=False)

    config = load_config()

    assert config["download_media"] is True
    assert config["log_level"] == "INFO"
    assert config["data_dir"] == "data"
    assert config["media_max_size_mb"] == 50
    assert config["batch_interval_sec"] == 300
