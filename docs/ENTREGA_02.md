# Módulo 01 · Etapa 01 · Entrega 02 — Dependências e ambiente

## Pré-requisitos
- Windows, Python 3.13 de 64 bits e Git.
- Projeto em `C:\Projetos\CatalogoEstampas2`.
- Não copiar `.venv` de outra máquina e não alterar instalações globais de Python.

## Arquivos alterados nesta entrega
- `pyproject.toml`: dependências opcionais agrupadas e configuração de build.
- `README.md`: referência à Entrega 02.
- `docs/ENTREGA_02.md`: instruções e validações.

## Instalação — somente após autorização e conferência do ZIP

No PowerShell, na raiz do projeto e com o `.venv` ativo:

```powershell
python -m pip install -e '.[client,server,dev]'
```

O grupo `distribution` fica preparado, mas não é instalado agora; será utilizado na etapa de empacotamento.

## Validação

```powershell
python -m pip check
python -m pip list
python -c "import PySide6, httpx, fastapi, uvicorn, pydantic, pytest; print('Importacoes OK')"
python -m pytest -q
git status --short
```

Ainda não existem testes funcionais; `pytest` pode retornar código 5 (nenhum teste coletado).

## Travamento de versões do ambiente homologado

Depois de instalar e validar as bibliotecas:

```powershell
python -m pip freeze --all > requirements-lock.txt
```

Esse arquivo captura versões exatas instaladas nesta máquina e será revisado antes de entrar no Git. Não foi pré-gerado porque as versões efetivamente resolvidas dependem da instalação.

## Segurança e controle
- Nunca incluir `.venv`, credenciais, banco operacional ou arquivos privados no ZIP/Git.
- Não iniciar servidor nem abrir portas nesta entrega.
- Após homologação: commit, envio ao GitHub e backup ZIP na unidade G:.
