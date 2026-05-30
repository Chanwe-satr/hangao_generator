import os
from datetime import datetime

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.worker import GeneratorWorker
from utils.cache import load_settings, save_settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("函告生成系统 v2.0")
        self.resize(720, 600)
        self._thread: QThread | None = None
        self._worker: GeneratorWorker | None = None
        self._running = False

        self._setup_menu()
        self._setup_ui()
        self._load_cached_settings()
        self._set_state_idle()

    # --- menu ---

    def _setup_menu(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("文件(&F)")
        exit_action = QAction("退出(&Q)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = mb.addMenu("帮助(&H)")
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_about(self) -> None:
        QMessageBox.about(self, "关于", "函告生成系统 v2.0\n\n交通执法文书自动生成工具\n基于 PySide6")

    # --- ui layout ---

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)

        root.addWidget(self._build_config_group())
        root.addWidget(self._build_progress_group())
        root.addWidget(self._build_log_group(), 1)
        root.addLayout(self._build_control_bar())

    def _build_config_group(self) -> QGroupBox:
        gb = QGroupBox("配置")
        layout = QVBoxLayout(gb)

        # --- Excel file row ---
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Excel文件:"))
        self._excel_edit = QLineEdit()
        self._excel_edit.setPlaceholderText("选择 函告.xls 或 函告.xlsx ...")
        row1.addWidget(self._excel_edit, 1)
        excel_btn = QPushButton("浏览...")
        excel_btn.clicked.connect(self._browse_excel)
        row1.addWidget(excel_btn)
        layout.addLayout(row1)

        # --- case number row ---
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("起始案号:"))
        self._case_spin = QSpinBox()
        self._case_spin.setRange(1, 999999)
        self._case_spin.setValue(1)
        row2.addWidget(self._case_spin)
        row2.addStretch(1)

        row2.addWidget(QLabel("模板目录:"))
        self._template_edit = QLineEdit()
        self._template_edit.setPlaceholderText("选择模板目录...")
        row2.addWidget(self._template_edit, 1)
        template_btn = QPushButton("浏览...")
        template_btn.clicked.connect(self._browse_template_dir)
        row2.addWidget(template_btn)
        layout.addLayout(row2)

        # --- token input row ---
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Cookie:"))
        self._token_edit = QPlainTextEdit()
        self._token_edit.setPlaceholderText("在此粘贴 cookie")
        self._token_edit.setFixedHeight(50)
        row3.addWidget(self._token_edit, 1)
        layout.addLayout(row3)

        return gb

    def _build_progress_group(self) -> QGroupBox:
        gb = QGroupBox("进度")
        layout = QVBoxLayout(gb)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        layout.addWidget(self._progress_bar)

        self._current_label = QLabel("就绪")
        layout.addWidget(self._current_label)

        return gb

    def _build_log_group(self) -> QGroupBox:
        gb = QGroupBox("日志")
        layout = QVBoxLayout(gb)

        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setProperty("logView", True)
        font = QFont("Consolas", 8)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._log_view.setFont(font)
        self._log_view.setMaximumBlockCount(5000)
        layout.addWidget(self._log_view, 1)

        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self._log_view.clear)
        layout.addWidget(clear_btn)

        return gb

    def _build_control_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._run_btn = QPushButton("▶ 开始生成")
        self._run_btn.setProperty("role", "primary")
        self._run_btn.setMinimumHeight(28)
        self._run_btn.clicked.connect(self._on_start)
        row.addWidget(self._run_btn, 1)

        self._stop_btn = QPushButton("■ 停止")
        self._stop_btn.setMinimumHeight(28)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_stop)
        row.addWidget(self._stop_btn, 1)

        self._status_label = QLabel("就绪")
        row.addWidget(self._status_label)

        return row

    # --- state management ---

    def _set_state_idle(self) -> None:
        self._running = False
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._excel_edit.setEnabled(True)
        self._case_spin.setEnabled(True)
        self._token_edit.setEnabled(True)
        self._template_edit.setEnabled(True)

    def _set_state_running(self) -> None:
        self._running = True
        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._excel_edit.setEnabled(False)
        self._case_spin.setEnabled(False)
        self._token_edit.setEnabled(False)
        self._template_edit.setEnabled(False)
        self._status_label.setText("运行中...")
        self._status_label.setStyleSheet("color: #2196F3; font-weight: bold;")

    def _set_state_done(self, msg: str = "已完成") -> None:
        self._set_state_idle()
        self._status_label.setText(msg)
        self._status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self._progress_bar.setValue(100)

    def _set_state_error(self, msg: str) -> None:
        self._set_state_idle()
        self._status_label.setText(f"错误: {msg}")
        self._status_label.setStyleSheet("color: #F44336; font-weight: bold;")

    # --- cache ---

    def _load_cached_settings(self) -> None:
        s = load_settings()
        if s.get("template_dir"):
            self._template_edit.setText(s["template_dir"])
        if s.get("case_number"):
            self._case_spin.setValue(s["case_number"])
        if s.get("cookie"):
            self._token_edit.setPlainText(s["cookie"])

    def _save_cached_settings(self) -> None:
        save_settings({
            "template_dir": self._template_edit.text().strip(),
            "case_number": self._case_spin.value(),
            "cookie": self._token_edit.toPlainText().strip(),
        })

    # --- slots ---

    def _browse_excel(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xls *.xlsx);;所有文件 (*)",
        )
        if path:
            self._excel_edit.setText(path)

    def _browse_template_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择模板目录")
        if path:
            self._template_edit.setText(path)

    def _on_start(self) -> None:
        excel_path = self._excel_edit.text().strip()
        if not excel_path:
            QMessageBox.warning(self, "提示", "请先选择Excel文件")
            return
        if not os.path.exists(excel_path):
            QMessageBox.warning(self, "提示", f"Excel文件不存在:\n{excel_path}")
            return

        token_text = self._token_edit.toPlainText().strip()
        if not token_text:
            QMessageBox.warning(self, "提示", "请先输入Token")
            return

        case_number = self._case_spin.value()
        template_dir = self._template_edit.text().strip() or "模板"

        self._save_cached_settings()
        self._set_state_running()
        self._log_view.clear()
        self._progress_bar.setValue(0)

        self._append_log("系统初始化...")

        self._thread = QThread(self)
        self._worker = GeneratorWorker(
            excel_path=excel_path,
            case_number=case_number,
            token_text=token_text,
            template_dir=template_dir,
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.log_signal.connect(self._on_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.error_signal.connect(self._on_error)
        self._worker.finished_signal.connect(self._thread.quit)
        self._worker.error_signal.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(lambda: setattr(self, "_thread", None))

        self._thread.start()

    def _on_stop(self) -> None:
        if self._worker:
            self._worker.cancel()
            self._append_log("正在停止...")
            self._stop_btn.setEnabled(False)

    def _on_log(self, msg: str) -> None:
        self._append_log(msg)

    def _on_progress(self, current: int, total: int, plate: str) -> None:
        pct = int(current / total * 100) if total > 0 else 0
        self._progress_bar.setValue(pct)
        self._current_label.setText(f"正在处理: {plate}  ({current}/{total})")

    def _on_finished(self) -> None:
        self._append_log("========== 处理完成 ==========")
        self._set_state_done("已完成")

    def _on_error(self, msg: str) -> None:
        self._append_log(f"!!! 错误: {msg}")
        self._set_state_error(msg)

    def _append_log(self, msg: str) -> None:
        ts = datetime.now().strftime("[%H:%M:%S]")
        self._log_view.appendPlainText(f"{ts} {msg}")

    # --- close event ---

    def closeEvent(self, event) -> None:
        self._save_cached_settings()
        if self._thread and self._thread.isRunning():
            self._append_log("正在关闭，等待线程结束...")
            if self._worker:
                self._worker.cancel()
            self._thread.quit()
            self._thread.wait(5000)
        event.accept()
