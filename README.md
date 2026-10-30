# Catálogo de Estampas 2.0

Aplicação Windows com cliente PySide6, servidor FastAPI e SQLite centralizado. Python 3.13.

**Módulo 01 — Etapa 03: interface principal entregue para testes e homologação no Windows.**

## Execução no Windows

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe server_main.py
```

Em outro terminal:

```powershell
.\.venv\Scripts\python.exe main.py
```

O banco é criado automaticamente em `%LOCALAPPDATA%\CatalogoEstampas2\catalogo.sqlite3` na primeira inicialização do servidor. O servidor permanece restrito a `127.0.0.1:8765`.

Leia `docs/ETAPA_02_SQLITE.md` para esquema, testes, limites de segurança e cuidados com backups. Não inclua `.venv`, bancos, credenciais ou arquivos privados no Git.

## Interface principal

Janela com identidade visual, logotipo, menu lateral recolhível, sete telas, painel inicial e indicador de conexão. A navegação é funcional; cadastro, galeria operacional e permissões serão implementados nas etapas correspondentes. Consulte `docs/ETAPA_03_INTERFACE.md`.
