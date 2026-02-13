from src.metadata import increment_collected, load_metadata, save_metadata, update_channel


def test_load_returns_empty_when_file_missing(tmp_path):
    filepath = tmp_path / "_metadata.json"

    result = load_metadata(str(filepath))

    assert result == {}


def test_save_writes_metadata_to_file(tmp_path):
    filepath = tmp_path / "_metadata.json"
    data = {"test_channel": {"last_message_id": 100}}

    save_metadata(str(filepath), data)

    assert filepath.exists()
    import json
    content = json.loads(filepath.read_text(encoding="utf-8"))
    assert content == data


def test_load_reads_saved_metadata(tmp_path):
    filepath = tmp_path / "_metadata.json"
    data = {
        "investnews_kr": {
            "last_message_id": 45232,
            "last_collected_at": "2026-02-11T18:15:01.654321",
            "total_collected": 1523,
        }
    }
    save_metadata(str(filepath), data)

    result = load_metadata(str(filepath))

    assert result == data
    assert result["investnews_kr"]["last_message_id"] == 45232


def test_update_channel_metadata(tmp_path):
    filepath = tmp_path / "_metadata.json"
    save_metadata(str(filepath), {"ch_a": {"last_message_id": 10, "total_collected": 5}})

    update_channel(str(filepath), "ch_a", last_message_id=20, last_collected_at="2026-02-12T00:00:00")

    result = load_metadata(str(filepath))
    assert result["ch_a"]["last_message_id"] == 20
    assert result["ch_a"]["last_collected_at"] == "2026-02-12T00:00:00"
    assert result["ch_a"]["total_collected"] == 5  # 기존 값 유지


def test_load_returns_empty_when_file_corrupted(tmp_path):
    filepath = tmp_path / "_metadata.json"
    filepath.write_text("{corrupted data!!!", encoding="utf-8")

    result = load_metadata(str(filepath))

    assert result == {}


def test_update_increments_total_collected(tmp_path):
    filepath = tmp_path / "_metadata.json"
    save_metadata(str(filepath), {"ch_a": {"total_collected": 10}})

    increment_collected(str(filepath), "ch_a")

    result = load_metadata(str(filepath))
    assert result["ch_a"]["total_collected"] == 11


def test_update_sets_last_collected_at_on_save_success(tmp_path):
    from datetime import datetime

    filepath = tmp_path / "_metadata.json"

    update_channel(
        str(filepath), "투자뉴스A",
        last_message_id=500,
        last_collected_at="2026-02-12T10:00:00+00:00",
    )

    result = load_metadata(str(filepath))
    assert result["투자뉴스A"]["last_collected_at"] == "2026-02-12T10:00:00+00:00"
    # ISO8601 파싱 가능한지 검증
    datetime.fromisoformat(result["투자뉴스A"]["last_collected_at"])


def test_metadata_concurrent_writes_are_safe(tmp_path):
    import threading

    filepath = str(tmp_path / "_metadata.json")
    save_metadata(filepath, {})

    errors = []

    def writer(channel_name, count):
        try:
            for i in range(count):
                increment_collected(filepath, channel_name)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=writer, args=("ch_a", 50))
    t2 = threading.Thread(target=writer, args=("ch_b", 50))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(errors) == 0

    result = load_metadata(filepath)
    # 각 채널의 total_collected가 정확하지 않더라도 파일이 손상되지 않아야 함
    assert "ch_a" in result
    assert "ch_b" in result
    assert result["ch_a"]["total_collected"] >= 1
    assert result["ch_b"]["total_collected"] >= 1
