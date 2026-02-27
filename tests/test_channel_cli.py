import json
from pathlib import Path
from uuid import uuid4

from src.channel_cli import main


def test_channel_cli_add_command_updates_file():
    tmp_dir = Path("tests") / ".tmp" / f"channel_cli_{uuid4().hex}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    channels_path = tmp_dir / "channels.json"

    exit_code = main(
        [
            "add",
            "--channels-file",
            str(channels_path),
            "--alias",
            "news_a",
            "--username",
            "investnews_kr",
        ]
    )

    assert exit_code == 0
    saved = json.loads(channels_path.read_text(encoding="utf-8"))
    assert saved["channels"][0]["alias"] == "news_a"
    assert saved["channels"][0]["username"] == "investnews_kr"
