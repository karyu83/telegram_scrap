import logging

from telethon import TelegramClient

logger = logging.getLogger(__name__)

SESSION_DIR = "session"


def create_client(config):
    session_path = f"{SESSION_DIR}/ticc_session"
    client = TelegramClient(
        session_path,
        config["api_id"],
        config["api_hash"],
    )
    return client


async def start_client(client, phone):
    await client.start(phone=phone)
    logger.info("Client started with phone authentication")
