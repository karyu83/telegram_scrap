from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from src.batch_collector import get_last_message_id, fetch_messages, collect_batch


def test_reads_last_message_id_from_metadata(tmp_path):
    import json
    metadata_path = tmp_path / "_metadata.json"
    metadata = {
        "투자뉴스A": {
            "last_message_id": 45232,
            "last_collected_at": "2026-02-11T18:15:01.654321",
            "total_collected": 1523,
        }
    }
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    result = get_last_message_id(str(metadata_path), "투자뉴스A")
    assert result == 45232


def test_reads_last_message_id_returns_zero_when_missing(tmp_path):
    import json
    metadata_path = tmp_path / "_metadata.json"
    metadata_path.write_text("{}", encoding="utf-8")

    result = get_last_message_id(str(metadata_path), "unknown_channel")
    assert result == 0


@pytest.mark.asyncio
async def test_builds_query_with_min_id():
    mock_client = MagicMock()
    mock_client.get_messages = AsyncMock(return_value=[])

    channel_entity = MagicMock()
    min_id = 1000

    await fetch_messages(mock_client, channel_entity, min_id=min_id)

    mock_client.get_messages.assert_called_once()
    call_kwargs = mock_client.get_messages.call_args[1]
    assert call_kwargs["min_id"] == 1000


@pytest.mark.asyncio
async def test_limits_to_100_messages():
    mock_client = MagicMock()
    mock_client.get_messages = AsyncMock(return_value=[])

    channel_entity = MagicMock()

    await fetch_messages(mock_client, channel_entity, min_id=0)

    call_kwargs = mock_client.get_messages.call_args[1]
    assert call_kwargs["limit"] == 100


@pytest.mark.asyncio
async def test_skips_already_stored_messages(tmp_path):
    from datetime import datetime, timezone
    import json

    # Setup: existing message in storage
    channel_alias = "투자뉴스A"
    data_dir = tmp_path / "data"
    channel_dir = data_dir / channel_alias
    channel_dir.mkdir(parents=True)
    existing_file = channel_dir / "2026-02-11.jsonl"
    existing_msg = {"message_id": 100, "date": "2026-02-11T09:00:00+00:00"}
    existing_file.write_text(json.dumps(existing_msg) + "\n", encoding="utf-8")

    # Mock messages: one already stored (100), one new (101)
    msg_existing = MagicMock()
    msg_existing.id = 100
    msg_existing.text = "이미 저장된 메시지"
    msg_existing.date = datetime(2026, 2, 11, 9, 0, 0, tzinfo=timezone.utc)
    msg_existing.media = None
    msg_existing.chat_id = -1001234567890
    msg_existing.views = 10
    msg_existing.forwards = 0
    msg_existing.edit_date = None

    msg_new = MagicMock()
    msg_new.id = 101
    msg_new.text = "새 메시지"
    msg_new.date = datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc)
    msg_new.media = None
    msg_new.chat_id = -1001234567890
    msg_new.views = 20
    msg_new.forwards = 1
    msg_new.edit_date = None

    mock_client = MagicMock()
    mock_client.get_messages = AsyncMock(return_value=[msg_new, msg_existing])

    metadata_path = str(tmp_path / "_metadata.json")
    channel_entity = MagicMock()

    count = await collect_batch(
        mock_client, channel_entity, channel_alias,
        metadata_path=metadata_path, data_dir=str(data_dir),
    )

    # Read file and count lines
    lines = existing_file.read_text(encoding="utf-8").strip().split("\n")
    message_ids = [json.loads(line)["message_id"] for line in lines]

    assert 101 in message_ids
    # message 100 should not be duplicated
    assert message_ids.count(100) == 1


@pytest.mark.asyncio
async def test_updates_metadata_after_collection(tmp_path):
    from datetime import datetime, timezone
    import json

    channel_alias = "투자뉴스A"
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    msg = MagicMock()
    msg.id = 500
    msg.text = "배치 수집 메시지"
    msg.date = datetime(2026, 2, 12, 8, 0, 0, tzinfo=timezone.utc)
    msg.media = None
    msg.chat_id = -1001234567890
    msg.views = 30
    msg.forwards = 2
    msg.edit_date = None

    mock_client = MagicMock()
    mock_client.get_messages = AsyncMock(return_value=[msg])

    metadata_path = str(tmp_path / "_metadata.json")
    channel_entity = MagicMock()

    await collect_batch(
        mock_client, channel_entity, channel_alias,
        metadata_path=metadata_path, data_dir=str(data_dir),
    )

    metadata = json.loads(open(metadata_path, encoding="utf-8").read())
    assert channel_alias in metadata
    assert metadata[channel_alias]["last_message_id"] == 500
    assert "last_collected_at" in metadata[channel_alias]
    assert metadata[channel_alias]["total_collected"] >= 1
