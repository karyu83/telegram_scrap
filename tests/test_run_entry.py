import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock telethon before importing runtime entry module.
sys.modules.setdefault("telethon", MagicMock())

from src.run import run_batch_mode, run_realtime_mode, main


@pytest.mark.asyncio
async def test_run_realtime_builds_channel_map_and_starts_client():
    config = {"phone": "+821012345678", "log_level": "INFO"}
    enabled_channels = [{"alias": "news_a", "username": "investnews_kr", "enabled": True}]
    resolved_channels = [{"alias": "news_a", "entity": MagicMock(id=-100123), "enabled": True}]
    client = MagicMock()

    with patch("src.run.load_dotenv"), \
         patch("src.run.load_config", return_value=config), \
         patch("src.run.configure_runtime_logging"), \
         patch("src.run.load_enabled_channels", return_value=enabled_channels), \
         patch("src.run.create_client", return_value=client), \
         patch("src.run.resolve_channels", new_callable=AsyncMock, return_value=resolved_channels), \
         patch("src.run.setup_handlers") as mock_setup_handlers, \
         patch("src.run.run_client", new_callable=AsyncMock) as mock_run_client:
        await run_realtime_mode(channels_path="channels.json")

    mock_setup_handlers.assert_called_once()
    args, _ = mock_setup_handlers.call_args
    assert args[0] is client
    assert args[1] == {-100123: "news_a"}
    mock_run_client.assert_awaited_once_with(client, phone="+821012345678")


@pytest.mark.asyncio
async def test_run_batch_uses_configured_interval_and_metadata_path():
    config = {
        "phone": "+821012345678",
        "log_level": "INFO",
        "data_dir": "data",
        "batch_interval_sec": 120,
    }
    client = MagicMock()
    enabled_channels = [{"alias": "news_a", "username": "investnews_kr", "enabled": True}]

    with patch("src.run.load_dotenv"), \
         patch("src.run.load_config", return_value=config), \
         patch("src.run.configure_runtime_logging"), \
         patch("src.run.load_enabled_channels", return_value=enabled_channels), \
         patch("src.run.create_client", return_value=client), \
         patch("src.run.start_client", new_callable=AsyncMock) as mock_start_client, \
         patch("src.run.run_periodic_batch", new_callable=AsyncMock) as mock_run_periodic_batch:
        await run_batch_mode(channels_path="channels.json", metadata_path="data/_metadata.json")

    mock_start_client.assert_awaited_once_with(client, phone="+821012345678")
    mock_run_periodic_batch.assert_awaited_once_with(
        client,
        enabled_channels,
        metadata_path="data/_metadata.json",
        data_dir="data",
        interval_sec=120,
    )


def test_run_main_supports_mode_and_channels_file_args():
    def _consume_coroutine(coro):
        coro.close()

    with patch("src.run.asyncio.run", side_effect=_consume_coroutine) as mock_asyncio_run:
        exit_code = main(
            [
                "--mode",
                "batch",
                "--channels-file",
                "channels.custom.json",
                "--metadata-path",
                "tmp/meta.json",
            ]
        )

    assert exit_code == 0
    assert mock_asyncio_run.call_count == 1
