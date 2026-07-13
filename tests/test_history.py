import json
from pathlib import Path

from trackhunter.history import (
    downloaded_file_name,
    empty_history,
    is_downloaded,
    is_file_downloaded,
    is_missing,
    load_history,
    mark_downloaded,
    mark_missing,
    missing_tracks,
    reconcile_history,
    save_history,
    track_key,
)


def test_load_history_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_history(tmp_path / "missing.json") == empty_history()


def test_mark_downloaded_and_reload(tmp_path: Path) -> None:
    history_path = tmp_path / "state" / "track_history.json"
    history = empty_history()

    mark_downloaded(history, "Anyma - Pictures Of You", "pictures.mp3", "mp3")
    save_history(history_path, history)
    loaded = load_history(history_path)

    assert is_downloaded(loaded, "anyma - pictures of you", "mp3")
    assert is_file_downloaded(loaded, "Pictures.mp3")
    assert downloaded_file_name(loaded, "Anyma - Pictures Of You", "mp3") == "pictures.mp3"


def test_mark_missing_increments_attempts(tmp_path: Path) -> None:
    history_path = tmp_path / "history.json"
    history = empty_history()

    mark_missing(history, "Anyma - Missing Track", "not found", "mp3")
    mark_missing(history, "Anyma - Missing Track", "not found again", "mp3")
    save_history(history_path, history)
    loaded = load_history(history_path)

    item = loaded["nao_encontradas"][track_key("Anyma - Missing Track", "mp3")]
    assert item["attempts"] == 2
    assert is_missing(loaded, "Anyma - Missing Track", "mp3")


def test_mark_downloaded_removes_missing_pending() -> None:
    history = empty_history()

    mark_missing(history, "Anyma - Pictures Of You", "not found", "mp3")
    mark_downloaded(history, "Anyma - Pictures Of You", "pictures.mp3", "mp3")

    assert is_downloaded(history, "Anyma - Pictures Of You", "mp3")
    assert not is_missing(history, "Anyma - Pictures Of You", "mp3")


def test_history_separates_mp3_and_aiff() -> None:
    history = empty_history()

    mark_downloaded(history, "Anyma - Pictures Of You", "pictures.mp3", "mp3")

    assert is_downloaded(history, "Anyma - Pictures Of You", "mp3")
    assert not is_downloaded(history, "Anyma - Pictures Of You", "aiff")


def test_reconcile_history_removes_downloaded_from_missing() -> None:
    key = track_key("Anyma - Pictures Of You", "mp3")
    history = {
        "baixadas": {key: {"track": "Anyma - Pictures Of You"}},
        "arquivos": {},
        "nao_encontradas": {key: {"track": "Anyma - Pictures Of You"}},
    }

    reconciled = reconcile_history(history)

    assert key in reconciled["baixadas"]
    assert key not in reconciled["nao_encontradas"]


def test_load_history_old_unformatted_mp3_key() -> None:
    history = {"baixadas": {track_key("Anyma - Pictures Of You"): {"track": "Anyma - Pictures Of You"}}}

    assert is_downloaded(history, "Anyma - Pictures Of You", "mp3")
    assert not is_downloaded(history, "Anyma - Pictures Of You", "aiff")


def test_missing_tracks_filters_by_format() -> None:
    history = empty_history()
    mark_missing(history, "Anyma - MP3 Missing", "not found", "mp3")
    mark_missing(history, "Anyma - AIFF Missing", "not found", "aiff")

    assert missing_tracks(history, "mp3") == ["Anyma - MP3 Missing"]
    assert missing_tracks(history, "aiff") == ["Anyma - AIFF Missing"]


def test_load_history_corrupted_json_returns_empty_and_backups_file(tmp_path: Path) -> None:
    history_path = tmp_path / "track_history.json"
    history_path.write_text("{invalid json", encoding="utf-8")

    history = load_history(history_path)

    assert history == empty_history()
    backups = list(tmp_path.glob("track_history.corrupted_*.json"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "{invalid json"


def test_save_history_replaces_file_atomically_without_tmp_leftover(tmp_path: Path) -> None:
    history_path = tmp_path / "track_history.json"
    history = empty_history()
    mark_downloaded(history, "Anyma - Pictures Of You", "pictures.mp3", "mp3")

    save_history(history_path, history)

    loaded_raw = json.loads(history_path.read_text(encoding="utf-8"))
    assert "baixadas" in loaded_raw
    assert not list(tmp_path.glob("*.tmp"))
