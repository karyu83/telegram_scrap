import json
import logging
import os

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def generate_file_path(channel_alias, date_str, data_dir="data"):
    return os.path.join(data_dir, channel_alias, f"{date_str}.jsonl")


def _read_existing_message_ids(filepath):
    ids = set()
    if not os.path.exists(filepath):
        return ids
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    ids.add(obj.get("message_id"))
                except json.JSONDecodeError:
                    continue
    return ids


def save_message(msg, channel_alias, data_dir="data"):
    date_str = msg["date"][:10]
    filepath = generate_file_path(channel_alias, date_str, data_dir)

    dir_path = os.path.dirname(filepath)
    os.makedirs(dir_path, exist_ok=True)

    existing_ids = _read_existing_message_ids(filepath)
    if msg["message_id"] in existing_ids:
        return True

    line = json.dumps(msg, ensure_ascii=False) + "\n"

    for attempt in range(MAX_RETRIES):
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(line)
            return True
        except OSError as e:
            logger.error(f"Write failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")

    logger.error(f"Failed to write message {msg['message_id']} after {MAX_RETRIES} retries")
    return False
