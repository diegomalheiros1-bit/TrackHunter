import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


ALLOWED_DOWNLOAD_FORMATS = {"mp3", "aiff"}
MIN_WAIT_LOGIN_MS = 1000
MIN_SEARCH_TIMEOUT_MS = 2500
MAX_TIMEOUT_MS = 600000


class ConfigError(ValueError):
    """Erro de configuracao validada antes da execucao principal."""


@dataclass(slots=True)
class Credentials:
    email: str
    password: str

    def validate(self) -> None:
        if not self.email.strip():
            raise ConfigError("Email vazio. Informe --email ou MUZPA_EMAIL.")
        if not self.password:
            raise ConfigError("Senha vazia. Informe --password ou MUZPA_PASSWORD.")


@dataclass(slots=True)
class AppConfig:
    tracklist_path: Path
    downloads_dir: Path
    logs_dir: Path
    history_path: Path
    download_format: str = "mp3"
    headless: bool = False
    manual_login: bool = False
    force_download: bool = False
    retry_missing_only: bool = False
    wait_login_ms: int = 90000
    search_timeout_ms: int = 25000

    def normalize(self) -> "AppConfig":
        self.tracklist_path = self.tracklist_path.resolve()
        self.downloads_dir = self.downloads_dir.resolve()
        self.logs_dir = self.logs_dir.resolve()
        self.history_path = self.history_path.resolve()
        self.download_format = self.download_format.lower().strip()
        self.wait_login_ms = int(self.wait_login_ms)
        self.search_timeout_ms = int(self.search_timeout_ms)
        return self

    def validate(self) -> None:
        self.normalize()
        if self.download_format not in ALLOWED_DOWNLOAD_FORMATS:
            allowed = ", ".join(sorted(ALLOWED_DOWNLOAD_FORMATS))
            raise ConfigError(f"Formato invalido: {self.download_format}. Use: {allowed}.")
        _validate_timeout("wait-login", self.wait_login_ms, MIN_WAIT_LOGIN_MS)
        _validate_timeout("search-timeout", self.search_timeout_ms, MIN_SEARCH_TIMEOUT_MS)
        if not self.retry_missing_only:
            if not self.tracklist_path.exists():
                raise ConfigError(f"Tracklist nao encontrada: {self.tracklist_path}")
            if not self.tracklist_path.is_file():
                raise ConfigError(f"Tracklist nao e um arquivo: {self.tracklist_path}")

    def ensure_directories(self) -> None:
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)


def credentials_from_sources(
    email_arg: str | None,
    password_arg: str | None,
    environ: Mapping[str, str] | None = None,
) -> Credentials:
    source = os.environ if environ is None else environ
    return Credentials(
        email=email_arg if email_arg is not None else source.get("MUZPA_EMAIL", ""),
        password=password_arg if password_arg is not None else source.get("MUZPA_PASSWORD", ""),
    )


def _validate_timeout(name: str, value: int, minimum: int) -> None:
    if value < minimum:
        raise ConfigError(f"{name} deve ser maior ou igual a {minimum} ms.")
    if value > MAX_TIMEOUT_MS:
        raise ConfigError(f"{name} deve ser menor ou igual a {MAX_TIMEOUT_MS} ms.")
