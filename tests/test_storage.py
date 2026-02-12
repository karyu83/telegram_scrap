import json
import os
from unittest.mock import patch

from src.storage import generate_file_path, save_message


def test_generate_file_path():
    path = generate_file_path("투자뉴스A", "2026-02-11", data_dir="data")

    expected = os.path.join("data", "투자뉴스A", "2026-02-11.jsonl")
    assert path == expected


def test_creates_directory_if_not_exists(tmp_path):
    msg = {"message_id": 1, "date": "2026-02-11T09:00:00+00:00", "text": "hello"}

    save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))

    channel_dir = tmp_path / "test_ch"
    assert channel_dir.exists()


def test_writes_single_message_as_jsonl(tmp_path):
    msg = {"message_id": 1, "date": "2026-02-11T09:00:00+00:00", "text": "hello"}

    save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))

    filepath = tmp_path / "test_ch" / "2026-02-11.jsonl"
    lines = filepath.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["message_id"] == 1


def test_appends_to_existing_file(tmp_path):
    msg1 = {"message_id": 1, "date": "2026-02-11T09:00:00+00:00", "text": "first"}
    msg2 = {"message_id": 2, "date": "2026-02-11T09:00:00+00:00", "text": "second"}

    save_message(msg1, channel_alias="test_ch", data_dir=str(tmp_path))
    save_message(msg2, channel_alias="test_ch", data_dir=str(tmp_path))

    filepath = tmp_path / "test_ch" / "2026-02-11.jsonl"
    lines = filepath.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2


def test_preserves_korean_text_utf8(tmp_path):
    msg = {"message_id": 1, "date": "2026-02-11T09:00:00+00:00", "text": "삼성전자 매수"}

    save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))

    filepath = tmp_path / "test_ch" / "2026-02-11.jsonl"
    content = filepath.read_text(encoding="utf-8")
    assert "삼성전자 매수" in content
    assert "\\u" not in content  # ensure_ascii=False


def test_each_line_is_valid_json(tmp_path):
    for i in range(3):
        msg = {"message_id": i, "date": "2026-02-11T09:00:00+00:00", "text": f"msg {i}"}
        save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))

    filepath = tmp_path / "test_ch" / "2026-02-11.jsonl"
    lines = filepath.read_text(encoding="utf-8").strip().split("\n")
    for line in lines:
        parsed = json.loads(line)  # should not raise
        assert "message_id" in parsed


def test_skips_duplicate_message_id(tmp_path):
    msg = {"message_id": 99, "date": "2026-02-11T09:00:00+00:00", "text": "original"}
    dup = {"message_id": 99, "date": "2026-02-11T09:00:00+00:00", "text": "duplicate"}

    save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))
    save_message(dup, channel_alias="test_ch", data_dir=str(tmp_path))

    filepath = tmp_path / "test_ch" / "2026-02-11.jsonl"
    lines = filepath.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    assert json.loads(lines[0])["text"] == "original"


def test_retries_on_write_failure(tmp_path):
    msg = {"message_id": 1, "date": "2026-02-11T09:00:00+00:00", "text": "retry test"}
    call_count = 0

    original_open = open

    def flaky_open(*args, **kwargs):
        nonlocal call_count
        if args[1] == "a" if len(args) > 1 else kwargs.get("mode") == "a":
            call_count += 1
            if call_count < 3:
                raise OSError("disk full")
        return original_open(*args, **kwargs)

    with patch("builtins.open", side_effect=flaky_open):
        save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))

    filepath = tmp_path / "test_ch" / "2026-02-11.jsonl"
    assert filepath.exists()


def test_logs_error_after_max_retries(tmp_path):
    msg = {"message_id": 1, "date": "2026-02-11T09:00:00+00:00", "text": "fail test"}

    with patch("builtins.open", side_effect=OSError("disk full")):
        result = save_message(msg, channel_alias="test_ch", data_dir=str(tmp_path))

    assert result is False
