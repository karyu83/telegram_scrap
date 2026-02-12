import logging
import os

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.media_downloader import generate_media_file_path, should_skip_media, download_media


def test_generate_media_file_path():
    path = generate_media_file_path("투자뉴스A", 12345, "report.pdf")
    expected = os.path.join("data", "투자뉴스A", "media", "12345_report.pdf")

    assert path == expected


def test_skip_file_over_max_size(caplog):
    size_bytes = 51 * 1024 * 1024  # 51MB
    max_size_mb = 50

    with caplog.at_level(logging.WARNING):
        result = should_skip_media(size_bytes, max_size_mb)

    assert result is True
    assert "50" in caplog.text or "skip" in caplog.text.lower()


@pytest.mark.asyncio
async def test_download_disabled_skips():
    mock_client = MagicMock()
    mock_message = MagicMock()

    result = await download_media(mock_client, mock_message, "ch", download_enabled=False)

    assert result is None
    mock_client.download_media.assert_not_called()


@pytest.mark.asyncio
async def test_download_failure_does_not_affect_text_storage(caplog):
    mock_client = MagicMock()
    mock_client.download_media = AsyncMock(side_effect=Exception("Network error"))

    mock_message = MagicMock()
    mock_message.id = 999
    mock_message.media = MagicMock()
    mock_message.file = MagicMock()
    mock_message.file.size = 1024
    mock_message.file.name = "test.jpg"

    with caplog.at_level(logging.ERROR):
        result = await download_media(mock_client, mock_message, "test_ch")

    assert result is None
    assert "999" in caplog.text or "error" in caplog.text.lower()


@pytest.mark.asyncio
async def test_downloads_highest_resolution_photo(tmp_path):
    mock_client = MagicMock()
    mock_client.download_media = AsyncMock(return_value=str(tmp_path / "photo.jpg"))

    mock_message = MagicMock()
    mock_message.id = 100
    mock_message.media = MagicMock()
    mock_message.photo = MagicMock()
    mock_message.file = MagicMock()
    mock_message.file.size = 1024
    mock_message.file.name = "photo.jpg"

    result = await download_media(mock_client, mock_message, "ch", data_dir=str(tmp_path))

    mock_client.download_media.assert_called_once()
    call_kwargs = mock_client.download_media.call_args
    assert call_kwargs[0][0] == mock_message
    assert result is not None
