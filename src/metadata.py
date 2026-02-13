import json
import os
import threading

_lock = threading.Lock()


def load_metadata(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}


def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_channel(filepath, channel_alias, **kwargs):
    with _lock:
        data = load_metadata(filepath)
        if channel_alias not in data:
            data[channel_alias] = {}
        data[channel_alias].update(kwargs)
        save_metadata(filepath, data)


def increment_collected(filepath, channel_alias):
    with _lock:
        data = load_metadata(filepath)
        if channel_alias not in data:
            data[channel_alias] = {}
        data[channel_alias]["total_collected"] = data[channel_alias].get("total_collected", 0) + 1
        save_metadata(filepath, data)
