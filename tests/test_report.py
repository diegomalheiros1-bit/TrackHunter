from pathlib import Path

from trackhunter.models import TrackResult
from trackhunter.report import format_duration, write_results


def test_format_duration() -> None:
    assert format_duration(None) == "Nao informado"
    assert format_duration(4.2) == "4s"
    assert format_duration(65) == "1min 05s"
    assert format_duration(3661) == "1h 01min 01s"


def test_write_results_creates_log_and_missing_file(tmp_path: Path) -> None:
    results = [
        TrackResult("Anyma - Pictures Of You", "baixada", "ok", "pictures.mp3"),
        TrackResult("Anyma - Missing", "nao_encontrada", "not found"),
    ]

    write_results(tmp_path, results, elapsed_seconds=65)

    log_files = list(tmp_path.glob("log_execucao_*.txt"))
    missing_files = list(tmp_path.glob("nao_encontradas_*.txt"))
    assert len(log_files) == 1
    assert len(missing_files) == 1
    log_text = log_files[0].read_text(encoding="utf-8-sig")
    assert "Total: 2" in log_text
    assert "Baixadas: 1" in log_text
    assert "Nao encontradas: 1" in log_text
    assert missing_files[0].read_text(encoding="utf-8-sig") == "Anyma - Missing\n"
