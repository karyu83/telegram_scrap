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
