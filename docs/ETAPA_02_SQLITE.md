# Módulo 01 — Etapa 02 — SQLite centralizado

## Escopo das seis entregas
1. Planejamento: modelo relacional, limites e regras.
2. Esquema SQLite inicial, criado automaticamente ao iniciar o servidor.
3. Chaves estrangeiras, índices, unicidade e integridade.
4. Integração com o ciclo de vida FastAPI; `/health` e `/info` preservados.
5. Transações `BEGIN IMMEDIATE`, `busy_timeout`, WAL, chave idempotente para operações de arquivo e revisão otimista para cadastros.
6. Testes automatizados, instruções de validação e checklist de homologação.

## Armazenamento
No Windows, o arquivo fica em `%LOCALAPPDATA%\CatalogoEstampas2\catalogo.sqlite3`, fora do Git e fora da pasta de instalação. O servidor é o único processo autorizado a acessá-lo; clientes só acessam a API. O SQLite não deve ser aberto por estações via SMB.

## Tabelas
`schema_meta`, `users`, `themes`, `subthemes`, `storage_units`, `artworks`, `artwork_files`, `file_operations`, `audit_events`.

As tabelas de usuários e operações são **estruturas preparatórias**, sem login, gravação de senhas, manipulação de arquivos ou endpoints CRUD expostos. As futuras operações administrativas exigirão autenticação e autorização antes de qualquer acesso por rede. A validação cruzada tema/subtema está implementada no repositório, e deverá ser reutilizada nas futuras APIs.

## Testes no Windows
Em `C:\Projetos\CatalogoEstampas2`, com o servidor fechado:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q app config main.py server_main.py tests
.\.venv\Scripts\python.exe server_main.py
```

Em outro terminal:

```powershell
.\.venv\Scripts\python.exe main.py
```

Verificar `http://127.0.0.1:8765/health` e `http://127.0.0.1:8765/info`. O servidor cria o banco ao iniciar; não há necessidade de executar SQL manualmente.

## Limitações e cuidados
- Esquema versão 1: futuras mudanças exigem migrações versionadas e backup prévio. Não foi implementado mecanismo de migração nesta etapa.
- O WAL cria arquivos auxiliares `-wal` e `-shm`. Não copie apenas o arquivo principal com o servidor ativo para fazer backup; use a API de backup do SQLite ou interrompa o servidor.
- Não há ainda API de cadastro, login, exclusão, cópia, movimentação ou sincronização entre computadores.
- O aviso de depreciação de `fastapi.testclient` visto na Entrega 03 pode persistir; não é falha dos testes.
- Homologação, commit, push e backup no Windows dependem de execução e confirmação do usuário.
