import sys
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.modules.setdefault("telethon", MagicMock())

from src.batch import run_batch, run_periodic_batch


@pytest.mark.asyncio
async def test_batch_entry_runs_collection():
    mock_client = MagicMock()
    mock_client.start = AsyncMock()
    mock_client.get_entity = AsyncMock(return_value=MagicMock())

    channels = [
        {"alias": "투자뉴스A", "username": "investnews_kr", "enabled": True},
    ]

    with patch("src.batch.collect_batch", new_callable=AsyncMock, return_value=5) as mock_collect:
        result = await run_batch(mock_client, channels, metadata_path="meta.json", data_dir="data")

        mock_collect.assert_called_once()
        assert result["투자뉴스A"] == 5


@pytest.mark.asyncio
async def test_batch_interval_uses_configurable_seconds():
    mock_client = MagicMock()
    mock_client.get_entity = AsyncMock(return_value=MagicMock())

    channels = [
        {"alias": "투자뉴스A", "username": "investnews_kr", "enabled": True},
    ]

    run_count = 0

    async def fake_sleep(seconds):
        nonlocal run_count
        assert seconds == 120  # 설정된 간격이 사용되는지 검증
        run_count += 1
        if run_count >= 2:
            raise KeyboardInterrupt  # 루프 탈출

    with patch("src.batch.collect_batch", new_callable=AsyncMock, return_value=1), \
         patch("src.batch.asyncio.sleep", side_effect=fake_sleep):
        try:
            await run_periodic_batch(
                mock_client, channels,
                metadata_path="meta.json", data_dir="data",
                interval_sec=120,
            )
        except KeyboardInterrupt:
            pass

    assert run_count >= 1
