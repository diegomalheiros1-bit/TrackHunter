import os
import re
import sys
import ctypes
import time
import threading
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, QSettings, QSize, Qt, QThread, Signal, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from .cli import run as run_bot
from .history import load_history
from .report import format_duration
from .utils import StopRequested, load_tracklist


def asset_path(file_name: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent)) / "assets" / file_name
    return Path(__file__).resolve().parent.parent / "assets" / file_name


def set_windows_app_id() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TrackHunter.Desktop.v2")
    except Exception:
        return


APP_STYLE = """
QMainWindow, QDialog {
    background: #0f131a;
    color: #edf2f7;
    font-family: Segoe UI;
    font-size: 10pt;
}
QWidget {
    color: #edf2f7;
}
QFrame#Panel {
    background: #171d26;
    border: 1px solid #253041;
    border-radius: 10px;
}
QLabel#SectionTitle {
    color: #f8fafc;
    font-size: 12pt;
    font-weight: 700;
}
QLabel#MusicIcon {
    color: #7dd3fc;
    font-size: 16pt;
    font-weight: 800;
    min-width: 22px;
    max-width: 22px;
}
QLabel#Hint, QLabel#FieldLabel, QLabel#ProgressText {
    color: #94a3b8;
}
QLabel#ProgressText {
    color: #cbd5e1;
    font-weight: 600;
}
QLabel#FieldLabel {
    min-height: 38px;
}
QLabel#HelpLabel {
    color: #7f8ea3;
    font-size: 9pt;
    min-height: 18px;
}
QLabel#SuccessLabel {
    color: #86efac;
    font-size: 9pt;
    min-height: 18px;
}
QLabel#WarningLabel {
    color: #fbbf24;
    font-size: 9pt;
    min-height: 18px;
}
QLineEdit {
    background: #0f141d;
    border: 1px solid #2a3546;
    border-radius: 8px;
    color: #f8fafc;
    min-height: 38px;
    padding: 0 10px;
    selection-background-color: #2563eb;
    placeholder-text-color: #B0B0B0;
}
QLineEdit:focus {
    border-color: #3b82f6;
}
QFrame#MillisStepper {
    background: #0f141d;
    border: 1px solid #2a3546;
    border-radius: 8px;
}
QFrame#MillisStepper:focus-within {
    border-color: #3b82f6;
}
QFrame#MillisStepper QLineEdit {
    background: transparent;
    border: 0;
    border-radius: 0;
    min-height: 36px;
    padding: 0 8px 0 10px;
}
QPushButton#StepperButton {
    background: transparent;
    border: 0;
    border-radius: 0;
    color: #dbeafe;
    font-size: 9pt;
    font-weight: 700;
    min-height: 18px;
    max-height: 18px;
    min-width: 28px;
    padding: 0;
}
QPushButton#StepperButton:hover {
    background: #1e293b;
}
QPushButton, QToolButton {
    background: #263244;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #f8fafc;
    font-weight: 600;
    min-height: 38px;
    padding: 0 14px;
}
QPushButton:hover, QToolButton:hover {
    background: #334155;
}
QPushButton:disabled {
    background: #1e293b;
    color: #64748b;
}
QPushButton#StartButton {
    background: #2563eb;
    border: 1px solid #3b82f6;
    font-size: 11pt;
    min-width: 104px;
    min-height: 44px;
}
QPushButton#StartButton:hover {
    background: #1d4ed8;
}
QPushButton#StopButton {
    background: #dc2626;
    border: 1px solid #ef4444;
    color: #ffffff;
    font-size: 11pt;
    min-width: 104px;
    min-height: 44px;
}
QPushButton#StopButton:hover {
    background: #b91c1c;
}
QPushButton#StopButton:disabled {
    background: #7f1d1d;
    border: 1px solid #991b1b;
    color: #fecaca;
}
QPushButton#BrowseButton {
    background: #1f2a3a;
    color: #bfdbfe;
}
QPushButton#GhostButton {
    background: transparent;
    border: 1px solid #334155;
    color: #cbd5e1;
}
QPushButton#GhostButton:hover {
    background: transparent;
    border: 1px solid #64748b;
    color: #f8fafc;
}
QListWidget {
    background: #0b1018;
    border: 1px solid #253041;
    border-radius: 10px;
    font-size: 9pt;
    padding: 4px;
    outline: 0;
}
QPlainTextEdit {
    background: #0b1018;
    border: 1px solid #253041;
    border-radius: 10px;
    color: #f8fafc;
    font-family: Consolas, Segoe UI;
    font-size: 10pt;
    padding: 10px;
    selection-background-color: #2563eb;
    placeholder-text-color: #B0B0B0;
}
QPlainTextEdit:focus {
    border-color: #3b82f6;
}
QListWidget::item {
    border-radius: 7px;
    margin: 1px;
    padding: 2px 7px;
}
QListWidget::item:selected {
    background: #1e293b;
}
QFrame#SummaryCard {
    background: #0f141d;
    border: 1px solid #253041;
    border-radius: 9px;
}
QLabel#SummaryValue {
    color: #f8fafc;
    font-size: 16pt;
    font-weight: 800;
}
QLabel#SummaryTitle {
    color: #94a3b8;
    font-size: 8.5pt;
}
QLabel#HistorySummary {
    color: #94a3b8;
}
QLabel#TooltipBadge {
    background: #253041;
    border: 1px solid #3b4a60;
    border-radius: 9px;
    color: #cbd5e1;
    font-size: 8pt;
    font-weight: 700;
    min-width: 18px;
    max-width: 18px;
    min-height: 18px;
    max-height: 18px;
}
QToolTip {
    background: #111827;
    border: 1px solid #3b4a60;
    color: #f8fafc;
    padding: 7px;
}
QProgressBar {
    background: #111827;
    border: 1px solid #253041;
    border-radius: 9px;
    color: transparent;
    min-height: 18px;
    max-height: 18px;
    text-align: center;
}
QProgressBar::chunk {
    background: #22c55e;
    border-radius: 9px;
}
QCheckBox {
    color: #dbeafe;
    spacing: 10px;
}
QCheckBox::indicator {
    width: 42px;
    height: 22px;
    border-radius: 11px;
    background: #334155;
}
QCheckBox::indicator:checked {
    background: #2563eb;
}
QCheckBox::indicator:unchecked {
    background: #475569;
}
"""


class MillisecondsStepper(QFrame):
    def __init__(self, minimum: int, maximum: int, step: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("MillisStepper")
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.setMinimumWidth(126)
        self.setMaximumWidth(142)
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.input = QLineEdit()
        self.input.setMinimumWidth(86)
        self.input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.input.editingFinished.connect(self._normalize_text)

        buttons = QVBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(0)

        self.up_btn = QPushButton("▲")
        self.up_btn.setObjectName("StepperButton")
        self.up_btn.clicked.connect(lambda: self.step_by(self.step))

        self.down_btn = QPushButton("▼")
        self.down_btn.setObjectName("StepperButton")
        self.down_btn.clicked.connect(lambda: self.step_by(-self.step))

        buttons.addWidget(self.up_btn)
        buttons.addWidget(self.down_btn)
        layout.addWidget(self.input, 1)
        layout.addLayout(buttons)
        self.setValue(minimum)

    def value(self) -> int:
        digits = re.sub(r"\D", "", self.input.text())
        if not digits:
            return self.minimum
        return max(self.minimum, min(self.maximum, int(digits)))

    def setValue(self, value: int) -> None:
        bounded = max(self.minimum, min(self.maximum, value))
        self.input.setText(f"{bounded} ms")
        self.input.setCursorPosition(0)

    def step_by(self, delta: int) -> None:
        self.setValue(self.value() + delta)

    def _normalize_text(self) -> None:
        self.setValue(self.value())


class IconLineEdit(QLineEdit):
    def __init__(self, icon_name: str, parent: QWidget | None = None, password: bool = False) -> None:
        super().__init__(parent)
        self.icon_name = icon_name
        self.has_password_toggle = password
        self.password_hidden = password
        self.icon_color = QColor("#9aa7b8")
        self.setFixedHeight(40)
        self.setMinimumWidth(260)
        self.setMaximumWidth(760)
        self.setTextMargins(34, 0, 34 if password else 10, 0)
        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.setCursor(Qt.CursorShape.IBeamCursor)

    def sizeHint(self) -> QSize:
        return QSize(520, 38)

    def toggle_password_visibility(self) -> None:
        if not self.has_password_toggle:
            return
        self.password_hidden = not self.password_hidden
        mode = QLineEdit.EchoMode.Password if self.password_hidden else QLineEdit.EchoMode.Normal
        self.setEchoMode(mode)
        self.update()

    def mousePressEvent(self, event) -> None:
        if self.has_password_toggle and event.button() == Qt.MouseButton.LeftButton:
            icon_rect = self._trailing_icon_rect()
            if icon_rect.contains(event.position()):
                self.toggle_password_visibility()
                return
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self.icon_color, 1.7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        self._draw_leading_icon(painter, self._leading_icon_rect())
        if self.has_password_toggle:
            self._draw_eye_icon(painter, self._trailing_icon_rect(), self.password_hidden)
        painter.end()

    def _leading_icon_rect(self) -> QRectF:
        side = 18
        return QRectF(10, (self.height() - side) / 2, side, side)

    def _trailing_icon_rect(self) -> QRectF:
        side = 18
        return QRectF(self.width() - side - 11, (self.height() - side) / 2, side, side)

    def _draw_leading_icon(self, painter: QPainter, rect: QRectF) -> None:
        if self.icon_name == "person":
            painter.drawEllipse(QRectF(rect.x() + 6, rect.y() + 3, 6, 6))
            painter.drawArc(QRectF(rect.x() + 3.5, rect.y() + 10, 11, 7), 0, 180 * 16)
            painter.drawLine(rect.x() + 4, rect.y() + 15, rect.x() + 14, rect.y() + 15)
            return

        if self.icon_name == "lock":
            painter.drawRoundedRect(QRectF(rect.x() + 4, rect.y() + 9, 10, 7), 2, 2)
            painter.drawArc(QRectF(rect.x() + 5.5, rect.y() + 3, 7, 10), 0, 180 * 16)
            painter.drawLine(rect.x() + 5.5, rect.y() + 9, rect.x() + 5.5, rect.y() + 8)
            painter.drawLine(rect.x() + 12.5, rect.y() + 9, rect.x() + 12.5, rect.y() + 8)
            return

        if self.icon_name == "folder":
            painter.drawPolyline(
                [
                    rect.topLeft() + QPointF(2, 6),
                    rect.topLeft() + QPointF(7, 6),
                    rect.topLeft() + QPointF(9, 8),
                    rect.topLeft() + QPointF(16, 8),
                    rect.topLeft() + QPointF(16, 15),
                    rect.topLeft() + QPointF(2, 15),
                    rect.topLeft() + QPointF(2, 6),
                ]
            )
            return

        if self.icon_name == "music":
            painter.drawLine(rect.x() + 7, rect.y() + 4, rect.x() + 7, rect.y() + 13)
            painter.drawLine(rect.x() + 7, rect.y() + 4, rect.x() + 14, rect.y() + 6)
            painter.drawLine(rect.x() + 14, rect.y() + 6, rect.x() + 14, rect.y() + 15)
            painter.drawEllipse(QRectF(rect.x() + 3, rect.y() + 12, 6, 4))
            painter.drawEllipse(QRectF(rect.x() + 10, rect.y() + 14, 6, 4))

    def _draw_eye_icon(self, painter: QPainter, rect: QRectF, hidden: bool) -> None:
        points = [
            rect.topLeft() + QPointF(2, 9),
            rect.topLeft() + QPointF(5, 5.5),
            rect.topLeft() + QPointF(9, 4),
            rect.topLeft() + QPointF(13, 5.5),
            rect.topLeft() + QPointF(16, 9),
            rect.topLeft() + QPointF(13, 12.5),
            rect.topLeft() + QPointF(9, 14),
            rect.topLeft() + QPointF(5, 12.5),
            rect.topLeft() + QPointF(2, 9),
        ]
        painter.drawPolyline(points)
        painter.drawEllipse(QRectF(rect.x() + 7, rect.y() + 7, 4, 4))
        if hidden:
            painter.drawLine(rect.x() + 4, rect.y() + 3, rect.x() + 15, rect.y() + 15)


class Panel(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 14, 16, 14)
        self.layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        self.layout.addWidget(title_label)


class SummaryCard(QFrame):
    def __init__(self, title: str, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SummaryCard")
        self.color = color
        self.setMinimumHeight(66)
        self.setMinimumWidth(98)
        self.setMaximumWidth(138)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 9, 14, 8)
        layout.setSpacing(2)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("SummaryValue")
        self.value_label.setStyleSheet(f"color: {color};")
        self.value_label.setFixedHeight(30)

        title_label = QLabel(title)
        title_label.setObjectName("SummaryTitle")
        title_label.setFixedHeight(20)

        layout.addWidget(self.value_label)
        layout.addWidget(title_label)

    def set_value(self, value: int) -> None:
        self.value_label.setText(str(value))


class ToggleSwitch(QCheckBox):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setMinimumWidth(max(112, self.fontMetrics().horizontalAdvance(text) + 64))

    def sizeHint(self) -> QSize:
        return QSize(self.minimumWidth(), 32)

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        track = self.rect().adjusted(0, 5, -self.rect().width() + 46, -5)
        track_color = QColor("#2563eb" if self.isChecked() else "#475569")
        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track, 11, 11)

        knob_x = track.right() - 18 if self.isChecked() else track.left() + 4
        painter.setBrush(QColor("#f8fafc"))
        painter.drawEllipse(knob_x, track.top() + 4, 14, 14)

        painter.setPen(QColor("#dbeafe"))
        text_rect = self.rect().adjusted(58, 0, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())


class _StreamEmitter:
    def __init__(self, callback) -> None:
        self.callback = callback

    def write(self, text: str) -> int:
        if text:
            self.callback(text)
        return len(text)

    def flush(self) -> None:
        return


class BotWorker(QThread):
    output = Signal(str)
    finished_with_code = Signal(int)

    def __init__(self, args: list[str], email: str, password: str) -> None:
        super().__init__()
        self.args = args
        self.email = email
        self.password = password
        self.stop_event = threading.Event()

    def request_stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        if self.email:
            os.environ["MUZPA_EMAIL"] = self.email
        if self.password:
            os.environ["MUZPA_PASSWORD"] = self.password

        stream = _StreamEmitter(self.output.emit)
        exit_code = 0
        try:
            with redirect_stdout(stream), redirect_stderr(stream):
                run_bot(self.args, stop_event=self.stop_event)
        except StopRequested:
            exit_code = 130
        except Exception as exc:
            exit_code = 1
            self.output.emit(f"\nErro: {exc}\n")
        self.finished_with_code.emit(exit_code)


class SettingsDialog(QDialog):
    def __init__(self, parent, logs_path: str, history_path: str, downloads_path: str, base_dir: Path) -> None:
        super().__init__(parent)
        self.setWindowTitle("Arquivos do TrackHunter")
        self.resize(820, 260)
        self.logs_path = Path(logs_path).resolve()
        self.history_path = Path(history_path).resolve()
        self.downloads_path = Path(downloads_path).resolve()
        self.base_dir = base_dir.resolve()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Arquivos e pastas do programa")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        hint = QLabel("Estes caminhos são automáticos. Use esta tela apenas para abrir e conferir os arquivos gerados.")
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        layout.addLayout(grid)

        self._add_path_row(grid, 0, "Logs:", self.logs_path, "Abrir logs", lambda: self._open_directory(self.logs_path))
        self._add_path_row(grid, 1, "Downloads:", self.downloads_path, "Abrir downloads", lambda: self._open_directory(self.downloads_path))
        self._add_path_row(grid, 2, "Histórico:", self.history_path, "Abrir histórico", self._open_history_file)
        self._add_path_row(grid, 3, "Pasta do app:", self.base_dir, "Abrir pasta", lambda: self._open_directory(self.base_dir))

        close_btn = QPushButton("Fechar")
        close_btn.setObjectName("GhostButton")
        close_btn.clicked.connect(self.accept)
        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _add_path_row(self, grid: QGridLayout, row: int, label: str, path: Path, button_text: str, callback) -> None:
        label_widget = QLabel(label)
        label_widget.setObjectName("FieldLabel")
        path_input = QLineEdit(str(path))
        path_input.setReadOnly(True)
        path_input.setCursorPosition(0)
        button = QPushButton(button_text)
        button.setObjectName("GhostButton")
        button.clicked.connect(callback)
        grid.addWidget(label_widget, row, 0)
        grid.addWidget(path_input, row, 1)
        grid.addWidget(button, row, 2)

    def _open_directory(self, path: Path) -> None:
        directory = path.resolve()
        directory.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(directory)))

    def _open_history_file(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_path.exists():
            self.history_path.write_text('{"baixadas": {}, "arquivos": {}, "nao_encontradas": {}}', encoding="utf-8")
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.history_path)))


class TracklistDialog(QDialog):
    def __init__(self, parent, tracklist_path: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar Tracklist")
        self.resize(840, 620)
        self.setMinimumSize(720, 540)
        self.tracklist_path = Path(tracklist_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Tracklist")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        hint = QLabel(
            "Adicione, edite ou cole suas músicas abaixo. Use uma música por linha. "
            "Você pode informar só o nome ou usar Artista - Título para melhorar a precisão."
        )
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        editor_panel = QFrame()
        editor_panel.setObjectName("Panel")
        editor_panel_layout = QVBoxLayout(editor_panel)
        editor_panel_layout.setContentsMargins(14, 12, 14, 12)
        editor_panel_layout.setSpacing(10)

        editor_header = QHBoxLayout()
        editor_header.setContentsMargins(0, 0, 0, 0)
        editor_header.setSpacing(8)
        music_icon = QLabel("♪")
        music_icon.setObjectName("MusicIcon")
        music_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor_title = QLabel("Tracklist")
        editor_title.setObjectName("SectionTitle")
        editor_header.addWidget(music_icon)
        editor_header.addWidget(editor_title)
        editor_header.addStretch(1)
        editor_panel_layout.addLayout(editor_header)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Kill Me Slow (Agents Of Time Remix)\nArtista - Título")
        self.editor.textChanged.connect(self._refresh_status)
        editor_panel_layout.addWidget(self.editor, 1)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(10)
        self.status_label = QLabel("0 faixas")
        self.status_label.setObjectName("HelpLabel")
        footer.addWidget(self.status_label, 1)
        clear_btn = QPushButton("Limpar")
        clear_btn.setObjectName("GhostButton")
        clear_btn.clicked.connect(self.editor.clear)
        footer.addWidget(clear_btn)
        editor_panel_layout.addLayout(footer)
        layout.addWidget(editor_panel, 1)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(10)
        actions.addStretch(1)
        cancel_btn = QPushButton("Fechar")
        cancel_btn.setObjectName("GhostButton")
        cancel_btn.setFixedSize(134, 44)
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Salvar lista")
        save_btn.setObjectName("StartButton")
        save_btn.setFixedSize(134, 44)
        save_btn.clicked.connect(self._save_and_close)
        actions.addWidget(cancel_btn)
        actions.addWidget(save_btn)
        layout.addLayout(actions)

        self._load_tracks()

    def _load_tracks(self) -> None:
        if self.tracklist_path.exists():
            self.editor.setPlainText(self.tracklist_path.read_text(encoding="utf-8-sig").strip())
        self._refresh_status()

    def _normalized_tracks(self) -> list[str]:
        return [line.strip() for line in self.editor.toPlainText().splitlines() if line.strip()]

    def _refresh_status(self) -> None:
        tracks = self._normalized_tracks()
        without_artist = [track for track in tracks if " - " not in track]
        plural = "faixa" if len(tracks) == 1 else "faixas"
        if not tracks:
            self.status_label.setText("Nenhuma faixa cadastrada.")
            self.status_label.setObjectName("WarningLabel")
        elif without_artist:
            self.status_label.setText(f"{len(tracks)} {plural} salvas. Dica: incluir o artista pode melhorar a busca.")
            self.status_label.setObjectName("HelpLabel")
        else:
            self.status_label.setText(f"{len(tracks)} {plural} prontas para execução.")
            self.status_label.setObjectName("SuccessLabel")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _save_and_close(self) -> None:
        tracks = self._normalized_tracks()
        self.tracklist_path.parent.mkdir(parents=True, exist_ok=True)
        content = "\n".join(tracks)
        if content:
            content += "\n"
        self.tracklist_path.write_text(content, encoding="utf-8")
        self.accept()


class HistoryDialog(QDialog):
    def __init__(self, parent, history_path: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("Histórico")
        self.resize(820, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Músicas no histórico")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        close_btn = QPushButton("Fechar")
        close_btn.setObjectName("GhostButton")
        close_btn.clicked.connect(self.accept)
        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

        self._load_items(history_path)

    def _load_items(self, history_path: str) -> None:
        history = load_history(Path(history_path))
        downloaded = list(history.get("baixadas", {}).values())
        missing = list(history.get("nao_encontradas", {}).values())

        if not downloaded and not missing:
            self._add_item("Histórico ainda vazio.", "#cbd5e1", "#111827")
            return

        for item in downloaded:
            track = item.get("track", "")
            file_name = item.get("file_name", "")
            detail = f"✓ Baixada - {track}"
            if file_name:
                detail += f" ({file_name})"
            self._add_item(detail, "#bbf7d0", "#10291b")

        for item in missing:
            track = item.get("track", "")
            attempts = item.get("attempts", 0)
            detail = f"✕ Não encontrada - {track} ({attempts} tentativa(s))"
            self._add_item(detail, "#fecaca", "#3b1118")

    def _add_item(self, text: str, color: str, bg: str) -> None:
        item = QListWidgetItem(text)
        item.setForeground(QColor(color))
        item.setBackground(QColor(bg))
        self.list_widget.addItem(item)


class TrackHunterWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TrackHunter v2.0")
        self.setWindowIcon(QIcon(str(asset_path("app_icon.png"))))
        self.resize(1180, 820)
        self.setMinimumSize(980, 800)

        self.base_dir = self._resolve_base_dir()
        self.worker: BotWorker | None = None
        self.settings = QSettings("TrackHunter", "TrackHunter")
        self.run_counts = {"baixada": 0, "ja_baixada": 0, "nao_encontrada": 0, "erro": 0}
        self.current_track = ""
        self.current_track_index = 0
        self.run_started_at: float | None = None

        self.logs_path = str(self.base_dir / "logs")
        self.history_path = str(self.base_dir / "state" / "track_history.json")
        self.tracklist_path = str(self.base_dir / "state" / "tracklist.txt")

        self._build_ui()
        self._set_defaults()
        self._load_saved_credentials()

    def _resolve_base_dir(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent.parent

    def _field_label(self, text: str) -> QLabel:
        label = QLabel(text if text.endswith(":") else f"{text}:")
        label.setObjectName("FieldLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        label.setFixedHeight(38)
        label.setFixedWidth(92)
        label.setContentsMargins(0, 0, 0, 0)
        return label

    def _help_label(self, text: str, kind: str = "help") -> QLabel:
        label = QLabel(text)
        object_name = {
            "success": "SuccessLabel",
            "warning": "WarningLabel",
        }.get(kind, "HelpLabel")
        label.setObjectName(object_name)
        label.setWordWrap(True)
        return label

    def _tooltip_badge(self, text: str) -> QLabel:
        badge = QLabel("?")
        badge.setObjectName("TooltipBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setToolTip(text)
        badge.setCursor(Qt.CursorShape.WhatsThisCursor)
        return badge

    def _option_with_tooltip(self, toggle: ToggleSwitch, tooltip: str) -> QWidget:
        toggle.setToolTip(tooltip)
        widget = QWidget()
        option_width = toggle.minimumWidth() + 22
        widget.setMinimumWidth(option_width)
        widget.setMaximumWidth(option_width)
        widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.addWidget(toggle)
        layout.addWidget(self._tooltip_badge(tooltip))
        widget.setLayout(layout)
        widget.setMinimumHeight(32)
        return widget

    def _clear_grid(self, layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.setParent(None)
            elif child_layout:
                while child_layout.count():
                    child = child_layout.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)

    def _place_authentication(self, compact: bool) -> None:
        self._clear_grid(self.auth_grid)
        if compact:
            self.auth_grid.addWidget(self.email_label, 0, 0)
            self.auth_grid.addWidget(self.email_input, 0, 1)
            self.auth_grid.addWidget(self.password_label, 1, 0)
            self.auth_grid.addWidget(self.password_input, 1, 1)
            self.auth_grid.setColumnStretch(1, 1)
            self.auth_grid.setColumnStretch(3, 0)
            return

        self.auth_grid.addWidget(self.email_label, 0, 0)
        self.auth_grid.addWidget(self.email_input, 0, 1)
        self.auth_grid.addWidget(self.password_label, 0, 2)
        self.auth_grid.addWidget(self.password_input, 0, 3)
        self.auth_grid.setColumnStretch(1, 1)
        self.auth_grid.setColumnStretch(3, 1)

    def _place_options(self, compact: bool) -> None:
        self._clear_grid(self.options_grid)
        if compact:
            placements = [
                (self.manual_option, 0, 0),
                (self.assisted_option, 1, 0),
                (self.force_option, 2, 0),
                (self.retry_option, 3, 0),
                (self.timeout_widget, 4, 0),
                (self.settings_btn, 4, 1),
            ]
            for widget, row, column in placements:
                self.options_grid.addWidget(widget, row, column, alignment=Qt.AlignmentFlag.AlignLeft)
            self.options_grid.setColumnStretch(0, 0)
            self.options_grid.setColumnStretch(1, 0)
            return

        placements = [
            (self.manual_option, 0, 0),
            (self.assisted_option, 0, 1),
            (self.force_option, 1, 0),
            (self.retry_option, 1, 1),
            (self.timeout_widget, 2, 0),
            (self.settings_btn, 2, 1),
        ]

        for widget, row, column in placements:
            self.options_grid.addWidget(widget, row, column, alignment=Qt.AlignmentFlag.AlignLeft)
        self.options_grid.setColumnStretch(0, 0)
        self.options_grid.setColumnStretch(1, 0)

    def _place_summary(self, compact: bool) -> None:
        self._clear_grid(self.summary_grid)
        for column in range(6):
            self.summary_grid.setColumnStretch(column, 0)

        cards = [self.downloaded_card, self.skipped_card, self.missing_card, self.error_card]
        if compact:
            for index, card in enumerate(cards):
                self.summary_grid.addWidget(card, 0, index, alignment=Qt.AlignmentFlag.AlignCenter)
            self.summary_grid.addWidget(self.history_summary_label, 1, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
            self.summary_grid.addWidget(self.history_btn, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            for index, card in enumerate(cards):
                self.summary_grid.addWidget(card, 0, index, alignment=Qt.AlignmentFlag.AlignCenter)
            self.summary_grid.addWidget(self.history_summary_label, 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)
            self.summary_grid.addWidget(self.history_btn, 0, 5, alignment=Qt.AlignmentFlag.AlignCenter)
        self.summary_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _apply_responsive_layout(self) -> None:
        width = self.width()
        compact = width < 1500
        self._place_authentication(compact)
        self._place_options(compact)
        self._place_summary(compact)
        panel_height = 176 if compact else 202
        self.credentials_panel.setMinimumHeight(panel_height)
        self.options_panel.setMinimumHeight(panel_height)
        self.files_panel.setMinimumHeight(panel_height)
        self.summary_panel.setMinimumHeight(panel_height)
        self.log_panel.setMinimumWidth(0)
        self.log_panel.setMaximumWidth(16777215)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "options_grid"):
            self._apply_responsive_layout()

    def _prepare_input(self, line_edit: QLineEdit) -> None:
        palette = line_edit.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#B0B0B0"))
        line_edit.setPalette(palette)

    def _validate_tracklist_status(self) -> None:
        path = Path(self.tracklist_path)
        if not path.exists():
            self.tracklist_status_label.setText("Nenhuma tracklist salva ainda.")
            self.tracklist_status_label.setObjectName("WarningLabel")
            self.tracklist_status_label.style().unpolish(self.tracklist_status_label)
            self.tracklist_status_label.style().polish(self.tracklist_status_label)
            return

        try:
            track_count = len(load_tracklist(path))
        except Exception:
            self.tracklist_status_label.setText("Arquivo inválido ou vazio.")
            self.tracklist_status_label.setObjectName("WarningLabel")
        else:
            plural = "faixa detectada" if track_count == 1 else "faixas detectadas"
            self.tracklist_status_label.setText(f"Tracklist salva: {track_count} {plural}.")
            self.tracklist_status_label.setObjectName("SuccessLabel")

        self.tracklist_status_label.style().unpolish(self.tracklist_status_label)
        self.tracklist_status_label.style().polish(self.tracklist_status_label)

    def _load_saved_credentials(self) -> None:
        save_credentials = self.settings.value("credentials/save", False, type=bool)
        self.save_credentials_check.blockSignals(True)
        self.save_credentials_check.setChecked(save_credentials)
        self.save_credentials_check.blockSignals(False)
        if save_credentials:
            self.email_input.setText(self.settings.value("credentials/email", "", type=str))
            self.password_input.setText(self.settings.value("credentials/password", "", type=str))

    def _sync_saved_credentials(self) -> None:
        if self.save_credentials_check.isChecked():
            self.settings.setValue("credentials/save", True)
            self.settings.setValue("credentials/email", self.email_input.text().strip())
            self.settings.setValue("credentials/password", self.password_input.text())
            return

        self.settings.setValue("credentials/save", False)
        self.settings.remove("credentials/email")
        self.settings.remove("credentials/password")

    def closeEvent(self, event) -> None:
        self._sync_saved_credentials()
        super().closeEvent(event)

    def _reset_progress(self) -> None:
        self.progress_bar.setValue(0)
        self.progress_text.setText("0/0 Faixas - 0.0%")

    def _set_progress(self, current: int, total: int, percent: float) -> None:
        self.progress_bar.setValue(round(percent))
        self.progress_text.setText(f"{current}/{total} Faixas - {percent:.1f}%")

    def _reset_summary(self) -> None:
        self.run_counts = {"baixada": 0, "ja_baixada": 0, "nao_encontrada": 0, "erro": 0}
        self.current_track = ""
        self.current_track_index = 0
        self._refresh_summary_cards()

    def _refresh_summary_cards(self) -> None:
        self.downloaded_card.set_value(self.run_counts["baixada"])
        self.skipped_card.set_value(self.run_counts["ja_baixada"])
        self.missing_card.set_value(self.run_counts["nao_encontrada"])
        self.error_card.set_value(self.run_counts["erro"])

    def _refresh_history_summary(self) -> None:
        try:
            history = load_history(Path(self.history_path))
        except Exception:
            self.history_summary_label.setText("Histórico indisponível.")
            return

        downloaded = len(history.get("baixadas", {}))
        missing = len(history.get("nao_encontradas", {}))
        self.history_summary_label.setText(f"Histórico: {downloaded} baixadas, {missing} não encontradas pendentes.")

    def _record_track_status(self, status: str) -> None:
        if status not in self.run_counts:
            status = "erro"
        self.run_counts[status] += 1
        self._refresh_summary_cards()

        labels = {
            "baixada": ("✓", "Baixada", "#bbf7d0", "#10291b"),
            "ja_baixada": ("!", "Ignorada", "#fed7aa", "#32210e"),
            "nao_encontrada": ("✕", "Não encontrada", "#fecaca", "#3b1118"),
            "erro": ("✕", "Erro", "#fecaca", "#3b1118"),
        }
        marker, label, color, bg = labels[status]
        track = self.current_track or "Faixa"
        prefix = f"Faixa {self.current_track_index} - " if self.current_track_index else ""
        self._add_log_line(f"{marker} {prefix}{track} - {label}", color_override=color, bg_override=bg)

    def _add_log_line(self, line: str, color_override: str | None = None, bg_override: str | None = None) -> None:
        clean_line = line.strip()
        if not clean_line:
            return

        level, color, bg, icon = self._classify_log_line(clean_line)
        if color_override:
            color = color_override
        if bg_override:
            bg = bg_override
        item = QListWidgetItem(icon, clean_line)
        item.setData(Qt.ItemDataRole.UserRole, level)
        item.setForeground(QColor(color))
        item.setBackground(QColor(bg))
        item.setSizeHint(QSize(0, 22))
        self.output.addItem(item)
        self.output.scrollToBottom()

    def _classify_log_line(self, line: str):
        lowered = line.lower()
        if "erro" in lowered or "falha" in lowered or "timeout" in lowered:
            return ("erro", "#fecaca", "#3b1118", self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical))
        if "baixada" in lowered or "download iniciado" in lowered or "ok" in lowered or "finalizado" in lowered:
            return ("sucesso", "#bbf7d0", "#10291b", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        if (
            "ignorada" in lowered
            or "historico" in lowered
            or "nao encontrada" in lowered
            or "nenhuma faixa" in lowered
            or "parada solicitada" in lowered
            or "interrompida" in lowered
        ):
            return ("aviso", "#fed7aa", "#32210e", self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning))
        if "buscando" in lowered or "iniciando" in lowered or "login" in lowered or "credenciais" in lowered:
            return ("busca", "#bfdbfe", "#10233d", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        return ("info", "#cbd5e1", "#111827", self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(22, 16, 22, 10)
        root.setSpacing(8)

        logo_pixmap = QPixmap(str(asset_path("logo.png")))
        if logo_pixmap.isNull():
            title = QLabel("TrackHunter")
            title.setStyleSheet("font-size: 28px; font-weight: 800; color: #f8fafc;")
            root.addWidget(title)
        else:
            title = QLabel()
            title.setPixmap(logo_pixmap.scaledToHeight(70, Qt.TransformationMode.SmoothTransformation))
            title.setFixedHeight(76)
            title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            root.addWidget(title)
        subtitle = QLabel("Automação de busca e downloads de músicas no MUZPA")
        subtitle.setObjectName("Hint")
        root.addWidget(subtitle)

        credentials = Panel("Autenticação")
        self.credentials_panel = credentials
        self.email_input = IconLineEdit("person")
        self.email_input.setPlaceholderText("usuario@email.com")
        self.password_input = IconLineEdit("lock", password=True)
        self.password_input.setPlaceholderText("senha")
        self._prepare_input(self.email_input)
        self._prepare_input(self.password_input)

        self.email_label = self._field_label("Usuário")
        self.password_label = self._field_label("Senha")
        self.auth_grid = QGridLayout()
        self.auth_grid.setContentsMargins(0, 0, 0, 0)
        self.auth_grid.setHorizontalSpacing(12)
        self.auth_grid.setVerticalSpacing(8)
        credentials.layout.addLayout(self.auth_grid)

        self.save_credentials_check = ToggleSwitch("Salvar credenciais")
        self.save_credentials_check.setToolTip("Salva usuário e senha neste Windows para preencher automaticamente na próxima abertura.")
        self.save_credentials_check.toggled.connect(self._sync_saved_credentials)
        credentials_footer = QHBoxLayout()
        credentials_footer.setContentsMargins(0, 0, 0, 0)
        credentials_footer.setSpacing(10)
        credentials_footer.addWidget(self.save_credentials_check)
        credentials_footer.addWidget(self._help_label("As credenciais são criptografadas e salvas apenas no seu computador."), 1)
        credentials.layout.addLayout(credentials_footer)

        files = Panel("Arquivos")
        self.files_panel = files
        files.layout.setContentsMargins(16, 10, 16, 12)
        files.layout.setSpacing(6)
        files_layout = QGridLayout()
        files_layout.setContentsMargins(0, 0, 0, 0)
        files_layout.setHorizontalSpacing(10)
        files_layout.setVerticalSpacing(8)
        files_layout.setRowMinimumHeight(0, 58)
        files_layout.setRowMinimumHeight(1, 58)

        self.downloads_input = IconLineEdit("folder")
        self.downloads_input.setMaximumWidth(620)
        self._prepare_input(self.downloads_input)

        tracklist_btn = QPushButton("Tracklist")
        tracklist_btn.setObjectName("BrowseButton")
        tracklist_btn.setFixedWidth(132)
        tracklist_btn.clicked.connect(self.open_tracklist_editor)
        downloads_btn = QPushButton("Selecionar")
        downloads_btn.setObjectName("BrowseButton")
        downloads_btn.setFixedWidth(132)
        downloads_btn.clicked.connect(lambda: self._pick_directory(self.downloads_input))

        tracklist_stack = QVBoxLayout()
        tracklist_stack.setContentsMargins(0, 0, 0, 0)
        tracklist_stack.setSpacing(4)
        self.tracklist_help_label = self._help_label("Edite a lista diretamente no software. Formato recomendado: Artista - Título.")
        self.tracklist_status_label = self._help_label("Abra a Tracklist para cadastrar músicas.", "warning")
        tracklist_stack.addWidget(self.tracklist_help_label)
        tracklist_stack.addWidget(self.tracklist_status_label)

        files_layout.addWidget(self._field_label("Tracklist"), 0, 0)
        files_layout.addLayout(tracklist_stack, 0, 1)
        files_layout.addWidget(tracklist_btn, 0, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        downloads_stack = QVBoxLayout()
        downloads_stack.setContentsMargins(0, 0, 0, 0)
        downloads_stack.setSpacing(4)
        downloads_stack.addWidget(self.downloads_input, alignment=Qt.AlignmentFlag.AlignLeft)
        downloads_stack.addWidget(self._help_label("Selecione a pasta onde deseja salvar as músicas baixadas."))

        files_layout.addWidget(self._field_label("Downloads"), 1, 0)
        files_layout.addLayout(downloads_stack, 1, 1)
        files_layout.addWidget(downloads_btn, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)
        files_layout.setColumnStretch(1, 1)
        files.layout.addLayout(files_layout)

        options = Panel("Opções")
        self.options_panel = options
        options.layout.setContentsMargins(16, 14, 16, 22)
        self.options_grid = QGridLayout()
        self.options_grid.setContentsMargins(0, 0, 0, 0)
        self.options_grid.setHorizontalSpacing(18)
        self.options_grid.setVerticalSpacing(8)
        self.options_grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        manual_login_tip = "Abre o navegador para login manual se o automático falhar."
        assisted_search_tip = "Permite acompanhar a busca no navegador."
        force_download_tip = "Baixa novamente, mesmo se já existir no histórico."
        retry_missing_tip = "Busca apenas músicas pendentes como não encontradas."
        timeout_tip = "Tempo máximo de espera para carregar o login."

        self.manual_login_check = ToggleSwitch("Login manual")
        self.headless_check = ToggleSwitch("Busca assistida")
        self.force_download_check = ToggleSwitch("Baixar novamente")
        self.retry_missing_check = ToggleSwitch("Somente não encontradas")

        self.timeout_spin = MillisecondsStepper(10000, 600000, 5000)
        self.timeout_spin.setToolTip(timeout_tip)

        self.settings_btn = QPushButton("Arquivos")
        self.settings_btn.setObjectName("GhostButton")
        self.settings_btn.setFixedWidth(120)
        self.settings_btn.clicked.connect(self.open_settings)

        self.manual_option = self._option_with_tooltip(self.manual_login_check, manual_login_tip)
        self.assisted_option = self._option_with_tooltip(self.headless_check, assisted_search_tip)
        self.force_option = self._option_with_tooltip(self.force_download_check, force_download_tip)
        self.retry_option = self._option_with_tooltip(self.retry_missing_check, retry_missing_tip)
        self.timeout_widget = QWidget()
        self.timeout_widget.setMinimumHeight(38)
        self.timeout_widget.setMinimumWidth(260)
        self.timeout_widget.setMaximumWidth(354)
        self.timeout_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        timeout_layout = QHBoxLayout()
        timeout_layout.setContentsMargins(0, 0, 0, 0)
        timeout_layout.setSpacing(4)
        timeout_label = self._field_label("Timeout Login")
        timeout_label.setToolTip(timeout_tip)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self._tooltip_badge(timeout_tip))
        timeout_layout.addWidget(self.timeout_spin)
        self.timeout_widget.setLayout(timeout_layout)
        options.layout.addLayout(self.options_grid)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.start_btn = QPushButton("Iniciar")
        self.start_btn.setObjectName("StartButton")
        self.stop_btn = QPushButton("Parar")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_bot)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.start_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        controls.addStretch(1)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)

        summary_panel = Panel("Resumo")
        self.summary_panel = summary_panel
        summary_panel.layout.setContentsMargins(18, 14, 18, 14)
        summary_panel.layout.setSpacing(10)
        self.summary_grid = QGridLayout()
        self.summary_grid.setContentsMargins(0, 0, 0, 0)
        self.summary_grid.setHorizontalSpacing(10)
        self.summary_grid.setVerticalSpacing(10)
        self.downloaded_card = SummaryCard("Baixadas", "#86efac")
        self.skipped_card = SummaryCard("Ignoradas", "#fbbf24")
        self.missing_card = SummaryCard("Não encontradas", "#fca5a5")
        self.error_card = SummaryCard("Erros", "#f87171")
        self.history_summary_label = QLabel("Histórico: 0 baixadas, 0 não encontradas pendentes.")
        self.history_summary_label.setObjectName("HistorySummary")
        self.history_summary_label.setMinimumWidth(210)
        self.history_summary_label.setMaximumWidth(250)
        self.history_summary_label.setWordWrap(True)
        self.history_btn = QPushButton("Ver histórico")
        self.history_btn.setObjectName("GhostButton")
        self.history_btn.setFixedWidth(136)
        self.history_btn.clicked.connect(self.open_history)
        summary_panel.layout.addLayout(self.summary_grid)

        log_panel = Panel("Log de execução")
        self.log_panel = log_panel
        log_panel.setFixedHeight(150)
        log_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.output = QListWidget()
        self.output.setAlternatingRowColors(False)
        self.output.setMinimumHeight(70)
        self.output.setAutoScroll(True)
        self.output.setSpacing(1)
        self.output.setIconSize(QSize(16, 16))
        log_panel.layout.addWidget(self.output)

        progress_row = QHBoxLayout()
        progress_row.setContentsMargins(0, 0, 0, 0)
        progress_row.setSpacing(12)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        self.progress_text = QLabel("0/0 Faixas - 0.0%")
        self.progress_text.setObjectName("ProgressText")
        self.progress_text.setMinimumWidth(176)
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.progress_text)

        dashboard_grid = QGridLayout()
        dashboard_grid.setContentsMargins(0, 0, 0, 0)
        dashboard_grid.setHorizontalSpacing(10)
        dashboard_grid.setVerticalSpacing(8)
        dashboard_grid.addWidget(credentials, 0, 0)
        dashboard_grid.addWidget(options, 0, 1)
        dashboard_grid.addWidget(files, 1, 0)
        dashboard_grid.addWidget(summary_panel, 1, 1)
        dashboard_grid.setColumnStretch(0, 1)
        dashboard_grid.setColumnStretch(1, 1)
        dashboard_grid.setRowStretch(0, 1)
        dashboard_grid.setRowStretch(1, 1)

        root.addLayout(dashboard_grid)
        root.addLayout(controls)
        root.addLayout(progress_row)
        root.addWidget(log_panel)
        root.addStretch(1)
        self._apply_responsive_layout()

    def _set_defaults(self) -> None:
        self.downloads_input.setText(str(self.base_dir / "downloads"))
        self.manual_login_check.setChecked(False)
        self.timeout_spin.setValue(30000)
        self._ensure_tracklist_file()
        self._validate_tracklist_status()
        self._reset_summary()
        self._refresh_history_summary()

    def _ensure_tracklist_file(self) -> None:
        path = Path(self.tracklist_path)
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        legacy_path = self.base_dir / "tracklist.txt"
        if legacy_path.exists():
            path.write_text(legacy_path.read_text(encoding="utf-8-sig"), encoding="utf-8")
            return
        path.write_text("", encoding="utf-8")

    def open_settings(self) -> None:
        dlg = SettingsDialog(
            self,
            self.logs_path,
            self.history_path,
            self.downloads_input.text().strip() or str(self.base_dir / "downloads"),
            self.base_dir,
        )
        dlg.exec()

    def open_history(self) -> None:
        HistoryDialog(self, self.history_path).exec()

    def open_tracklist_editor(self) -> None:
        dlg = TracklistDialog(self, self.tracklist_path)
        if dlg.exec():
            self._validate_tracklist_status()

    def _pick_directory(self, target: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta", target.text() or str(self.base_dir))
        if path:
            target.setText(path)

    def start_bot(self) -> None:
        if self.worker and self.worker.isRunning():
            return

        tracklist = self.tracklist_path
        downloads = self.downloads_input.text().strip()
        logs = self.logs_path.strip()
        history = self.history_path.strip()

        if not tracklist or not downloads or not logs or not history:
            QMessageBox.warning(self, "Campos obrigatórios", "Preencha a tracklist, downloads e configurações.")
            return

        if not self.retry_missing_check.isChecked():
            try:
                load_tracklist(Path(tracklist))
            except Exception:
                QMessageBox.warning(
                    self,
                    "Tracklist",
                    "A tracklist está vazia. Clique em 'Tracklist' e cadastre pelo menos uma música antes de iniciar.",
                )
                return

        email = self.email_input.text().strip()
        password = self.password_input.text()
        wants_manual_login = self.manual_login_check.isChecked()
        has_credentials = bool(email and password)

        if not wants_manual_login and not has_credentials:
            QMessageBox.warning(self, "Credenciais", "Informe usuário e senha, ou marque 'Login manual'.")
            return
        self._sync_saved_credentials()

        Path(downloads).mkdir(parents=True, exist_ok=True)
        Path(logs).mkdir(parents=True, exist_ok=True)
        Path(history).parent.mkdir(parents=True, exist_ok=True)

        args = [
            "--tracklist",
            tracklist,
            "--downloads",
            downloads,
            "--logs",
            logs,
            "--history",
            history,
            "--wait-login",
            str(self.timeout_spin.value()),
        ]

        if wants_manual_login and not has_credentials:
            args.append("--manual-login")
        # "Busca assistida": navegador visível para acompanhar. Se desmarcado, roda headless.
        if not self.headless_check.isChecked():
            args.append("--headless")
        if self.force_download_check.isChecked():
            args.append("--force-download")
        if self.retry_missing_check.isChecked():
            args.append("--retry-missing-only")

        self.output.clear()
        self.run_started_at = time.perf_counter()
        self._reset_progress()
        self._reset_summary()
        self._refresh_history_summary()
        self._add_log_line("Iniciando TrackHunter...")
        self._add_log_line(f"Pasta de logs: {logs}")
        if has_credentials:
            self._add_log_line("Credenciais detectadas: login automático habilitado.")
        elif wants_manual_login:
            self._add_log_line("Login manual habilitado.")

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = BotWorker(args=args, email=email, password=password)
        self.worker.output.connect(self._append_output)
        self.worker.finished_with_code.connect(self._on_process_finished)
        self.worker.start()

    def stop_bot(self) -> None:
        if not self.worker or not self.worker.isRunning():
            return
        self.worker.request_stop()
        self.stop_btn.setEnabled(False)
        self._add_log_line("Parada solicitada. Finalizando etapa atual com segurança...")

    def _append_output(self, text: str) -> None:
        for line in text.splitlines():
            search = re.search(r"\[(\d+)/(\d+)\]\s+Buscando:\s*(.+)", line)
            if search:
                self.current_track_index = int(search.group(1))
                self.current_track = search.group(3).strip()
                self._add_log_line(line)
                continue

            progress = re.search(r"Progresso:\s*(\d+)/(\d+)\s*\(([\d.]+)%\)", line)
            if progress:
                current = int(progress.group(1))
                total = int(progress.group(2))
                percent = float(progress.group(3))
                self._set_progress(current, total, percent)

            status = re.search(r"Status:\s*([a-z_]+)", line)
            if status:
                self._record_track_status(status.group(1))
                continue

            self._add_log_line(line)

    def _on_process_finished(self, exit_code: int) -> None:
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._refresh_history_summary()
        elapsed = None if self.run_started_at is None else time.perf_counter() - self.run_started_at
        self._add_log_line(f"Processo finalizado. Código: {exit_code}")
        self._add_log_line(f"Tempo de execução: {format_duration(elapsed)}")
        self.run_started_at = None


def main() -> None:
    set_windows_app_id()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(asset_path("app_icon.png"))))
    app.setStyleSheet(APP_STYLE)
    win = TrackHunterWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


