import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.channel_manager import parse_channels, filter_enabled_channels, resolve_channels


def test_parse_channels_from_json(sample_channel_config):
    channels = parse_channels(sample_channel_config)

    assert len(channels) > 0
    assert channels[0]["alias"] == "투자뉴스A"
    assert channels[0]["username"] == "investnews_kr"


def test_filter_enabled_channels_only(sample_channel_config):
    channels = parse_channels(sample_channel_config)
    enabled = filter_enabled_channels(channels)

    assert len(enabled) == 2
    for ch in enabled:
        assert ch["enabled"] is True
    aliases = [ch["alias"] for ch in enabled]
    assert "비활성채널" not in aliases


def test_channel_identified_by_username(sample_channel_config):
    channels = parse_channels(sample_channel_config)
    public_ch = channels[0]

    assert "username" in public_ch
    assert public_ch["username"] == "investnews_kr"
    assert "id" not in public_ch


def test_channel_identified_by_id(sample_channel_config):
    channels = parse_channels(sample_channel_config)
    private_ch = channels[1]

    assert "id" in private_ch
    assert private_ch["id"] == -1001234567890
    assert "username" not in private_ch


def test_channel_alias_assigned(sample_channel_config):
    channels = parse_channels(sample_channel_config)

    assert channels[0]["alias"] == "투자뉴스A"
    assert channels[1]["alias"] == "해외주식속보"
    assert channels[2]["alias"] == "비활성채널"


@pytest.mark.asyncio
async def test_resolve_failure_logs_error_continues(caplog):
    channels = [
        {"alias": "정상채널", "username": "good_channel", "enabled": True},
        {"alias": "실패채널", "username": "bad_channel", "enabled": True},
    ]

    mock_client = MagicMock()

    good_entity = MagicMock()
    good_entity.id = 111

    async def fake_get_entity(identifier):
        if identifier == "good_channel":
            return good_entity
        raise ValueError("Cannot find entity")

    mock_client.get_entity = AsyncMock(side_effect=fake_get_entity)

    with caplog.at_level(logging.ERROR):
        resolved = await resolve_channels(mock_client, channels)

    assert len(resolved) == 1
    assert resolved[0]["alias"] == "정상채널"
    assert "bad_channel" in caplog.text
