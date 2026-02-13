import logging

from src.message_parser import parse_message
from src.storage import save_message

logger = logging.getLogger(__name__)


async def handle_new_message(event, channel_map, is_edit=False):
    chat_id = event.message.chat_id
    if chat_id not in channel_map:
        return

    channel_alias = channel_map[chat_id]
    parsed = parse_message(event.message, channel_alias, is_edit=is_edit)
    if parsed is None:
        return
    result = save_message(parsed, channel_alias)
    if result:
        logger.info("Message %s from %s saved", parsed["message_id"], channel_alias)
