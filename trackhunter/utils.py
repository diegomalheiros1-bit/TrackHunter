import re
import time
import unicodedata
from pathlib import Path
from typing import List

from .models import TrackParts


class StopRequested(Exception):
    """Sinaliza que o usuario solicitou parar a execucao."""


def raise_if_stopped(stop_event) -> None:
    if stop_event is not None and stop_event.is_set():
        raise StopRequested("Execucao interrompida pelo usuario")


def wait_for_url_or_stop(page, url_pattern: str, timeout_ms: int, stop_event) -> None:
    """
    Aguarda uma URL, mas checa periodicamente se o usuario pediu parada.
    Isso evita que o botao Parar fique preso em waits longos do Playwright.
    """
    deadline = time.perf_counter() + (timeout_ms / 1000)
    last_error = None
    while time.perf_counter() < deadline:
        raise_if_stopped(stop_event)
        remaining_ms = max(1, int((deadline - time.perf_counter()) * 1000))
        try:
            page.wait_for_url(url_pattern, timeout=min(1000, remaining_ms))
            return
        except Exception as exc:
            last_error = exc
    raise last_error or TimeoutError(f"Timeout aguardando URL: {url_pattern}")


def wait_for_condition_or_stop(check, timeout_ms: int, stop_event, interval_ms: int = 500):
    """
    Aguarda uma condicao customizada checando parada do usuario entre tentativas.
    Retorna o valor truthy produzido por check(), ou None quando expira.
    """
    deadline = time.perf_counter() + (timeout_ms / 1000)
    while time.perf_counter() < deadline:
        raise_if_stopped(stop_event)
        value = check()
        if value:
            return value
        remaining_ms = max(1, int((deadline - time.perf_counter()) * 1000))
        page_wait_ms = min(interval_ms, remaining_ms)
        if page_wait_ms > 0:
            time.sleep(page_wait_ms / 1000)
    return None


def normalize_text(value: str) -> str:
    """
    Padroniza texto para comparacoes:
    - remove acentos
    - transforma em minusculas
    - comprime espacos
    """
    nfkd = unicodedata.normalize("NFKD", value)
    ascii_only = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    ascii_only = ascii_only.lower()
    ascii_only = re.sub(r"\s+", " ", ascii_only)
    return ascii_only.strip()


def parse_track_parts(track: str) -> TrackParts:
    """
    Divide uma faixa no formato comum:
    "ARTISTA - TITULO (VERSAO)".
    """
    artist = ""
    title = track.strip()
    version = ""

    if " - " in track:
        artist, title = [p.strip() for p in track.split(" - ", 1)]

    m = re.search(r"\(([^)]+)\)\s*$", title)
    if m:
        version = m.group(1).strip()
        title = title[: m.start()].strip()

    return TrackParts(artist=artist, title=title, version=version)


def build_fallback_query(track: str) -> str:
    """
    Monta consulta alternativa sem artista:
    - se tiver versao: "titulo versao"
    - senao: "titulo"
    """
    parts = parse_track_parts(track)
    if parts.version:
        return f"{parts.title} {parts.version}".strip()
    return parts.title.strip()


def load_tracklist(path: Path) -> List[str]:
    """
    Le tracklist txt (uma faixa por linha), ignora vazias e valida conteudo.
    """
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    tracks = [line.strip() for line in lines if line.strip()]
    if not tracks:
        raise ValueError(f"Tracklist vazia: {path}")
    return tracks


def ensure_dir(path: Path) -> None:
    """Cria pasta (e pais) caso ainda nao exista."""
    path.mkdir(parents=True, exist_ok=True)
