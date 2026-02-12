import logging

logger = logging.getLogger(__name__)


def parse_channels(config):
    return config.get("channels", [])


def filter_enabled_channels(channels):
    return [ch for ch in channels if ch.get("enabled", False)]


async def resolve_channels(client, channels):
    resolved = []
    for ch in channels:
        identifier = ch.get("username") or ch.get("id")
        try:
            entity = await client.get_entity(identifier)
            ch["entity"] = entity
            resolved.append(ch)
        except Exception as e:
            logger.error("Failed to resolve channel %s: %s", identifier, e)
    return resolved
