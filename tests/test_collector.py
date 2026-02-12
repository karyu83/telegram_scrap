from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from src.collector import handle_new_message


@pytest.mark.asyncio
async def test_handler_extracts_message_data():
    event = MagicMock()
    event.message = MagicMock()
    event.message.id = 100
    event.message.text = "테스트 메시지"
    event.message.date = datetime(2026, 2, 11, 9, 0, 0, tzinfo=timezone.utc)
    event.message.media = None
    event.message.chat_id = -1001234567890
    event.message.views = 50
    event.message.forwards = 3
    event.message.edit_date = None

    channel_map = {-1001234567890: "투자뉴스A"}

    with patch("src.collector.parse_message") as mock_parse, \
         patch("src.collector.save_message") as mock_save:
        mock_parse.return_value = {"message_id": 100, "text": "테스트 메시지"}
        mock_save.return_value = True

        await handle_new_message(event, channel_map)

        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        assert call_args[0][0] == event.message
        assert call_args[1].get("channel_alias") == "투자뉴스A" or call_args[0][1] == "투자뉴스A"


@pytest.mark.asyncio
async def test_ignores_unregistered_channel():
    event = MagicMock()
    event.message = MagicMock()
    event.message.chat_id = -9999999

    channel_map = {-1001234567890: "투자뉴스A"}

    with patch("src.collector.parse_message") as mock_parse, \
         patch("src.collector.save_message") as mock_save:
        await handle_new_message(event, channel_map)

        mock_parse.assert_not_called()
        mock_save.assert_not_called()


@pytest.mark.asyncio
async def test_handles_edited_message_event():
    event = MagicMock()
    event.message = MagicMock()
    event.message.id = 200
    event.message.text = "수정된 메시지"
    event.message.date = datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc)
    event.message.media = None
    event.message.chat_id = -1001234567890
    event.message.views = 80
    event.message.forwards = 2
    event.message.edit_date = datetime(2026, 2, 11, 11, 0, 0, tzinfo=timezone.utc)

    channel_map = {-1001234567890: "투자뉴스A"}

    with patch("src.collector.parse_message") as mock_parse, \
         patch("src.collector.save_message") as mock_save:
        mock_parse.return_value = {"message_id": 200, "is_edit": True}
        mock_save.return_value = True

        await handle_new_message(event, channel_map, is_edit=True)

        mock_parse.assert_called_once()
        call_kwargs = mock_parse.call_args
        assert call_kwargs[1].get("is_edit") is True or call_kwargs[0][2] is True


@pytest.mark.asyncio
async def test_routes_message_to_parse_and_store():
    event = MagicMock()
    event.message = MagicMock()
    event.message.id = 300
    event.message.text = "파이프라인 테스트"
    event.message.date = datetime(2026, 2, 11, 12, 0, 0, tzinfo=timezone.utc)
    event.message.media = None
    event.message.chat_id = -1001234567890
    event.message.views = 10
    event.message.forwards = 0
    event.message.edit_date = None

    channel_map = {-1001234567890: "투자뉴스A"}
    parsed_data = {"message_id": 300, "text": "파이프라인 테스트", "date": "2026-02-11T12:00:00+00:00"}

    with patch("src.collector.parse_message", return_value=parsed_data) as mock_parse, \
         patch("src.collector.save_message", return_value=True) as mock_save:
        await handle_new_message(event, channel_map)

        mock_parse.assert_called_once()
        mock_save.assert_called_once_with(parsed_data, "투자뉴스A")


@pytest.mark.asyncio
@pytest.mark.parametrize("text,media,expected_has_media", [
    ("텍스트만", None, False),
    (None, MagicMock(), True),
    ("캡션 텍스트", MagicMock(), True),
])
async def test_handles_text_media_and_caption_messages(text, media, expected_has_media):
    event = MagicMock()
    event.message = MagicMock()
    event.message.id = 400
    event.message.text = text
    event.message.date = datetime(2026, 2, 11, 14, 0, 0, tzinfo=timezone.utc)
    event.message.media = media
    event.message.chat_id = -1001234567890
    event.message.views = 5
    event.message.forwards = 0
    event.message.edit_date = None

    channel_map = {-1001234567890: "투자뉴스A"}
    parsed_data = {"message_id": 400, "has_media": expected_has_media}

    with patch("src.collector.parse_message", return_value=parsed_data) as mock_parse, \
         patch("src.collector.save_message", return_value=True) as mock_save:
        await handle_new_message(event, channel_map)

        mock_parse.assert_called_once()
        mock_save.assert_called_once()
