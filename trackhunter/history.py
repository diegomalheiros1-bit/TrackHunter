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


def track_key(track: str) -> str:
    """Chave estavel para comparar faixas mesmo com acentos/caixa diferentes."""
    return normalize_text(track)


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


def is_downloaded(history: Dict, track: str) -> bool:
    """Verifica se a faixa ja foi baixada antes pelo texto da tracklist."""
    return track_key(track) in history.get("baixadas", {})


def is_missing(history: Dict, track: str) -> bool:
    """Verifica se a faixa esta pendente como nao encontrada."""
    return track_key(track) in history.get("nao_encontradas", {})


def downloaded_file_name(history: Dict, track: str) -> str:
    """
    Retorna o nome de arquivo registrado para uma faixa baixada.
    Usado para confirmar se o MP3 ainda existe fisicamente em downloads/.
    """
    item = history.get("baixadas", {}).get(track_key(track), {})
    return item.get("file_name", "")


def is_file_downloaded(history: Dict, file_name: str) -> bool:
    """Verifica se o arquivo retornado pelo site ja apareceu em outro download."""
    return file_key(file_name) in history.get("arquivos", {})


def mark_downloaded(history: Dict, track: str, file_name: str) -> None:
    """
    Registra download concluido.
    Tambem remove a faixa das nao encontradas, porque agora ela foi resolvida.
    """
    now = datetime.now().isoformat()
    t_key = track_key(track)
    f_key = file_key(file_name)

    history.setdefault("baixadas", {})[t_key] = {
        "track": track,
        "file_name": file_name,
        "last_seen": now,
    }
    if file_name:
        history.setdefault("arquivos", {})[f_key] = {
            "track": track,
            "file_name": file_name,
            "last_seen": now,
        }
    history.setdefault("nao_encontradas", {}).pop(t_key, None)


def mark_missing(history: Dict, track: str, detail: str) -> None:
    """
    Registra uma faixa como nao encontrada.
    Ela continua elegivel para novas buscas em execucoes futuras.
    """
    now = datetime.now().isoformat()
    t_key = track_key(track)
    previous = history.setdefault("nao_encontradas", {}).get(t_key, {})

    history["nao_encontradas"][t_key] = {
        "track": track,
        "detail": detail,
        "attempts": int(previous.get("attempts", 0)) + 1,
        "last_seen": now,
    }


def missing_tracks(history: Dict) -> List[str]:
    """Retorna a lista de faixas marcadas como nao encontradas."""
    reconciled = reconcile_history(history)
    return [item["track"] for item in reconciled.get("nao_encontradas", {}).values()]
