import logging

from src.metadata import load_metadata, update_channel, increment_collected
from src.message_parser import parse_message
from src.storage import save_message

logger = logging.getLogger(__name__)


def get_last_message_id(metadata_path, channel_alias):
    data = load_metadata(metadata_path)
    channel_data = data.get(channel_alias, {})
    return channel_data.get("last_message_id", 0)


MAX_MESSAGES = 100


async def fetch_messages(client, channel_entity, min_id=0):
    messages = await client.get_messages(
        channel_entity,
        limit=MAX_MESSAGES,
        min_id=min_id,
    )
    return messages


async def collect_batch(client, channel_entity, channel_alias, metadata_path, data_dir="data"):
    min_id = get_last_message_id(metadata_path, channel_alias)
    messages = await fetch_messages(client, channel_entity, min_id=min_id)

    saved_count = 0
    max_msg_id = min_id

    for msg in messages:
        parsed = parse_message(msg, channel_alias)
        result = save_message(parsed, channel_alias, data_dir=data_dir)
        if result:
            saved_count += 1
            if msg.id > max_msg_id:
                max_msg_id = msg.id

    if max_msg_id > min_id:
        from datetime import datetime, timezone
        update_channel(
            metadata_path, channel_alias,
            last_message_id=max_msg_id,
            last_collected_at=datetime.now(timezone.utc).isoformat(),
        )
        for _ in range(saved_count):
            increment_collected(metadata_path, channel_alias)

    return saved_count
