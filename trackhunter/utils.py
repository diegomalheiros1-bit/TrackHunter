import re
import unicodedata
from pathlib import Path
from typing import List

from .models import TrackParts


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
