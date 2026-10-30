"""Janela inicial do cliente e verificação assíncrona da API local."""
import sys
import httpx
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from app.shared.constants import APP_NAME, APP_VERSION, API_VERSION
from config.settings import settings


class ConnectionWorker(QObject):
    finished = Signal(bool, str)

    @Slot()
    def check(self) -> None:
        try:
            with httpx.Client(timeout=settings.timeout_seconds, trust_env=False) as client:
                response = client.get(f"{settings.base_url}/health")
                response.raise_for_status()
                payload = response.json()
            if payload.get("status") != "online":
                self.finished.emit(False, "Resposta inesperada do servidor.")
            elif payload.get("api_version") != API_VERSION:
                self.finished.emit(False, "Versão da API incompatível. Atualize o cliente ou o servidor.")
            else:
                self.finished.emit(True, "Servidor conectado. Login será implementado em etapa futura.")
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            self.finished.emit(False, f"Servidor indisponível: {exc}")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_VERSION}")
        self.resize(650, 300)
        self._thread: QThread | None = None
        self._worker: ConnectionWorker | None = None
        self._busy = False
        root = QWidget(self)
        layout = QVBoxLayout(root)
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 23px; font-weight: bold;")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Servidor: {settings.base_url}"))
        self.status = QLabel("Aguardando verificação de conexão...")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QHBoxLayout()
        self.retry = QPushButton("Testar conexão novamente")
        self.retry.clicked.connect(self.check_connection)
        buttons.addWidget(self.retry)
        buttons.addStretch()
        layout.addLayout(buttons)
        layout.addStretch()
        self.setCentralWidget(root)
        self.timer = QTimer(self)
        self.timer.setInterval(10_000)
        self.timer.timeout.connect(self.check_connection)
        self.timer.start()
        QTimer.singleShot(0, self.check_connection)

    @Slot()
    def check_connection(self) -> None:
        if self._busy:
            return
        self._busy = True
        self.retry.setEnabled(False)
        self.status.setText("Verificando servidor...")
        thread = QThread(self)
        worker = ConnectionWorker()
        worker.moveToThread(thread)
        thread.started.connect(worker.check)
        worker.finished.connect(self._on_result)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._thread_finished)
        self._thread, self._worker = thread, worker
        thread.start()

    @Slot(bool, str)
    def _on_result(self, connected: bool, message: str) -> None:
        self.status.setText(("● Conectado — " if connected else "● Desconectado — ") + message)
        self.status.setStyleSheet("color: #167a3a;" if connected else "color: #b42318;")
        self.retry.setEnabled(True)

    @Slot()
    def _thread_finished(self) -> None:
        self._busy = False
        self._thread = None
        self._worker = None

    def closeEvent(self, event) -> None:
        self.timer.stop()
        if self._thread is not None and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(3500)
        super().closeEvent(event)


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
