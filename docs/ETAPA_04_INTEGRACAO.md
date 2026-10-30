# Módulo 01 — Etapa 04 — Integração do Dashboard

## Entrega
- API GET /dashboard/stats: agregados reais consultados pelo servidor no SQLite existente.
- Artes cadastradas: total de linhas em `artworks`.
- Temas organizados: total de linhas em `themes` (não inclui subtemas).
- Unidades disponíveis: registros de `storage_units` com `available=1` (não é detecção física do HD).
- Operações recentes: registros em `file_operations` criados nos últimos 7 dias, independentemente do estado.
- Atualização automática a cada 10 segundos e manual por botão existente.
- A interface não acessa o banco diretamente; servidor fora do ar exibe traços, sem valores desatualizados.
- Preservados logo, menus, layout e schema SQLite.

## Execução
No PowerShell, na pasta do projeto, execute ` .\.venv\Scripts\python.exe -m pytest -q `.
Em um terminal: ` .\.venv\Scripts\python.exe server_main.py `.
Em outro: ` .\.venv\Scripts\python.exe main.py `.

## Segurança e escopo
Endpoint de estatísticas disponível apenas no servidor vinculado a 127.0.0.1, sem dados pessoais; autenticação e autorização ficam para etapa posterior. Não expor porta à rede.

## Homologação
Verificar quatro números com servidor ativo; atualização manual e automática; desligar servidor e conferir indicador desconectado e números substituídos por traços; religar e conferir recuperação. Não fazer commit ou backup definitivo antes da aprovação do usuário.
