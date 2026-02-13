import logging

from src.reconnect import calculate_backoff, ReconnectManager, extract_flood_wait_seconds


def test_exponential_backoff_sequence():
    assert calculate_backoff(0) == 30
    assert calculate_backoff(1) == 60
    assert calculate_backoff(2) == 120
    assert calculate_backoff(3) == 240
    assert calculate_backoff(4) == 300


def test_backoff_max_cap_300():
    assert calculate_backoff(5) == 300
    assert calculate_backoff(10) == 300
    assert calculate_backoff(100) == 300


def test_backoff_resets_on_success():
    manager = ReconnectManager()

    manager.record_failure()
    manager.record_failure()
    assert manager.attempt == 2

    manager.record_success()
    assert manager.attempt == 0
    assert manager.get_delay() == 30


def test_flood_wait_error_extracts_seconds():
    from unittest.mock import MagicMock

    error = MagicMock()
    error.seconds = 45

    wait_time = extract_flood_wait_seconds(error)
    assert wait_time == 45


def test_reconnect_triggers_batch_collection():
    from unittest.mock import MagicMock

    batch_callback = MagicMock()
    manager = ReconnectManager(on_reconnect=batch_callback)

    manager.record_success()

    batch_callback.assert_called_once()


def test_disconnect_waits_30_seconds_before_retry():
    manager = ReconnectManager()

    # 첫 실패: attempt=0일 때 대기시간은 30초
    delay = manager.get_delay()
    assert delay == 30

    manager.record_failure()
    # 두번째: attempt=1일 때 60초
    assert manager.get_delay() == 60


def test_connection_state_changes_are_logged(caplog):
    manager = ReconnectManager()

    with caplog.at_level(logging.INFO):
        manager.record_failure()
        manager.record_success()

    log_text = caplog.text.lower()
    assert "disconnect" in log_text or "fail" in log_text
    assert "reconnect" in log_text or "success" in log_text or "connected" in log_text
