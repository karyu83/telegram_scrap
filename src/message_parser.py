import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _detect_media_type(message):
    if message.media is None:
        return None
    if getattr(message, "photo", None) is not None:
        return "photo"
    if getattr(message, "video", None) is not None:
        return "video"
    if getattr(message, "document", None) is not None:
        return "document"
    return None


def parse_message(message, channel_alias="", is_edit=False):
    try:
        edit_date = getattr(message, "edit_date", None)

        return {
            "message_id": message.id,
            "channel_id": message.chat_id,
            "channel_alias": channel_alias,
            "date": message.date.isoformat(),
            "text": message.text or "",
            "has_media": message.media is not None,
            "media_type": _detect_media_type(message),
            "media_file": None,
            "views": getattr(message, "views", None),
            "forwards": getattr(message, "forwards", None),
            "edit_date": edit_date.isoformat() if edit_date else None,
            "is_edit": is_edit,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        msg_id = getattr(message, "id", "unknown")
        logger.error("Failed to parse message %s: %s", msg_id, e)
        return None
