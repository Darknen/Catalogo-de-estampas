# Catálogo de Estampas 2.0

Cliente Windows PySide6 e servidor central FastAPI, projeto independente do catálogo anterior.
Python 3.13 (64 bits). **Estado: Módulo 01 · Etapa 01 · Entrega 03 — aguardando testes e homologação.**

## Início rápido

Use a pasta de projeto existente, com `.venv` já preparado na Entrega 02. Em dois terminais PowerShell separados, com o ambiente virtual ativo:

```powershell
python server_main.py
```

```powershell
python main.py
```

O cliente verifica `http://127.0.0.1:8765/health`, mostra a conexão e permite nova tentativa. O servidor deve ser iniciado manualmente. A conexão é **apenas local** e não inclui autenticação nem acesso ao catálogo.

## Verificações

```powershell
python -m pytest -q
python -m compileall -q app config main.py server_main.py
```

## Documentação

- `docs/ENTREGA_02.md`: dependências e ambiente.
- `docs/ENTREGA_03.md`: instruções, testes e limites da entrega.
- `docs/DECISOES.md`: decisões técnicas resumidas.

**Nunca incluir `.venv`, credenciais, banco de dados ou arquivos privados no Git ou no ZIP de entrega.**
