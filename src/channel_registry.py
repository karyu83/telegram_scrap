import json
import os


def _load_config(channels_path):
    if not os.path.exists(channels_path):
        return {"channels": []}

    with open(channels_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("channels config must be an object")
    channels = data.get("channels")
    if channels is None:
        data["channels"] = []
    elif not isinstance(channels, list):
        raise ValueError("channels must be a list")

    return data


def _save_config(channels_path, data):
    directory = os.path.dirname(channels_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(channels_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize_alias(alias):
    value = (alias or "").strip()
    if not value:
        raise ValueError("alias is required")
    return value


def _normalize_username(username):
    if username is None:
        return None
    value = username.strip()
    if value == "":
        return None
    return value


def add_channel(channels_path, alias, username=None, channel_id=None, enabled=True):
    alias = _normalize_alias(alias)
    username = _normalize_username(username)

    if username is None and channel_id is None:
        raise ValueError("username or id is required")

    config = _load_config(channels_path)
    channels = config["channels"]

    for existing in channels:
        if existing.get("alias") == alias:
            raise ValueError(f"duplicate alias: {alias}")
        if username is not None and existing.get("username") == username:
            raise ValueError(f"duplicate username: {username}")
        if channel_id is not None and existing.get("id") == channel_id:
            raise ValueError(f"duplicate id: {channel_id}")

    new_entry = {
        "alias": alias,
        "enabled": bool(enabled),
    }
    if username is not None:
        new_entry["username"] = username
    if channel_id is not None:
        new_entry["id"] = channel_id

    channels.append(new_entry)
    _save_config(channels_path, config)
    return new_entry


def load_channels_config(channels_path):
    return _load_config(channels_path)
