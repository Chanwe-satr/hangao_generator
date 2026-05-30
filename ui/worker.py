from PySide6.QtCore import QObject, Signal

from crawl.backend import GeneratorBackend


class GeneratorWorker(QObject):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(
        self,
        excel_path: str,
        case_number: int,
        token_text: str,
        template_dir: str = "模板",
        card_mapping_path: str = "card_mapping.json",
    ):
        super().__init__()
        self._excel_path = excel_path
        self._case_number = case_number
        self._token_text = token_text
        self._template_dir = template_dir
        self._card_mapping_path = card_mapping_path
        self._backend: GeneratorBackend | None = None

    def run(self) -> None:
        try:
            self._backend = GeneratorBackend(
                log_callback=self.log_signal.emit,
                progress_callback=self.progress_signal.emit,
            )
            self._backend.load_token(self._token_text)
            self._backend.set_template_dir(self._template_dir)
            self._backend.load_card_mapping(self._card_mapping_path)
            self._backend.load_excel(self._excel_path)
            self._backend.set_case_number(self._case_number)
            self._backend.process_all()
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

    def cancel(self) -> None:
        if self._backend:
            self._backend.cancel()
