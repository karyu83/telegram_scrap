from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_message():
    """Telethon Message 객체 모킹"""
    msg = MagicMock()
    msg.id = 12345
    msg.text = "테스트 메시지"
    msg.date = datetime(2026, 2, 11, 9, 0, 0, tzinfo=timezone.utc)
    msg.media = None
    msg.views = 100
    msg.forwards = 5
    msg.edit_date = None
    msg.chat_id = -1001234567890
    return msg


@pytest.fixture
def mock_channel():
    """Telethon Channel 엔티티 모킹"""
    ch = MagicMock()
    ch.id = -1001234567890
    ch.username = "investnews_kr"
    ch.title = "투자뉴스A"
    return ch


@pytest.fixture
def sample_channel_config():
    """채널 설정 샘플"""
    return {
        "channels": [
            {
                "alias": "투자뉴스A",
                "username": "investnews_kr",
                "enabled": True,
            },
            {
                "alias": "해외주식속보",
                "id": -1001234567890,
                "enabled": True,
            },
            {
                "alias": "비활성채널",
                "username": "disabled_ch",
                "enabled": False,
            },
        ]
    }
