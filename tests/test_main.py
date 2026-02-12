import sys
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Mock telethon before importing main
sys.modules.setdefault("telethon", MagicMock())
sys.modules.setdefault("telethon.events", MagicMock())

from src.main import setup_handlers, run_client


def test_main_registers_event_handlers():
    mock_client = MagicMock()
    channel_map = {-1001234567890: "투자뉴스A"}

    setup_handlers(mock_client, channel_map)

    assert mock_client.on.call_count >= 2 or mock_client.add_event_handler.call_count >= 2


@pytest.mark.asyncio
async def test_main_connects_and_runs():
    mock_client = MagicMock()
    mock_client.start = AsyncMock()
    mock_client.run_until_disconnected = AsyncMock()

    await run_client(mock_client, phone="+821012345678")

    mock_client.start.assert_called_once_with(phone="+821012345678")
    mock_client.run_until_disconnected.assert_called_once()
