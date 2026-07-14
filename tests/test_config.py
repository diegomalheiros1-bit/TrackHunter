from pathlib import Path

import pytest

from trackhunter.config import AppConfig, ConfigError, Credentials, credentials_from_sources


def test_app_config_validates_and_creates_directories(tmp_path: Path) -> None:
    tracklist = tmp_path / "tracklist.txt"
    tracklist.write_text("Artist - Track\n", encoding="utf-8")
    config = AppConfig(
        tracklist_path=tracklist,
        downloads_dir=tmp_path / "downloads",
        logs_dir=tmp_path / "logs",
        history_path=tmp_path / "state" / "history.json",
        download_format="AIFF",
    )

    config.validate()
    config.ensure_directories()

    assert config.download_format == "aiff"
    assert config.downloads_dir.is_dir()
    assert config.logs_dir.is_dir()
    assert config.history_path.parent.is_dir()


def test_app_config_rejects_invalid_format(tmp_path: Path) -> None:
    tracklist = tmp_path / "tracklist.txt"
    tracklist.write_text("Artist - Track\n", encoding="utf-8")
    config = AppConfig(
        tracklist_path=tracklist,
        downloads_dir=tmp_path / "downloads",
        logs_dir=tmp_path / "logs",
        history_path=tmp_path / "history.json",
        download_format="wav",
    )

    with pytest.raises(ConfigError, match="Formato invalido"):
        config.validate()


def test_app_config_requires_tracklist_unless_retrying_missing(tmp_path: Path) -> None:
    config = AppConfig(
        tracklist_path=tmp_path / "missing.txt",
        downloads_dir=tmp_path / "downloads",
        logs_dir=tmp_path / "logs",
        history_path=tmp_path / "history.json",
        retry_missing_only=True,
    )

    config.validate()


def test_app_config_rejects_too_small_timeout(tmp_path: Path) -> None:
    tracklist = tmp_path / "tracklist.txt"
    tracklist.write_text("Artist - Track\n", encoding="utf-8")
    config = AppConfig(
        tracklist_path=tracklist,
        downloads_dir=tmp_path / "downloads",
        logs_dir=tmp_path / "logs",
        history_path=tmp_path / "history.json",
        search_timeout_ms=100,
    )

    with pytest.raises(ConfigError, match="search-timeout"):
        config.validate()


def test_credentials_from_args_override_environment() -> None:
    credentials = credentials_from_sources(
        "arg@example.com",
        "arg-password",
        {"MUZPA_EMAIL": "env@example.com", "MUZPA_PASSWORD": "env-password"},
    )

    assert credentials == Credentials("arg@example.com", "arg-password")


def test_credentials_validate_requires_email_and_password() -> None:
    with pytest.raises(ConfigError, match="Email vazio"):
        Credentials("", "secret").validate()

    with pytest.raises(ConfigError, match="Senha vazia"):
        Credentials("user@example.com", "").validate()
