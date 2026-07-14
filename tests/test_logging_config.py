import logging
from pathlib import Path

from trackhunter.logging_config import CallbackLogHandler, configure_logging


def test_configure_logging_writes_runtime_file(tmp_path: Path) -> None:
    log_path = configure_logging(tmp_path)

    logging.getLogger("trackhunter.test").info("runtime ready")

    assert log_path == tmp_path / "trackhunter-runtime.log"
    assert "runtime ready" in log_path.read_text(encoding="utf-8")


def test_callback_log_handler_emits_formatted_message() -> None:
    messages: list[str] = []
    handler = CallbackLogHandler(messages.append)
    configure_logging(extra_handlers=[handler])

    logging.getLogger("trackhunter.test").warning("visible in gui")

    assert messages
    assert "WARNING" in messages[0]
    assert "visible in gui" in messages[0]
