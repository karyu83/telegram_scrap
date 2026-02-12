import sys
from unittest.mock import patch, MagicMock

# Mock telethon before importing src.client
sys.modules.setdefault("telethon", MagicMock())

from src.client import create_client


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

        session_path = MockClient.call_args[0][0]
        assert session_path.startswith("session/")
