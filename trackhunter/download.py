from typing import Callable, Iterable, List

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .history import downloaded_file_name, is_downloaded, is_file_downloaded, is_missing, mark_downloaded, mark_missing
from .models import TrackResult
from .search import MIN_MATCH_SCORE, best_download_candidate_for_track, find_search_input
from .utils import StopRequested, build_fallback_query, normalize_text, raise_if_stopped, wait_for_condition_or_stop


def click_download(page: Page, candidate, stop_event=None):
    """
    Envolve o clique em um contexto expect_download para capturar o arquivo.
    Timeout curto evita que candidatos ruins segurem a execucao por muito tempo.
    """
    raise_if_stopped(stop_event)
    with page.expect_download(timeout=5000) as dl_info:
        candidate.click(timeout=3000, force=True)
    return dl_info.value


def select_site_download_mode(page: Page, download_format: str, stop_event=None) -> None:
    """
    Alterna o modo global do Muzpa quando o site expõe o seletor MP3/LOSSLESS.
    AIFF aparece dentro do modo LOSSLESS; MP3 usa o modo MP3.
    """
    raise_if_stopped(stop_event)
    label = "LOSSLESS" if download_format == "aiff" else "MP3"
    selectors = [
        f"ms-layout-topbar a:has-text('{label}')",
        f"ms-layout-topbar button:has-text('{label}')",
        f"ms-layout-topbar span:has-text('{label}')",
        f".topbar a:has-text('{label}')",
        f".topbar button:has-text('{label}')",
    ]

    for selector in selectors:
        locator = page.locator(selector)
        count = min(locator.count(), 5)
        for idx in range(count):
            candidate = locator.nth(idx)
            try:
                if candidate.is_visible() and candidate.is_enabled():
                    candidate.click(timeout=1500, force=True)
                    page.wait_for_timeout(800)
                    return
            except Exception:
                continue


def process_tracks(
    page: Page,
    tracks: Iterable[str],
    downloads_dir,
    history,
    force_download: bool = False,
    download_format: str = "mp3",
    search_timeout_ms: int = 15000,
    stop_event=None,
    on_history_changed: Callable[[dict], None] | None = None,
) -> List[TrackResult]:
    """
    Processa a tracklist faixa a faixa.
    Fluxo por faixa:
    1) pula faixas ja baixadas no historico
    2) busca completa
    3) fallback "titulo + versao" (sem artista), se aplicavel
    4) tenta baixar via melhor candidato
    5) atualiza historico e registra status final
    """
    results: List[TrackResult] = []
    track_list = list(tracks)
    total = len(track_list)
    normalized_format = "aiff" if str(download_format).lower() == "aiff" else "mp3"
    normalized_search_timeout_ms = max(2500, int(search_timeout_ms or 15000))
    select_site_download_mode(page, normalized_format, stop_event=stop_event)

    def print_progress(current: int, status: str) -> None:
        """Mostra progresso simples no terminal apos cada faixa processada."""
        percent = (current / total * 100) if total else 100
        print(f"    Status: {status} | Progresso: {current}/{total} ({percent:.1f}%)")

    def notify_history_changed() -> None:
        if on_history_changed is not None:
            on_history_changed(history)

    for idx, track in enumerate(track_list, start=1):
        raise_if_stopped(stop_event)
        print(f"[{idx}/{total}] Buscando: {track}")
        try:
            # Evita downloads repetidos entre execucoes diferentes, mas so pula
            # quando o arquivo registrado ainda existe fisicamente em downloads/.
            if not force_download and is_downloaded(history, track, normalized_format):
                known_file = downloaded_file_name(history, track, normalized_format)
                if known_file and (downloads_dir / known_file).exists():
                    if is_missing(history, track, normalized_format):
                        mark_downloaded(history, track, known_file, normalized_format)
                        notify_history_changed()
                        results.append(TrackResult(track, "baixada", "Resolvida: faixa pendente ja existia no historico", file_name=known_file))
                        print("    Resolvida: pendencia ja estava baixada no historico")
                        print_progress(idx, "baixada")
                    else:
                        results.append(TrackResult(track, "ja_baixada", "Ignorada: faixa ja existe no historico", file_name=known_file))
                        print("    Ignorada: ja baixada no historico")
                        print_progress(idx, "ja_baixada")
                    continue
                print("    Historico encontrado, mas arquivo ausente; baixando novamente")

            search_input = find_search_input(page)
            if not search_input:
                results.append(TrackResult(track, "erro", "Campo de busca nao encontrado"))
                print_progress(idx, "erro")
                continue

            # Primeira tentativa usa texto completo da tracklist.
            attempts = [("busca_completa", track)]
            fallback_query = build_fallback_query(track)
            # Segunda tentativa remove artista quando a consulta muda de fato.
            if normalize_text(fallback_query) != normalize_text(track):
                attempts.append(("fallback_titulo_versao", fallback_query))

            downloaded = False
            last_detail = "Sem correspondencia relevante"

            for attempt_name, query in attempts:
                raise_if_stopped(stop_event)
                # Digita consulta e dispara busca.
                search_input.click()
                search_input.fill("")
                search_input.fill(query)
                search_input.press("Enter")

                def find_loaded_candidate():
                    row_candidate, candidate_score = best_download_candidate_for_track(page, track, normalized_format)
                    if row_candidate is not None and candidate_score >= MIN_MATCH_SCORE:
                        return row_candidate, candidate_score
                    return None

                loaded_candidate = wait_for_condition_or_stop(
                    find_loaded_candidate,
                    normalized_search_timeout_ms,
                    stop_event,
                    interval_ms=700,
                )
                row, score = loaded_candidate if loaded_candidate else (None, -1)
                if row is None or score < MIN_MATCH_SCORE:
                    last_detail = f"Sem correspondencia relevante ({attempt_name}, timeout pesquisa {normalized_search_timeout_ms} ms)"
                    continue

                try:
                    download = click_download(page, row, stop_event=stop_event)
                except PlaywrightTimeoutError:
                    # Se o clique nao dispara download, tratamos como ausencia de match util.
                    last_detail = f"Timeout aguardando download ({attempt_name})"
                    continue

                if not download:
                    last_detail = f"Correspondencia sem botao de download ({attempt_name})"
                    continue

                file_name = download.suggested_filename or ""
                if file_name and not force_download and is_file_downloaded(history, file_name) and (downloads_dir / file_name).exists():
                    # Tambem associa esta linha da tracklist ao arquivo conhecido.
                    was_missing = is_missing(history, track, normalized_format)
                    mark_downloaded(history, track, file_name, normalized_format)
                    notify_history_changed()
                    if was_missing:
                        results.append(TrackResult(track, "baixada", "Resolvida: arquivo ja existia no historico", file_name=file_name))
                        print(f"    Resolvida: arquivo ja baixado ({file_name})")
                        print_progress(idx, "baixada")
                    else:
                        results.append(TrackResult(track, "ja_baixada", "Ignorada: arquivo ja existe no historico", file_name=file_name))
                        print(f"    Ignorada: arquivo ja baixado ({file_name})")
                        print_progress(idx, "ja_baixada")
                    downloaded = True
                    break

                # Persistencia fisica na pasta downloads.
                target = downloads_dir / file_name if file_name else downloads_dir / f"download_{idx}.bin"
                download.save_as(target)
                mark_downloaded(history, track, file_name, normalized_format)
                notify_history_changed()
                results.append(TrackResult(track, "baixada", f"OK ({attempt_name})", file_name=file_name))
                print(f"    Download iniciado: {file_name}")
                print_progress(idx, "baixada")
                page.wait_for_timeout(1200)
                raise_if_stopped(stop_event)
                downloaded = True
                break

            if not downloaded:
                mark_missing(history, track, last_detail, normalized_format)
                notify_history_changed()
                results.append(TrackResult(track, "nao_encontrada", last_detail))
                print_progress(idx, "nao_encontrada")
        except PlaywrightTimeoutError:
            # Timeouts de busca/download costumam significar que o site nao retornou
            # um resultado baixavel para essa faixa dentro do tempo esperado.
            detail = "Timeout durante busca/download"
            mark_missing(history, track, detail, normalized_format)
            notify_history_changed()
            results.append(TrackResult(track, "nao_encontrada", detail))
            print_progress(idx, "nao_encontrada")
        except StopRequested:
            raise
        except Exception as exc:
            # Qualquer erro inesperado e registrado para auditoria.
            results.append(TrackResult(track, "erro", f"Falha inesperada: {exc}"))
            print_progress(idx, "erro")

    return results
