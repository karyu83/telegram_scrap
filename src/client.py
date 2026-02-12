from telethon import TelegramClient


SESSION_DIR = "session"


def create_client(config):
    session_path = f"{SESSION_DIR}/ticc_session"
    client = TelegramClient(
        session_path,
        config["api_id"],
        config["api_hash"],
    )
    return client
