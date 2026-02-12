import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock

import pytest

from src.batch_collector import collect_batch
from src.collector import handle_new_message
from src.media_downloader import download_media
from src.message_parser import parse_message
from src.storage import save_message


@pytest.mark.asyncio
async def test_pipeline_receive_parse_store(tmp_path):
    """수신 → 파싱 → 저장 전체 파이프라인 (모킹 없이 실제 모듈 연동)"""
    event = MagicMock()
    event.message.id = 5001
    event.message.text = "통합 테스트 메시지"
    event.message.date = datetime(2026, 2, 12, 10, 0, 0, tzinfo=timezone.utc)
    event.message.media = None
    event.message.chat_id = -1001234567890
    event.message.views = 42
    event.message.forwards = 3
    event.message.edit_date = None
    event.message.photo = None
    event.message.video = None
    event.message.document = None

    channel_map = {-1001234567890: "통합채널"}
    data_dir = str(tmp_path)

    # 실제 parse → save 파이프라인 실행 (collector가 내부에서 호출)
    chat_id = event.message.chat_id
    channel_alias = channel_map[chat_id]
    parsed = parse_message(event.message, channel_alias)
    save_message(parsed, channel_alias, data_dir=data_dir)

    # 검증: JSONL 파일이 생성되었는지
    jsonl_path = tmp_path / "통합채널" / "2026-02-12.jsonl"
    assert jsonl_path.exists()

    lines = jsonl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1

    saved = json.loads(lines[0])
    assert saved["message_id"] == 5001
    assert saved["text"] == "통합 테스트 메시지"
    assert saved["channel_alias"] == "통합채널"
    assert saved["has_media"] is False


@pytest.mark.asyncio
async def test_pipeline_with_media_download(tmp_path):
    """미디어 다운로드 포함 파이프라인: parse → download → save"""
    mock_client = MagicMock()
    mock_client.download_media = AsyncMock(return_value=str(tmp_path / "photo.jpg"))

    msg = MagicMock()
    msg.id = 5002
    msg.text = "사진 포함 메시지"
    msg.date = datetime(2026, 2, 12, 11, 0, 0, tzinfo=timezone.utc)
    msg.media = MagicMock()
    msg.photo = MagicMock()
    msg.video = None
    msg.document = None
    msg.chat_id = -1001234567890
    msg.views = 10
    msg.forwards = 0
    msg.edit_date = None
    msg.file = MagicMock()
    msg.file.size = 1024
    msg.file.name = "photo.jpg"

    channel_alias = "미디어채널"
    data_dir = str(tmp_path)

    # 1. Parse
    parsed = parse_message(msg, channel_alias)
    assert parsed["has_media"] is True
    assert parsed["media_type"] == "photo"

    # 2. Download media
    media_path = await download_media(mock_client, msg, channel_alias, data_dir=data_dir)
    assert media_path is not None

    # 3. Update parsed with media file path and save
    parsed["media_file"] = media_path
    save_message(parsed, channel_alias, data_dir=data_dir)

    # 검증
    jsonl_path = tmp_path / "미디어채널" / "2026-02-12.jsonl"
    assert jsonl_path.exists()

    saved = json.loads(jsonl_path.read_text(encoding="utf-8").strip())
    assert saved["message_id"] == 5002
    assert saved["has_media"] is True
    assert saved["media_file"] is not None


@pytest.mark.asyncio
async def test_batch_collection_pipeline(tmp_path):
    """배치 수집 전체 흐름: fetch → parse → save → metadata update"""
    msg1 = MagicMock()
    msg1.id = 6001
    msg1.text = "배치 메시지 1"
    msg1.date = datetime(2026, 2, 12, 8, 0, 0, tzinfo=timezone.utc)
    msg1.media = None
    msg1.chat_id = -1001234567890
    msg1.views = 10
    msg1.forwards = 0
    msg1.edit_date = None
    msg1.photo = None
    msg1.video = None
    msg1.document = None

    msg2 = MagicMock()
    msg2.id = 6002
    msg2.text = "배치 메시지 2"
    msg2.date = datetime(2026, 2, 12, 9, 0, 0, tzinfo=timezone.utc)
    msg2.media = None
    msg2.chat_id = -1001234567890
    msg2.views = 20
    msg2.forwards = 1
    msg2.edit_date = None
    msg2.photo = None
    msg2.video = None
    msg2.document = None

    mock_client = MagicMock()
    mock_client.get_messages = AsyncMock(return_value=[msg2, msg1])

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    metadata_path = str(tmp_path / "_metadata.json")
    channel_entity = MagicMock()

    count = await collect_batch(
        mock_client, channel_entity, "배치채널",
        metadata_path=metadata_path, data_dir=str(data_dir),
    )

    assert count == 2

    # JSONL 파일 검증
    jsonl_path = data_dir / "배치채널" / "2026-02-12.jsonl"
    assert jsonl_path.exists()
    lines = jsonl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2

    # 메타데이터 검증
    meta = json.loads(open(metadata_path, encoding="utf-8").read())
    assert meta["배치채널"]["last_message_id"] == 6002
    assert meta["배치채널"]["total_collected"] == 2


@pytest.mark.asyncio
async def test_duplicate_prevention_across_pipeline(tmp_path):
    """실시간 수신 후 배치 수집이 와도 중복 저장 안 됨"""
    msg = MagicMock()
    msg.id = 7001
    msg.text = "중복 방지 테스트"
    msg.date = datetime(2026, 2, 12, 12, 0, 0, tzinfo=timezone.utc)
    msg.media = None
    msg.chat_id = -1001234567890
    msg.views = 5
    msg.forwards = 0
    msg.edit_date = None
    msg.photo = None
    msg.video = None
    msg.document = None

    channel_alias = "중복채널"
    data_dir = str(tmp_path)

    # 1. 실시간 수신으로 먼저 저장
    parsed = parse_message(msg, channel_alias)
    save_message(parsed, channel_alias, data_dir=data_dir)

    # 2. 배치 수집으로 같은 메시지 다시 수집 시도
    mock_client = MagicMock()
    mock_client.get_messages = AsyncMock(return_value=[msg])

    metadata_path = str(tmp_path / "_metadata.json")
    channel_entity = MagicMock()

    await collect_batch(
        mock_client, channel_entity, channel_alias,
        metadata_path=metadata_path, data_dir=data_dir,
    )

    # 검증: 파일에 메시지가 1개만 있어야 함
    jsonl_path = tmp_path / channel_alias / "2026-02-12.jsonl"
    lines = jsonl_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1

    saved = json.loads(lines[0])
    assert saved["message_id"] == 7001
