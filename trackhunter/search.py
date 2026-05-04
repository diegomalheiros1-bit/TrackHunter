import re
from typing import Optional, Tuple

from playwright.sync_api import Locator, Page

from .utils import normalize_text


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


def best_download_candidate_for_track(page: Page, track: str) -> Tuple[Optional[Locator], int]:
    """
    Procura o melhor botao de download para a faixa desejada.
    Preferencia:
    1) botoes MP3
    2) fallback ZIP/Download (se nao houver MP3 valido)

    Retorna (locator, score).
    """
    # Limite para acelerar execucao: evita varrer DOM inteiro.
    max_candidates = 120
    normalized = normalize_text(track)
    # Tokens relevantes para score de similaridade textual.
    tokens = [t for t in re.split(r"[^a-z0-9]+", normalized) if len(t) >= 3]
    candidates = page.locator("a:has-text('MP3'), button:has-text('MP3')")
    count = min(candidates.count(), max_candidates)
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
            norm_text = normalize_text(raw_text)
            score = 0
            if normalized in norm_text:
                score += 100
            # Pontuacao por sobreposicao de tokens.
            score += sum(5 for t in tokens if t in norm_text)
            btn_text = normalize_text(candidate.inner_text(timeout=500))
            if "mp3" in btn_text:
                # Bonus para reforcar escolha de MP3.
                score += 20
            if score > best_score:
                best_score = score
                best = candidate
        except Exception:
            continue

    if best is None:
        # Se nao encontrou MP3 confiavel, tenta ZIP/Download.
        fallback_candidates = page.locator(
            "a:has-text('ZIP'), button:has-text('ZIP'), a:has-text('Download'), button:has-text('Download')"
        )
        fb_count = min(fallback_candidates.count(), max_candidates)
        for idx in range(fb_count):
            candidate = fallback_candidates.nth(idx)
            try:
                if not candidate.is_visible() or not candidate.is_enabled():
                    continue
                context = candidate.locator(
                    "xpath=ancestor::*[contains(@class,'release') or contains(@class,'item') or contains(@class,'promo') or contains(@class,'scene')][1]"
                )
                if context.count() == 0:
                    context = candidate.locator("xpath=ancestor::*[3]")
                raw_text = context.first.inner_text(timeout=1000).strip()
                if not raw_text:
                    continue
                norm_text = normalize_text(raw_text)
                score = 0
                if normalized in norm_text:
                    score += 100
                score += sum(5 for t in tokens if t in norm_text)
                if score > best_score:
                    best_score = score
                    best = candidate
            except Exception:
                continue

    return best, best_score
