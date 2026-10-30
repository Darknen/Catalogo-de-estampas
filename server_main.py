"""Inicia manualmente o servidor, exclusivamente no computador local."""
import uvicorn
from config.settings import settings


def main() -> int:
    print(f"Servidor local: {settings.base_url} (Ctrl+C para encerrar)")
    try:
        uvicorn.run("app.server.application:app", host=settings.host, port=settings.port, log_level="info")
    except KeyboardInterrupt:
        return 0
    except OSError as exc:
        print(f"Não foi possível iniciar o servidor: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
