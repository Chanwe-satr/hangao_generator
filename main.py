#!/usr/bin/env python
"""交通执法文书自动生成系统 — 桌面版"""
import sys
from PySide6.QtWidgets import QApplication
import qdarktheme
from ui.main_window import MainWindow
from ui.style import apply_app_style

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("函告生成系统")
    qdarktheme.setup_theme("light")
    apply_app_style(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
