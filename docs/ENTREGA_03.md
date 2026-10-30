# Módulo 01 · Etapa 01 · Entrega 03 — Inicialização local

## O que está incluído
- API FastAPI com endpoints públicos mínimos `/health` e `/info`.
- Servidor manual, vinculado somente a `127.0.0.1:8765`.
- Cliente PySide6 com indicador de conexão, botão de nova tentativa e verificação periódica.
- Verificação de compatibilidade da versão da API.
- Testes básicos sem abrir portas ou acessar banco de dados.

## Instalação no projeto existente
1. Faça backup do projeto e mantenha sua pasta `.venv` atual.
2. Extraia este ZIP em uma pasta temporária e confira os arquivos.
3. Copie os arquivos para a raiz do projeto, preservando a estrutura; **não substitua `.venv`**.
4. No PowerShell, em `C:\Projetos\CatalogoEstampas2`, ative `.venv`.
5. Confira as dependências já instaladas: `python -m pip check`.

## Execução — em dois terminais
Terminal 1:
```powershell
python server_main.py
```
Terminal 2:
```powershell
python main.py
```

Abra `http://127.0.0.1:8765/health` para conferir a API. Feche o servidor com Ctrl+C.

## Testes
```powershell
python -m pytest -q
python -m compileall -q app config main.py server_main.py
```

## Limites de segurança
Não abrir a porta na rede. Não há autenticação, banco de dados, operações de arquivos, tela de login funcional, descoberta mDNS ou HTTPS nesta entrega. O indicador de conexão não concede acesso a dados.

## Homologação
Somente após os testes manuais e aprovação: commit, push e backup ZIP. Não foram realizados automaticamente.
