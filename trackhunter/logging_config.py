import logging
from pathlib import Path
from typing import Callable


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class CallbackLogHandler(logging.Handler):
    """Encaminha logs formatados para uma callback, como a tela do Qt."""

    def __init__(self, emit_callback: Callable[[str], None]) -> None:
        super().__init__()
        self.emit_callback = emit_callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.emit_callback(self.format(record) + "\n")
        except Exception:
            self.handleError(record)


def configure_logging(
    logs_dir: Path | None = None,
    level: int = logging.INFO,
    stream=None,
    extra_handlers: list[logging.Handler] | None = None,
) -> Path | None:
    """
    Configura logging central do TrackHunter sem duplicar handlers gerenciados.
    Retorna o caminho do log tecnico quando logs_dir e informado.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    for handler in list(root_logger.handlers):
        if getattr(handler, "_trackhunter_managed", False):
            root_logger.removeHandler(handler)
            handler.close()

    technical_log_path = None
    if logs_dir is not None:
        logs_dir.mkdir(parents=True, exist_ok=True)
        technical_log_path = logs_dir / "trackhunter-runtime.log"
        file_handler = logging.FileHandler(technical_log_path, encoding="utf-8")
        _add_managed_handler(root_logger, file_handler, formatter, level)

    if stream is not None:
        stream_handler = logging.StreamHandler(stream)
        _add_managed_handler(root_logger, stream_handler, formatter, level)

    for handler in extra_handlers or []:
        _add_managed_handler(root_logger, handler, formatter, level)

    return technical_log_path


def _add_managed_handler(
    logger: logging.Logger,
    handler: logging.Handler,
    formatter: logging.Formatter,
    level: int,
) -> None:
    handler.setLevel(level)
    handler.setFormatter(formatter)
    handler._trackhunter_managed = True
    logger.addHandler(handler)
