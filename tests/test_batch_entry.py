import sys
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.modules.setdefault("telethon", MagicMock())

from src.batch import run_batch


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
