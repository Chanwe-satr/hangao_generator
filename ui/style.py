from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

_EXTRA_QSS = """
* {
    font-size: 12px;
}

QMainWindow {
    background: #f4f7fb;
}

QTabWidget::pane {
    border: 1px solid #d7dfeb;
    border-radius: 14px;
    background: #fbfdff;
    margin-top: 8px;
}

QTabBar::tab {
    background: transparent;
    color: #5d6b82;
    border: none;
    border-radius: 10px;
    padding: 6px 14px;
    margin: 0 4px 6px 0;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: #1f6feb;
    color: white;
}

QTabBar::tab:hover:!selected {
    background: #e8f0ff;
    color: #204a87;
}

QWidget[page="true"] {
    background: transparent;
}

QGroupBox {
    border: 1px solid #d8e0ec;
    border-radius: 14px;
    margin-top: 12px;
    padding: 12px 12px 10px 12px;
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #ffffff,
        stop: 1 #f6f9ff
    );
    font-weight: 700;
    color: #22324d;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #31507e;
}

QLabel {
    color: #31425f;
}

QLineEdit,
QDateEdit,
QComboBox,
QSpinBox,
QTextEdit,
QPlainTextEdit,
QTableView {
    border: 1px solid #d6deea;
    border-radius: 8px;
    background: white;
    padding: 4px 8px;
    selection-background-color: #d8e8ff;
    selection-color: #183153;
}

QLineEdit:focus,
QDateEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QTableView:focus {
    border: 1px solid #1f6feb;
}

QLineEdit[readOnly="true"] {
    background: #f7f9fc;
    color: #5d6b82;
}

QCalendarWidget {
    min-width: 320px;
    min-height: 260px;
    font-size: 14px;
}

QCalendarWidget QToolButton::menu-indicator {
    image: none;
}

QCalendarWidget QTableView {
    border: none;
    padding: 0px;
    border-radius: 0px;
}

QCalendarWidget QAbstractItemView:enabled {
    selection-background-color: #1f6feb;
    selection-color: white;
}

QPushButton {
    border: none;
    border-radius: 8px;
    background: #e8eff9;
    color: #26415f;
    padding: 5px 12px;
    font-weight: 600;
}

QPushButton:hover {
    background: #dbe8fb;
}

QPushButton:pressed {
    background: #c9dcfa;
}

QPushButton:disabled {
    background: #eef2f7;
    color: #95a3b8;
}

QPushButton[role="primary"] {
    background: #1f6feb;
    color: white;
}

QPushButton[role="primary"]:hover {
    background: #1559c1;
}

QPushButton[role="danger"] {
    background: #fff1f0;
    color: #c53b32;
}

QPushButton[role="danger"]:hover {
    background: #ffe2e0;
}

QCheckBox {
    spacing: 6px;
    color: #31425f;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #b8c6da;
    background: white;
}

QCheckBox::indicator:checked {
    border: 1px solid #1f6feb;
    background: #1f6feb;
}

QHeaderView::section {
    background: #eef4fb;
    color: #3d4d67;
    border: none;
    border-bottom: 1px solid #dbe4f0;
    padding: 6px;
    font-weight: 700;
}

QTableView {
    gridline-color: #edf2f8;
    alternate-background-color: #f8fbff;
}

QTableView::item {
    padding: 4px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 0 4px 0;
}

QScrollBar::handle:vertical {
    background: #c8d5e6;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #aebfd8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical,
QScrollBar:horizontal,
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    border: none;
    width: 0px;
    height: 0px;
}

QTextEdit[logView="true"],
QPlainTextEdit[logView="true"] {
    background: #0f1728;
    color: #dce7fb;
    border: 1px solid #1c2a44;
    font-family: "Consolas", "Microsoft YaHei UI";
    font-size: 11px;
}

QProgressBar {
    border: 1px solid #d6deea;
    border-radius: 6px;
    background: white;
    height: 14px;
    text-align: center;
}

QProgressBar::chunk {
    background: #1f6feb;
    border-radius: 5px;
}

QSpinBox {
    min-width: 60px;
}
"""


def apply_app_style(app: QApplication) -> None:
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f4f7fb"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f8fbff"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e8eff9"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#d8e8ff"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#183153"))
    app.setPalette(palette)
    app.setStyleSheet(f"{app.styleSheet()}\n{_EXTRA_QSS}")
