import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .utils import normalize_text


def empty_history() -> Dict:
    """
    Estrutura padrao do historico.
    - baixadas: musicas que ja tiveram download concluido
    - nao_encontradas: musicas que podem ser tentadas novamente no futuro
    """
    return {
        "baixadas": {},
        "arquivos": {},
        "nao_encontradas": {},
    }


def reconcile_history(history: Dict) -> Dict:
    """
    Remove inconsistencias simples do historico.
    Uma faixa baixada nao deve continuar pendente em nao_encontradas.
    """
    source = history or {}
    normalized = empty_history()
    normalized["baixadas"] = dict(source.get("baixadas", {}))
    normalized["arquivos"] = dict(source.get("arquivos", {}))
    normalized["nao_encontradas"] = dict(source.get("nao_encontradas", {}))

    downloaded_keys = set(normalized.get("baixadas", {}))
    for key in list(normalized.get("nao_encontradas", {})):
        if key in downloaded_keys:
            normalized["nao_encontradas"].pop(key, None)
    return normalized


def normalize_download_format(download_format: str = "mp3") -> str:
    """Normaliza o formato usado para separar historico de MP3 e AIFF."""
    return "aiff" if str(download_format).lower() == "aiff" else "mp3"


def track_key(track: str, download_format: str | None = None) -> str:
    """Chave estavel para comparar faixas mesmo com acentos/caixa diferentes."""
    normalized_track = normalize_text(track)
    if download_format is None:
        return normalized_track
    return f"{normalize_download_format(download_format)}:{normalized_track}"


def _track_keys(track: str, download_format: str = "mp3") -> List[str]:
    current_key = track_key(track, download_format)
    if normalize_download_format(download_format) == "mp3":
        return [current_key, track_key(track)]
    return [current_key]


def file_key(file_name: str) -> str:
    """Chave estavel para comparar nomes de arquivo baixados."""
    return normalize_text(file_name)


def load_history(path: Path) -> Dict:
    """
    Carrega historico persistente em JSON.
    Se o arquivo ainda nao existir, inicia com estrutura vazia.
    """
    if not path.exists():
        return empty_history()

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    history = empty_history()
    history.update(data)
    return reconcile_history(history)


def save_history(path: Path, history: Dict) -> None:
    """Salva historico em JSON, criando a pasta se necessario."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(history, fh, ensure_ascii=False, indent=2)


def is_downloaded(history: Dict, track: str, download_format: str = "mp3") -> bool:
    """Verifica se a faixa ja foi baixada antes pelo texto da tracklist."""
    downloaded = history.get("baixadas", {})
    return any(key in downloaded for key in _track_keys(track, download_format))


def is_missing(history: Dict, track: str, download_format: str = "mp3") -> bool:
    """Verifica se a faixa esta pendente como nao encontrada."""
    missing = history.get("nao_encontradas", {})
    return any(key in missing for key in _track_keys(track, download_format))


def downloaded_file_name(history: Dict, track: str, download_format: str = "mp3") -> str:
    """
    Retorna o nome de arquivo registrado para uma faixa baixada.
    Usado para confirmar se o arquivo ainda existe fisicamente em downloads/.
    """
    downloaded = history.get("baixadas", {})
    for key in _track_keys(track, download_format):
        item = downloaded.get(key, {})
        if item:
            return item.get("file_name", "")
    return ""


def is_file_downloaded(history: Dict, file_name: str) -> bool:
    """Verifica se o arquivo retornado pelo site ja apareceu em outro download."""
    return file_key(file_name) in history.get("arquivos", {})


def mark_downloaded(history: Dict, track: str, file_name: str, download_format: str = "mp3") -> None:
    """
    Registra download concluido.
    Tambem remove a faixa das nao encontradas, porque agora ela foi resolvida.
    """
    now = datetime.now().isoformat()
    normalized_format = normalize_download_format(download_format)
    t_key = track_key(track, normalized_format)
    f_key = file_key(file_name)

    history.setdefault("baixadas", {})[t_key] = {
        "track": track,
        "file_name": file_name,
        "format": normalized_format,
        "last_seen": now,
    }
    if normalized_format == "mp3":
        history.setdefault("baixadas", {}).pop(track_key(track), None)
    if file_name:
        history.setdefault("arquivos", {})[f_key] = {
            "track": track,
            "file_name": file_name,
            "format": normalized_format,
            "last_seen": now,
        }
    for key in _track_keys(track, normalized_format):
        history.setdefault("nao_encontradas", {}).pop(key, None)


def mark_missing(history: Dict, track: str, detail: str, download_format: str = "mp3") -> None:
    """
    Registra uma faixa como nao encontrada.
    Ela continua elegivel para novas buscas em execucoes futuras.
    """
    now = datetime.now().isoformat()
    normalized_format = normalize_download_format(download_format)
    t_key = track_key(track, normalized_format)
    previous = history.setdefault("nao_encontradas", {}).get(t_key, {})

    history["nao_encontradas"][t_key] = {
        "track": track,
        "detail": detail,
        "format": normalized_format,
        "attempts": int(previous.get("attempts", 0)) + 1,
        "last_seen": now,
    }


def missing_tracks(history: Dict, download_format: str = "mp3") -> List[str]:
    """Retorna a lista de faixas marcadas como nao encontradas."""
    reconciled = reconcile_history(history)
    normalized_format = normalize_download_format(download_format)
    tracks = []
    for key, item in reconciled.get("nao_encontradas", {}).items():
        item_format = item.get("format")
        if item_format == normalized_format or (normalized_format == "mp3" and item_format is None and ":" not in key):
            tracks.append(item["track"])
    return tracks
