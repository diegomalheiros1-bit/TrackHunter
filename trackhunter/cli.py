import argparse
import logging
import sys
import time
from pathlib import Path

# Ponto de entrada do Playwright sincronizado.
from playwright.sync_api import sync_playwright

# Modulos internos separados por responsabilidade.
from .auth import do_login
from .config import AppConfig, Credentials, credentials_from_sources
from .download import process_tracks
from .history import load_history, missing_tracks, save_history
from .logging_config import configure_logging
from .models import TrackResult
from .report import write_results
from .utils import StopRequested, load_tracklist, raise_if_stopped, wait_for_url_or_stop

# Tela base usada para login e inicio de processamento.
DEFAULT_URL = "https://srv.muzpa.com/#/media/releases"
logger = logging.getLogger(__name__)


def run(argv: list[str] | None = None, stop_event=None, credentials: Credentials | None = None) -> None:
    """
    Orquestrador principal:
    - le argumentos
    - prepara pastas e tracklist
    - abre navegador
    - executa login (manual ou automatico)
    - processa downloads
    - atualiza historico de baixadas/nao encontradas
    - grava log final
    """
    # Garante saida UTF-8 no terminal (acentos e caracteres especiais).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Robo de busca e download no Muzpa")
    # Arquivo com lista de musicas.
    parser.add_argument("--tracklist", default="tracklist.txt", help="Caminho para tracklist txt")
    # Pasta onde os arquivos baixados serao salvos.
    parser.add_argument("--downloads", default="downloads", help="Pasta para salvar os arquivos baixados")
    # Pasta de logs textuais.
    parser.add_argument("--logs", default="logs", help="Pasta para salvar log de execucao")
    # Compatibilidade com versoes antigas (equivale a downloads).
    parser.add_argument("--output", default=None, help="(Legado) Pasta de downloads")
    # Modo sem interface grafica.
    parser.add_argument("--headless", action="store_true", help="Executa sem interface grafica")
    # Tempo maximo para aguardar login.
    parser.add_argument("--wait-login", type=int, default=90000, help="Timeout de login em ms")
    # Tempo maximo para aguardar resultados de cada pesquisa.
    parser.add_argument("--search-timeout", type=int, default=15000, help="Timeout da pesquisa de cada musica em ms")
    # Se ativo, usuario faz login manual na janela.
    parser.add_argument("--manual-login", action="store_true", help="Nao preenche login automaticamente")
    # Arquivo JSON usado para evitar downloads duplicados e guardar nao encontradas.
    parser.add_argument("--history", default="state/track_history.json", help="Arquivo JSON de historico")
    # Ignora o historico de baixadas e permite baixar novamente.
    parser.add_argument("--force-download", action="store_true", help="Ignora historico e baixa novamente")
    # Processa somente faixas que ficaram como nao encontradas em execucoes anteriores.
    parser.add_argument("--retry-missing-only", action="store_true", help="Busca somente faixas nao encontradas no historico")
    # Formato de arquivo desejado.
    parser.add_argument("--download-format", choices=["mp3", "aiff"], default="mp3", help="Formato de download desejado")
    # Credenciais opcionais por argumento (prioridade sobre variaveis de ambiente).
    parser.add_argument("--email", default=None, help="Email de login do Muzpa")
    parser.add_argument("--password", default=None, help="Senha de login do Muzpa")
    args = parser.parse_args(argv)
    started_at = time.perf_counter()

    config = AppConfig(
        tracklist_path=Path(args.tracklist),
        # --output sobrescreve --downloads quando fornecido.
        downloads_dir=Path(args.output if args.output else args.downloads),
        logs_dir=Path(args.logs),
        history_path=Path(args.history),
        download_format=args.download_format,
        headless=args.headless,
        manual_login=args.manual_login,
        force_download=args.force_download,
        retry_missing_only=args.retry_missing_only,
        wait_login_ms=args.wait_login,
        search_timeout_ms=args.search_timeout,
    )
    config.validate()
    config.ensure_directories()
    configure_logging(config.logs_dir)
    logger.info(
        "Iniciando TrackHunter: formato=%s headless=%s manual_login=%s retry_missing_only=%s",
        config.download_format,
        config.headless,
        config.manual_login,
        config.retry_missing_only,
    )

    results: list[TrackResult] = []
    log_written = False
    browser = None
    context = None

    try:
        raise_if_stopped(stop_event)
        # Historico persistente: baixadas sao puladas; nao encontradas podem ser tentadas de novo.
        history = load_history(config.history_path)
        # Persiste limpeza de entradas obsoletas, por exemplo faixa em baixadas e nao_encontradas ao mesmo tempo.
        save_history(config.history_path, history)

        if config.retry_missing_only:
            # Neste modo, a fonte de faixas e o historico, nao a tracklist.
            tracks = missing_tracks(history, config.download_format)
            if not tracks:
                logger.info("Nenhuma faixa nao encontrada no historico para tentar novamente.")
                print("Nenhuma faixa nao encontrada no historico para tentar novamente.")
                write_results(config.logs_dir, [], elapsed_seconds=time.perf_counter() - started_at)
                log_written = True
                return
        else:
            # Carrega tracks do txt.
            tracks = load_tracklist(config.tracklist_path)

        # Credenciais para login automatico.
        login_credentials = credentials or credentials_from_sources(args.email, args.password)
        if not config.manual_login:
            login_credentials.validate()

        # Ciclo de vida Playwright: browser -> context -> page.
        with sync_playwright() as p:
            raise_if_stopped(stop_event)
            browser = p.chromium.launch(headless=config.headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            raise_if_stopped(stop_event)

            if config.manual_login:
                # Fluxo manual: usuario autentica na janela.
                page.goto(DEFAULT_URL, wait_until="domcontentloaded")
                logger.info("Login manual habilitado.")
                print("Login manual habilitado. Faca o login na janela e aguarde...")
                try:
                    wait_for_url_or_stop(page, "**/media/releases**", config.wait_login_ms, stop_event)
                except StopRequested:
                    raise
                except Exception:
                    logger.warning("Nao confirmou URL de releases no login manual; seguindo com processamento.")
                    print("Nao confirmou URL de releases no login manual; seguindo com tentativa de processamento.")
            else:
                # Fluxo automatico: valida variaveis e chama modulo de autenticacao.
                logger.info("Login automatico habilitado para email=%s", login_credentials.email)
                do_login(page, login_credentials.email, login_credentials.password, config.wait_login_ms, DEFAULT_URL, stop_event=stop_event)

            # Garante inicio na pagina base antes da busca.
            raise_if_stopped(stop_event)
            page.goto(DEFAULT_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            raise_if_stopped(stop_event)

            # Processa a lista e retorna resultados estruturados.
            results = process_tracks(
                page,
                tracks,
                config.downloads_dir,
                history,
                force_download=config.force_download,
                download_format=config.download_format,
                search_timeout_ms=config.search_timeout_ms,
                stop_event=stop_event,
                on_history_changed=lambda updated_history: save_history(config.history_path, updated_history),
            )
            save_history(config.history_path, history)
            # Salva log final da execucao.
            write_results(config.logs_dir, results, elapsed_seconds=time.perf_counter() - started_at)
            log_written = True

    except StopRequested as exc:
        logger.info("Execucao interrompida pelo usuario.")
        print("Execucao interrompida pelo usuario.")
        if not log_written:
            stop_result = TrackResult(
                track="Execucao",
                status="erro",
                detail=str(exc),
            )
            write_results(config.logs_dir, [*results, stop_result], elapsed_seconds=time.perf_counter() - started_at)
            log_written = True
        raise
    except Exception as exc:
        logger.exception("Falha na execucao do TrackHunter.")
        if not log_written:
            error_result = TrackResult(
                track="Execucao",
                status="erro",
                detail=f"Falha antes da conclusao: {exc}",
            )
            write_results(config.logs_dir, [*results, error_result], elapsed_seconds=time.perf_counter() - started_at)
            log_written = True
        raise

    finally:
        # Fecha recursos explicitamente quando uma falha acontece antes do final normal.
        if context is not None:
            try:
                context.close()
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass


def main() -> None:
    run()


if __name__ == "__main__":
    main()

