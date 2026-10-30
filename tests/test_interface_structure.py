"""Verificações estáticas da interface, sem exigir um servidor em execução."""
from pathlib import Path


def test_logo_svg_present():
    logo = Path(__file__).resolve().parents[1] / 'app/client/assets/logo.svg'
    assert logo.is_file()
    assert '<svg' in logo.read_text(encoding='utf-8')


def test_interface_exposes_main_window():
    source = (Path(__file__).resolve().parents[1] / 'app/client/application.py').read_text(encoding='utf-8')
    assert 'class MainWindow(QMainWindow)' in source
    assert 'class ConnectionWorker(QObject)' in source
    assert 'QStackedWidget' in source
    assert 'def _toggle_sidebar' in source
