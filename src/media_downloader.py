import logging
import os

logger = logging.getLogger(__name__)


def generate_media_file_path(channel_alias, message_id, filename, data_dir="data"):
    return os.path.join(data_dir, channel_alias, "media", f"{message_id}_{filename}")


def should_skip_media(size_bytes, max_size_mb):
    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        logger.warning("Media file size %d bytes exceeds max %dMB, skip", size_bytes, max_size_mb)
        return True
    return False


async def download_media(client, message, channel_alias, download_enabled=True, max_size_mb=50, data_dir="data"):
    if not download_enabled:
        return None

    if not message.media:
        return None

    file_size = getattr(getattr(message, "file", None), "size", None) or 0
    if should_skip_media(file_size, max_size_mb):
        return None

    filename = getattr(getattr(message, "file", None), "name", None) or f"{message.id}"
    file_path = generate_media_file_path(channel_alias, message.id, filename, data_dir)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        await client.download_media(message, file=file_path)
        return file_path
    except Exception as e:
        logger.error("Failed to download media for message %s: %s", message.id, e)
        return None
