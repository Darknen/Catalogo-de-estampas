"""Configuração do servidor local e banco SQLite em pasta de dados do Windows."""
from dataclasses import dataclass
from pathlib import Path
import os
from app.shared.constants import DEFAULT_HOST, DEFAULT_PORT


def default_data_dir() -> Path:
    base = os.environ.get('LOCALAPPDATA')
    return (Path(base) if base else Path.home()/'.local'/'share') / 'CatalogoEstampas2'

@dataclass(frozen=True)
class Settings:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    timeout_seconds: float = 2.0
    data_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.host != DEFAULT_HOST: raise ValueError('Servidor disponível somente em 127.0.0.1')
        if not 1 <= self.port <= 65535: raise ValueError('Porta inválida')
        if self.timeout_seconds <= 0: raise ValueError('Timeout deve ser positivo')

    @property
    def base_url(self) -> str:
        return f'http://{self.host}:{self.port}'

    @property
    def database_path(self) -> Path:
        return (self.data_dir or default_data_dir())/'catalogo.sqlite3'

settings = Settings()
