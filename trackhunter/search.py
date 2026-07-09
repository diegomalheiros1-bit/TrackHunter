import re
from typing import Optional, Tuple

from playwright.sync_api import Locator, Page

from .utils import normalize_text, parse_track_parts


MIN_MATCH_SCORE = 80
MAX_CANDIDATES = 120


def find_search_input(page: Page) -> Optional[Locator]:
    """
    Retorna o melhor input de busca visivel/habilitado na tela atual.
    A ordem dos seletores vai do mais especifico ao mais generico.
    """
    candidates = [
        "ms-layout-topbar input.searchfield input",
        "ms-layout-topbar .searchfield input",
        "input[ng-model*='advancedSearchVice.form.text']",
        "input[ng-model*='advancedSearch'][placeholder*='Search' i]",
        "form.search .searchfield input",
        "input[type='search']",
        "input[placeholder*='Search' i]",
        "input[placeholder*='Buscar' i]",
        "input[aria-label*='Search' i]",
        "input[aria-label*='Buscar' i]",
        "input[type='text']",
    ]
    for selector in candidates:
        locator = page.locator(selector)
        total = locator.count()
        if total == 0:
            continue
        for idx in range(total):
            candidate = locator.nth(idx)
            try:
                if candidate.is_visible() and candidate.is_enabled():
                    return candidate
            except Exception:
                continue
    return None


def _match_text(value: str) -> str:
    normalized = normalize_text(value)
    normalized = normalized.replace("'", "").replace("’", "")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _tokens(value: str) -> list[str]:
    return [token for token in _match_text(value).split() if token]


def _coverage(expected_tokens: list[str], actual_tokens: set[str]) -> float:
    if not expected_tokens:
        return 0
    matched = sum(1 for token in expected_tokens if token in actual_tokens)
    return matched / len(expected_tokens)


def _tokens_in_order(expected_tokens: list[str], actual_tokens: list[str]) -> bool:
    if not expected_tokens:
        return False
    cursor = 0
    for token in actual_tokens:
        if token == expected_tokens[cursor]:
            cursor += 1
            if cursor == len(expected_tokens):
                return True
    return False


def _title_matches(title_tokens: list[str], title_phrase: str, candidate_text: str, candidate_tokens: set[str]) -> bool:
    if not title_tokens:
        return False
    if title_phrase and title_phrase in candidate_text:
        return True
    coverage = _coverage(title_tokens, candidate_tokens)
    if len(title_tokens) <= 4:
        return coverage == 1 and _tokens_in_order(title_tokens, candidate_text.split())
    return coverage >= 0.85 and _tokens_in_order([token for token in title_tokens if token in candidate_tokens], candidate_text.split())


def _version_matches(version_tokens: list[str], version_phrase: str, candidate_text: str, candidate_tokens: set[str]) -> bool:
    if not version_tokens:
        return True
    if version_phrase and version_phrase in candidate_text:
        return True
    return _coverage(version_tokens, candidate_tokens) >= 0.65


def _artist_matches(artist_tokens: list[str], candidate_tokens: set[str]) -> bool:
    if not artist_tokens:
        return True
    comparable_tokens = [token for token in artist_tokens if len(token) > 1] or artist_tokens
    coverage = _coverage(comparable_tokens, candidate_tokens)
    if len(comparable_tokens) == 1:
        return coverage == 1
    return coverage >= 0.5


def score_candidate_text(track: str, raw_text: str, button_text: str = "", download_format: str = "mp3") -> int:
    """
    Pontua o texto de um card de resultado contra a faixa desejada.
    Mantido separado para conseguirmos testar e ajustar a heuristica sem Playwright.
    """
    parts = parse_track_parts(track)
    candidate_text = _match_text(raw_text)
    candidate_tokens = set(candidate_text.split())
    title_tokens = _tokens(parts.title)
    title_phrase = " ".join(title_tokens)
    version_tokens = _tokens(parts.version)
    version_phrase = " ".join(version_tokens)

    if not _title_matches(title_tokens, title_phrase, candidate_text, candidate_tokens):
        return 0
    if not _version_matches(version_tokens, version_phrase, candidate_text, candidate_tokens):
        return 0
    artist_tokens = _tokens(parts.artist)
    if not _artist_matches(artist_tokens, candidate_tokens):
        return 0

    score = 70
    if title_phrase and title_phrase in candidate_text:
        score += 70
    score += int(_coverage(title_tokens, candidate_tokens) * 40)

    if version_tokens:
        if version_phrase and version_phrase in candidate_text:
            score += 45
        else:
            score += int(_coverage(version_tokens, candidate_tokens) * 25)

    if artist_tokens:
        score += int(_coverage(artist_tokens, candidate_tokens) * 35)

    btn_text = normalize_text(button_text)
    preferred_format = normalize_text(download_format)
    if preferred_format and preferred_format in btn_text:
        score += 20
    return score


def _best_candidate_for_selector(page: Page, selector: str, track: str, download_format: str = "mp3") -> Tuple[Optional[Locator], int]:
    candidates = page.locator(selector)
    count = min(candidates.count(), MAX_CANDIDATES)
    best = None
    best_score = -1

    for idx in range(count):
        candidate = candidates.nth(idx)
        try:
            if not candidate.is_visible() or not candidate.is_enabled():
                continue
            # Sobe para um container pai e compara texto do card com a faixa alvo.
            context = candidate.locator(
                "xpath=ancestor::*[contains(@class,'release') or contains(@class,'item') or contains(@class,'promo') or contains(@class,'scene')][1]"
            )
            if context.count() == 0:
                # Fallback de arvore caso classes mudem.
                context = candidate.locator("xpath=ancestor::*[3]")
            raw_text = context.first.inner_text(timeout=1000).strip()
            if not raw_text:
                continue
            button_text = candidate.inner_text(timeout=500)
            score = score_candidate_text(track, raw_text, button_text, download_format)
            if score > best_score:
                best_score = score
                best = candidate
        except Exception:
            continue

    return best, best_score


def best_download_candidate_for_track(page: Page, track: str, download_format: str = "mp3") -> Tuple[Optional[Locator], int]:
    """
    Procura o melhor botao de download para a faixa desejada.
    Preferencia:
    1) botoes do formato escolhido (MP3 ou AIFF)

    Retorna (locator, score).
    """
    normalized_format = normalize_text(download_format)
    format_label = "AIFF" if normalized_format == "aiff" else "MP3"
    format_candidate, format_score = _best_candidate_for_selector(
        page,
        f"a:has-text('{format_label}'), button:has-text('{format_label}')",
        track,
        format_label,
    )
    if format_candidate is not None and format_score >= MIN_MATCH_SCORE:
        return format_candidate, format_score

    return format_candidate, format_score
