import logging

from telethon import events

from src.collector import handle_new_message

logger = logging.getLogger(__name__)


def setup_handlers(client, channel_map):
    @client.on(events.NewMessage)
    async def new_message_handler(event):
        await handle_new_message(event, channel_map)

    @client.on(events.MessageEdited)
    async def edited_message_handler(event):
        await handle_new_message(event, channel_map, is_edit=True)


async def run_client(client, phone):
    await client.start(phone=phone)
    logger.info("Client connected, listening for messages...")
    await client.run_until_disconnected()
