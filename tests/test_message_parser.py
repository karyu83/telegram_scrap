from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.message_parser import parse_message


def test_parse_text_only_message(mock_message):
    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["message_id"] == 12345
    assert result["text"] == "테스트 메시지"
    assert result["has_media"] is False
    assert result["media_type"] is None


def test_parse_message_with_none_text(mock_message):
    mock_message.text = None

    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["text"] == ""


def test_parse_date_utc_iso8601(mock_message):
    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["date"] == "2026-02-11T09:00:00+00:00"


def test_parse_message_with_photo(mock_message):
    mock_message.media = MagicMock()
    mock_message.media.__class__.__name__ = "MessageMediaPhoto"
    mock_message.photo = MagicMock()
    mock_message.document = None
    mock_message.video = None

    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["has_media"] is True
    assert result["media_type"] == "photo"


def test_parse_message_with_document(mock_message):
    mock_message.media = MagicMock()
    mock_message.photo = None
    mock_message.document = MagicMock()
    mock_message.document.mime_type = "application/pdf"
    mock_message.video = None

    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["has_media"] is True
    assert result["media_type"] == "document"


def test_parse_message_with_video(mock_message):
    mock_message.media = MagicMock()
    mock_message.photo = None
    mock_message.document = None
    mock_message.video = MagicMock()

    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["has_media"] is True
    assert result["media_type"] == "video"


def test_parse_message_with_caption(mock_message):
    mock_message.text = "사진 캡션입니다"
    mock_message.media = MagicMock()
    mock_message.photo = MagicMock()
    mock_message.document = None
    mock_message.video = None

    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["text"] == "사진 캡션입니다"
    assert result["has_media"] is True


def test_parse_message_views_and_forwards(mock_message):
    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["views"] == 100
    assert result["forwards"] == 5


def test_parse_edited_message(mock_message):
    mock_message.edit_date = datetime(2026, 2, 11, 10, 30, 0, tzinfo=timezone.utc)

    result = parse_message(mock_message, channel_alias="투자뉴스A", is_edit=True)

    assert result["is_edit"] is True
    assert result["edit_date"] == "2026-02-11T10:30:00+00:00"


def test_parse_message_collected_at_set(mock_message):
    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert "collected_at" in result
    # collected_at should be a valid ISO8601 string
    datetime.fromisoformat(result["collected_at"])


def test_parse_korean_text(mock_message):
    mock_message.text = "삼성전자 목표가 상향 조정 🚀 매수 추천"

    result = parse_message(mock_message, channel_alias="투자뉴스A")

    assert result["text"] == "삼성전자 목표가 상향 조정 🚀 매수 추천"
