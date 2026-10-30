# Módulo 01 — Etapa 03: Interface principal

## Entregue
- Janela principal PySide6, identidade visual própria e logotipo SVG.
- Menu lateral recolhível com sete seções navegáveis.
- Cabeçalho e estado de conexão do servidor central.
- Painel inicial com indicadores explicitamente indisponíveis (sem dados inventados).
- Páginas de preparação para os módulos ainda não implementados.
- Verificação de conexão em segundo plano a cada 10 segundos, com tentativa manual.
- Preservação do servidor FastAPI, do banco SQLite e das rotas já homologadas.

## Não incluído nesta etapa
Autenticação, cadastro funcional, galeria com imagens, movimentação de arquivos, API administrativa ou acesso pela rede. Essas funções dependem das etapas próprias e de segurança.

## Execução no Windows
1. ` .\.venv\Scripts\python.exe -m pytest -q `
2. ` .\.venv\Scripts\python.exe server_main.py `
3. Em outro terminal: ` .\.venv\Scripts\python.exe main.py `

## Homologação sugerida
Abrir janela, verificar logotipo, navegar pelas sete telas, recolher/expandir menu, redimensionar, desconectar/reconectar servidor e rodar testes de regressão.
