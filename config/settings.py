"""Configuração restrita ao loopback nesta entrega.

Não são aceitas variáveis de ambiente para alterar o host, evitando
exposição acidental da API ainda sem autenticação.
"""
from dataclasses import dataclass
from app.shared.constants import DEFAULT_HOST, DEFAULT_PORT


@dataclass(frozen=True)
class Settings:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    timeout_seconds: float = 2.0

    def __post_init__(self) -> None:
        if self.host != DEFAULT_HOST:
            raise ValueError("Entrega 03 permite somente 127.0.0.1")
        if not 1 <= self.port <= 65535:
            raise ValueError("Porta inválida")
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout deve ser positivo")

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


settings = Settings()
