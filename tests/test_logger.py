import logging
import re
from datetime import datetime

from src.logger import setup_logger


def test_log_format_matches_spec(tmp_path):
    log_dir = tmp_path / "logs"
    logger = setup_logger("test_module", log_dir=str(log_dir))
    logger.info("hello world")

    log_files = list(log_dir.iterdir())
    assert len(log_files) == 1

    content = log_files[0].read_text(encoding="utf-8")
    pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \[INFO\] \[test_module\] hello world"
    assert re.search(pattern, content)


def test_log_file_daily_rotation_name(tmp_path):
    log_dir = tmp_path / "logs"
    setup_logger("rotation_test", log_dir=str(log_dir))

    today = datetime.now().strftime("%Y-%m-%d")
    expected_file = log_dir / f"collector_{today}.log"
    assert expected_file.exists()


def test_logger_outputs_to_console_and_file(tmp_path):
    log_dir = tmp_path / "logs"
    logger = setup_logger("console_test", log_dir=str(log_dir))

    handler_types = [type(h) for h in logger.handlers]
    assert logging.FileHandler in handler_types
    assert logging.StreamHandler in handler_types


def test_message_receive_and_store_logged_info(tmp_path, caplog):
    """메시지 수신/저장 시 INFO 레벨로 로깅되는지 검증 (collector 모듈)"""
    from datetime import timezone
    from unittest.mock import MagicMock, patch

    from src.collector import handle_new_message
    import asyncio

    event = MagicMock()
    event.message.id = 8001
    event.message.text = "로그 테스트"
    event.message.date = datetime(2026, 2, 12, 10, 0, 0, tzinfo=timezone.utc)
    event.message.media = None
    event.message.chat_id = -1001234567890
    event.message.views = 1
    event.message.forwards = 0
    event.message.edit_date = None
    event.message.photo = None
    event.message.video = None
    event.message.document = None

    channel_map = {-1001234567890: "로그채널"}

    with caplog.at_level(logging.INFO), \
         patch("src.collector.save_message", return_value=True):
        asyncio.run(handle_new_message(event, channel_map))

    assert any(
        record.levelno == logging.INFO and "8001" in record.message
        for record in caplog.records
    )


def test_errors_include_traceback(tmp_path, caplog):
    """에러 로그에 traceback이 포함되는지 검증"""
    log_dir = tmp_path / "logs"
    logger = setup_logger("traceback_test", log_dir=str(log_dir))

    try:
        raise ValueError("test error for traceback")
    except ValueError:
        logger.error("Something went wrong", exc_info=True)

    log_file = list(log_dir.iterdir())[0]
    content = log_file.read_text(encoding="utf-8")

    assert "Traceback" in content
    assert "ValueError" in content
    assert "test error for traceback" in content
