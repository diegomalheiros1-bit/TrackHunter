import re
from typing import Optional, Tuple

from playwright.sync_api import Locator, Page

from .utils import normalize_text


MIN_MATCH_SCORE = 6
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


def score_candidate_text(track: str, raw_text: str, button_text: str = "") -> int:
    """
    Pontua o texto de um card de resultado contra a faixa desejada.
    Mantido separado para conseguirmos testar e ajustar a heuristica sem Playwright.
    """
    normalized = normalize_text(track)
    norm_text = normalize_text(raw_text)
    tokens = {t for t in re.split(r"[^a-z0-9]+", normalized) if len(t) >= 3}

    score = 0
    if normalized in norm_text:
        score += 100
    score += sum(5 for token in tokens if token in norm_text)

    btn_text = normalize_text(button_text)
    if "mp3" in btn_text:
        score += 20
    return score


def _best_candidate_for_selector(page: Page, selector: str, track: str) -> Tuple[Optional[Locator], int]:
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
            score = score_candidate_text(track, raw_text, button_text)
            if score > best_score:
                best_score = score
                best = candidate
        except Exception:
            continue

    return best, best_score


def best_download_candidate_for_track(page: Page, track: str) -> Tuple[Optional[Locator], int]:
    """
    Procura o melhor botao de download para a faixa desejada.
    Preferencia:
    1) botoes MP3
    2) fallback ZIP/Download (se nao houver MP3 valido)

    Retorna (locator, score).
    """
    mp3_candidate, mp3_score = _best_candidate_for_selector(page, "a:has-text('MP3'), button:has-text('MP3')", track)
    if mp3_candidate is not None and mp3_score >= MIN_MATCH_SCORE:
        return mp3_candidate, mp3_score

    # Se nao encontrou MP3 confiavel, tenta ZIP/Download.
    # Importante: antes o fallback so rodava quando nao havia nenhum MP3 na pagina.
    # Isso deixava passar resultados bons com ZIP quando existia um MP3 irrelevante em outro card.
    fallback_candidate, fallback_score = _best_candidate_for_selector(
        page,
        "a:has-text('ZIP'), button:has-text('ZIP'), a:has-text('Download'), button:has-text('Download')",
        track,
    )
    if fallback_candidate is not None and fallback_score >= MIN_MATCH_SCORE:
        return fallback_candidate, fallback_score

    if mp3_candidate is not None:
        return mp3_candidate, mp3_score
    return fallback_candidate, fallback_score
