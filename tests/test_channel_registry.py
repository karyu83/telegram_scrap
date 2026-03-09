import json
from pathlib import Path
from uuid import uuid4

import pytest

from src.channel_registry import add_channel, list_channels, remove_channel, set_channel_enabled


def _make_workspace_tmp_dir():
    base = Path("tests") / ".tmp" / f"channel_registry_{uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    return base


def test_add_channel_creates_channels_file_and_appends_entry():
    tmp_dir = _make_workspace_tmp_dir()
    channels_path = tmp_dir / "channels.json"

    entry = add_channel(
        channels_path=str(channels_path),
        alias="news_a",
        username="investnews_kr",
        enabled=True,
    )

    assert channels_path.exists()
    saved = json.loads(channels_path.read_text(encoding="utf-8"))
    assert len(saved["channels"]) == 1
    assert saved["channels"][0]["alias"] == "news_a"
    assert saved["channels"][0]["username"] == "investnews_kr"
    assert saved["channels"][0]["enabled"] is True
    assert entry["alias"] == "news_a"


def test_add_channel_rejects_duplicate_alias():
    tmp_dir = _make_workspace_tmp_dir()
    channels_path = tmp_dir / "channels.json"
    channels_path.write_text(
        json.dumps(
            {
                "channels": [
                    {"alias": "news_a", "username": "first_news", "enabled": True},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="alias"):
        add_channel(
            channels_path=str(channels_path),
            alias="news_a",
            username="second_news",
            enabled=True,
        )


def test_add_channel_rejects_duplicate_username_or_id():
    tmp_dir = _make_workspace_tmp_dir()
    channels_path = tmp_dir / "channels.json"
    channels_path.write_text(
        json.dumps(
            {
                "channels": [
                    {"alias": "news_a", "username": "investnews_kr", "enabled": True},
                    {"alias": "news_b", "id": -100111222333, "enabled": True},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="username"):
        add_channel(
            channels_path=str(channels_path),
            alias="news_c",
            username="investnews_kr",
            enabled=True,
        )

    with pytest.raises(ValueError, match="id"):
        add_channel(
            channels_path=str(channels_path),
            alias="news_d",
            channel_id=-100111222333,
            enabled=True,
        )


def test_list_enable_disable_remove_channel():
    tmp_dir = _make_workspace_tmp_dir()
    channels_path = tmp_dir / "channels.json"

    add_channel(str(channels_path), alias="news_a", username="investnews_kr", enabled=True)

    listed = list_channels(str(channels_path))
    assert len(listed) == 1
    assert listed[0]["enabled"] is True

    updated = set_channel_enabled(str(channels_path), alias="news_a", enabled=False)
    assert updated["enabled"] is False

    removed = remove_channel(str(channels_path), alias="news_a")
    assert removed["alias"] == "news_a"
    assert list_channels(str(channels_path)) == []
