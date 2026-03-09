import logging
import os

from telethon import TelegramClient

logger = logging.getLogger(__name__)


def create_client(config, session_dir="session"):
    os.makedirs(session_dir, exist_ok=True)
    session_path = os.path.join(session_dir, "ticc_session")
    client = TelegramClient(
        session_path,
        config["api_id"],
        config["api_hash"],
    )
    return client


async def start_client(client, phone):
    await client.start(phone=phone)
    logger.info("Client started with phone authentication")
