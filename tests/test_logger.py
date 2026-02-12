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
