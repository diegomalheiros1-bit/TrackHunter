from pathlib import Path

import pytest

from trackhunter.utils import build_fallback_query, load_tracklist, normalize_text, parse_track_parts


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Ação RÁPIDA", "acao rapida"),
        ("  Anyma   -   Pictures   ", "anyma - pictures"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_normalize_text(value: str, expected: str) -> None:
    assert normalize_text(value) == expected


def test_parse_track_parts_with_artist_title_and_remix() -> None:
    parts = parse_track_parts("Anyma - Pictures Of You (Extended Remix)")

    assert parts.artist == "Anyma"
    assert parts.title == "Pictures Of You"
    assert parts.version == "Extended Remix"


def test_parse_track_parts_without_artist() -> None:
    parts = parse_track_parts("Pictures Of You (Original Mix)")

    assert parts.artist == ""
    assert parts.title == "Pictures Of You"
    assert parts.version == "Original Mix"


def test_parse_track_parts_without_version() -> None:
    parts = parse_track_parts("Anyma - Pictures Of You")

    assert parts.artist == "Anyma"
    assert parts.title == "Pictures Of You"
    assert parts.version == ""


@pytest.mark.parametrize(
    ("track", "expected"),
    [
        ("Anyma - Pictures Of You (Extended Remix)", "Pictures Of You Extended Remix"),
        ("Anyma - Pictures Of You", "Pictures Of You"),
        ("Pictures Of You (Original Mix)", "Pictures Of You Original Mix"),
    ],
)
def test_build_fallback_query(track: str, expected: str) -> None:
    assert build_fallback_query(track) == expected


def test_load_tracklist_ignores_bom_blank_lines_and_spaces(tmp_path: Path) -> None:
    tracklist_path = tmp_path / "tracklist.txt"
    tracklist_path.write_text("\ufeff\n Anyma - Pictures Of You \n\nMassano - The Feeling\n", encoding="utf-8")

    assert load_tracklist(tracklist_path) == ["Anyma - Pictures Of You", "Massano - The Feeling"]


def test_load_tracklist_empty_file_raises(tmp_path: Path) -> None:
    tracklist_path = tmp_path / "tracklist.txt"
    tracklist_path.write_text("\ufeff\n\n   \n", encoding="utf-8")

    with pytest.raises(ValueError, match="Tracklist vazia"):
        load_tracklist(tracklist_path)
