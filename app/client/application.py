"""Interface principal da Etapa 03: navegação e estado de conexão.

Nenhum módulo operacional é exposto antes da implementação de autenticação.
"""
from __future__ import annotations

import sys
from pathlib import Path

import httpx
from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QScrollArea, QStackedWidget, QVBoxLayout, QWidget, QGridLayout, QSizePolicy,
)

from app.shared.constants import APP_NAME, APP_VERSION, API_VERSION
from config.settings import settings

LOGO = Path(__file__).resolve().parent / 'assets' / 'logo.svg'

LIGHT = '''
QMainWindow, QWidget#root {background:#F5F7FC;color:#202940;}
QFrame#sidebar {background:#171C34;border:0;}
QLabel#brand {color:#FFFFFF;font-size:18px;font-weight:800;}
QLabel#sideCaption {color:#8290B1;font-size:10px;font-weight:700;}
QPushButton#nav {background:transparent;color:#B8C2DF;border:0;border-radius:11px;text-align:left;padding:12px 14px;font-size:13px;}
QPushButton#nav:hover {background:#252E4D;color:#FFFFFF;}
QPushButton#nav[active="true"] {background:#35395F;color:#FFFFFF;font-weight:700;border-left:3px solid #9E8AFF;}
QFrame#header {background:#FFFFFF;border-bottom:1px solid #E8EBF2;}
QLabel#headerTitle {color:#242B42;font-size:17px;font-weight:750;}
QLabel#title {color:#202940;font-size:29px;font-weight:800;}
QLabel#subtitle {color:#768198;font-size:13px;}
QFrame#card {background:#FFFFFF;border:1px solid #E8EBF3;border-radius:17px;}
QLabel#cardTitle {color:#263049;font-size:14px;font-weight:700;}
QLabel#cardValue {color:#283149;font-size:25px;font-weight:800;}
QLabel#muted {color:#8290A6;font-size:12px;}
QPushButton#primary {background:#6956D9;color:white;border:0;border-radius:10px;padding:11px 17px;font-weight:700;}
QPushButton#primary:hover {background:#5744C9;}
QPushButton#secondary {background:#EDF0F8;color:#34405D;border:0;border-radius:10px;padding:11px 17px;font-weight:650;}
QPushButton#secondary:hover {background:#E0E5F1;}
QLabel#statusOk {color:#16805A;font-weight:700;}
QLabel#statusBad {color:#B9414E;font-weight:700;}
'''


class ConnectionWorker(QObject):
    finished = Signal(bool, str, object)

    @Slot()
    def check(self) -> None:
        try:
            with httpx.Client(timeout=settings.timeout_seconds, trust_env=False) as client:
                response = client.get(f'{settings.base_url}/health')
                response.raise_for_status()
                payload = response.json()
            if payload.get('status') != 'online':
                self.finished.emit(False, 'Resposta inesperada do servidor', None)
            elif payload.get('api_version') != API_VERSION:
                self.finished.emit(False, 'Versão da API incompatível', None)
            else:
                with httpx.Client(timeout=settings.timeout_seconds, trust_env=False) as client:
                    stats_response = client.get(f'{settings.base_url}/dashboard/stats')
                    stats_response.raise_for_status()
                    stats = stats_response.json()
                required = ('artworks', 'themes', 'storage_units', 'recent_operations')
                if not isinstance(stats, dict) or any(type(stats.get(k)) is not int or stats[k] < 0 for k in required):
                    raise ValueError('Indicadores inválidos recebidos do servidor')
                self.finished.emit(True, 'Servidor conectado; indicadores atualizados', stats)
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            self.finished.emit(False, f'Servidor indisponível: {exc}', None)


def make_label(text: str, object_name: str = '', wrap: bool = False) -> QLabel:
    label = QLabel(text)
    if object_name:
        label.setObjectName(object_name)
    label.setWordWrap(wrap)
    return label


class MainWindow(QMainWindow):
    """Shell visual da aplicação, sem CRUD ou login fictícios."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f'{APP_NAME} — {APP_VERSION}')
        self.setMinimumSize(840, 560)
        self.resize(1180, 760)
        if LOGO.is_file():
            self.setWindowIcon(QIcon(str(LOGO)))
        self._thread: QThread | None = None
        self._worker: ConnectionWorker | None = None
        self._busy = False
        self._connected = False
        self._current_page = 0
        self._nav_buttons: list[QPushButton] = []
        self._metric_labels: dict[str, QLabel] = {}
        self._metric_notes: dict[str, QLabel] = {}
        self._build_ui()
        self.setStyleSheet(LIGHT)
        self._select_page(0)
        self.timer = QTimer(self)
        self.timer.setInterval(10_000)
        self.timer.timeout.connect(self.check_connection)
        self.timer.start()
        QTimer.singleShot(0, self.check_connection)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName('root')
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName('sidebar')
        self.sidebar.setFixedWidth(240)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(18, 25, 18, 22)
        side.setSpacing(7)
        brand_row = QHBoxLayout()
        logo = QLabel()
        logo.setFixedSize(46, 46)
        if LOGO.is_file():
            from PySide6.QtGui import QPixmap
            logo.setPixmap(QPixmap(str(LOGO)).scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        brand_row.addWidget(logo)
        brand_row.addWidget(make_label('CATÁLOGO\nDE ESTAMPAS', 'brand'))
        brand_row.addStretch()
        side.addLayout(brand_row)
        side.addSpacing(32)
        side.addWidget(make_label('MENU PRINCIPAL', 'sideCaption'))
        nav_items = [
            ('⌂  Visão geral', 0), ('▦  Galeria de artes', 1),
            ('✦  Cadastrar estampa', 2), ('◈  Temas e subtemas', 3),
            ('▤  Armazenamento', 4), ('◷  Histórico', 5),
            ('⚙  Configurações', 6),
        ]
        for label, index in nav_items:
            button = QPushButton(label)
            button.setObjectName('nav')
            button.setCursor(Qt.PointingHandCursor)
            button.setProperty('active', False)
            button.clicked.connect(lambda checked=False, i=index: self._select_page(i))
            side.addWidget(button)
            self._nav_buttons.append(button)
        side.addStretch()
        side.addWidget(make_label('VERSÃO DE DESENVOLVIMENTO', 'sideCaption'))
        version = make_label(APP_VERSION, 'sideCaption')
        side.addWidget(version)
        outer.addWidget(self.sidebar)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        header = QFrame()
        header.setObjectName('header')
        header.setFixedHeight(76)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 0, 28, 0)
        toggle = QPushButton('☰')
        toggle.setObjectName('secondary')
        toggle.setFixedWidth(46)
        toggle.setToolTip('Recolher ou expandir o menu')
        toggle.clicked.connect(self._toggle_sidebar)
        header_layout.addWidget(toggle)
        header_layout.addSpacing(12)
        self.header_title = make_label('Visão geral', 'headerTitle')
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        self.connection_status = make_label('● Verificando...', 'statusBad')
        header_layout.addWidget(self.connection_status)
        main_layout.addWidget(header)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._dashboard())
        for title, detail in [
            ('Galeria de artes', 'A galeria e seus filtros serão ativados no módulo correspondente.'),
            ('Cadastrar estampa', 'O formulário de cadastro será integrado ao banco central em uma etapa futura.'),
            ('Temas e subtemas', 'A organização de temas será disponibilizada após a implementação das permissões.'),
            ('Armazenamento', 'O gerenciamento de HDs, cópias e movimentações será implementado posteriormente.'),
            ('Histórico', 'A auditoria de operações ficará disponível quando os módulos operacionais forem ativados.'),
            ('Configurações', 'A configuração administrativa será disponibilizada com autenticação e permissões.'),
        ]:
            self.stack.addWidget(self._placeholder(title, detail))
        main_layout.addWidget(self.stack, 1)
        outer.addWidget(main, 1)

    def _card(self, key: str, title: str, value: str, note: str) -> QFrame:
        card = QFrame()
        card.setObjectName('card')
        card.setMinimumHeight(136)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 17, 20, 17)
        layout.setSpacing(8)
        layout.addWidget(make_label(title, 'cardTitle'))
        value_label = make_label(value, 'cardValue')
        note_label = make_label(note, 'muted')
        self._metric_labels[key] = value_label
        self._metric_notes[key] = note_label
        layout.addWidget(value_label)
        layout.addWidget(note_label)
        return card

    def _dashboard(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.addWidget(make_label('Bem-vindo ao seu catálogo', 'title'))
        layout.addWidget(make_label('Acompanhe os indicadores reais do seu catálogo.', 'subtitle'))
        grid = QGridLayout()
        grid.setSpacing(16)
        for index, args in enumerate([
            ('artworks', 'Artes cadastradas', '—', 'Aguardando atualização'),
            ('themes', 'Temas organizados', '—', 'Aguardando atualização'),
            ('storage_units', 'Unidades disponíveis', '—', 'Unidades marcadas disponíveis no cadastro'),
            ('recent_operations', 'Operações recentes', '—', 'Operações registradas nos últimos 7 dias'),
        ]):
            grid.addWidget(self._card(*args), index // 2, index % 2)
        layout.addLayout(grid)
        panel = QFrame()
        panel.setObjectName('card')
        p = QVBoxLayout(panel)
        p.setContentsMargins(24, 22, 24, 22)
        p.setSpacing(12)
        p.addWidget(make_label('Conexão com o servidor central', 'cardTitle'))
        self.status = make_label('Verificando servidor...', 'muted', wrap=True)
        p.addWidget(self.status)
        p.addWidget(make_label(f'Endereço local: {settings.base_url}', 'muted'))
        actions = QHBoxLayout()
        self.retry = QPushButton('Testar conexão novamente')
        self.retry.setObjectName('primary')
        self.retry.clicked.connect(self.check_connection)
        actions.addWidget(self.retry)
        actions.addStretch()
        p.addLayout(actions)
        layout.addWidget(panel)
        layout.addStretch()
        scroll.setWidget(body)
        return scroll

    def _placeholder(self, title: str, detail: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 38, 34, 38)
        layout.setSpacing(16)
        layout.addWidget(make_label(title, 'title'))
        layout.addWidget(make_label(detail, 'subtitle', wrap=True))
        panel = QFrame()
        panel.setObjectName('card')
        box = QVBoxLayout(panel)
        box.setContentsMargins(28, 30, 28, 30)
        box.addWidget(make_label('Módulo em preparação', 'cardTitle'))
        box.addWidget(make_label('A navegação está pronta. Nenhuma operação de cadastro ou arquivo foi habilitada nesta etapa.', 'muted', wrap=True))
        layout.addWidget(panel)
        layout.addStretch()
        return page

    @Slot()
    def _toggle_sidebar(self) -> None:
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def _select_page(self, index: int) -> None:
        titles = ['Visão geral', 'Galeria de artes', 'Cadastrar estampa', 'Temas e subtemas', 'Armazenamento', 'Histórico', 'Configurações']
        self._current_page = index
        self.stack.setCurrentIndex(index)
        self.header_title.setText(titles[index])
        for i, button in enumerate(self._nav_buttons):
            button.setProperty('active', i == index)
            button.style().unpolish(button)
            button.style().polish(button)

    @Slot()
    def check_connection(self) -> None:
        if self._busy:
            return
        self._busy = True
        self.retry.setEnabled(False)
        self.status.setText('Verificando servidor...')
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

    @Slot(bool, str, object)
    def _on_result(self, connected: bool, message: str, stats: object) -> None:
        self._connected = connected
        self.connection_status.setText('● Conectado' if connected else '● Desconectado')
        self.connection_status.setObjectName('statusOk' if connected else 'statusBad')
        self.connection_status.style().unpolish(self.connection_status)
        self.connection_status.style().polish(self.connection_status)
        self.status.setText(message + (' — Autenticação será implementada em etapa futura.' if connected else ''))
        if connected and isinstance(stats, dict):
            for key, label in self._metric_labels.items():
                label.setText(str(stats[key]))
                if key in ('artworks', 'themes'):
                    self._metric_notes[key].setText('Dados reais do banco SQLite')
        elif not connected:
            for key, label in self._metric_labels.items():
                label.setText('—')
                self._metric_notes[key].setText('Sem dados: servidor indisponível')
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
    app.setFont(QFont('Segoe UI', 10))
    window = MainWindow()
    window.show()
    return app.exec()
