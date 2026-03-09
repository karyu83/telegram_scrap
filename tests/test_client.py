import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

# Mock telethon before importing src.client
sys.modules.setdefault("telethon", MagicMock())

from src.client import create_client, start_client


def test_creates_client_with_correct_params():
    config = {
        "api_id": 12345,
        "api_hash": "test_hash_abc",
        "phone": "+821012345678",
    }

    with patch("src.client.TelegramClient") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance

        client = create_client(config)

        MockClient.assert_called_once()
        call_args = MockClient.call_args
        assert call_args[0][1] == 12345
        assert call_args[0][2] == "test_hash_abc"


def test_session_file_in_session_directory():
    config = {
        "api_id": 12345,
        "api_hash": "test_hash_abc",
        "phone": "+821012345678",
    }

    with patch("src.client.TelegramClient") as MockClient:
        MockClient.return_value = MagicMock()

        create_client(config)

        session_path = os.path.normpath(MockClient.call_args[0][0])
        assert os.path.dirname(session_path).endswith("session")


@pytest.mark.asyncio
async def test_first_run_starts_phone_auth_and_creates_session_file():
    mock_client = MagicMock()
    mock_client.start = AsyncMock()
    mock_client.is_user_authorized = AsyncMock(return_value=False)

    await start_client(mock_client, phone="+821012345678")

    mock_client.start.assert_called_once_with(phone="+821012345678")


@pytest.mark.asyncio
async def test_reuses_existing_session_without_reauth():
    mock_client = MagicMock()
    mock_client.start = AsyncMock()
    mock_client.is_user_authorized = AsyncMock(return_value=True)
    mock_client.get_me = AsyncMock(return_value=MagicMock(first_name="Test"))

    await start_client(mock_client, phone="+821012345678")

    mock_client.start.assert_called_once_with(phone="+821012345678")
