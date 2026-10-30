# Catálogo de Estampas 2.0

Projeto novo, independente do catálogo anterior, com cliente Windows portátil
e servidor central. Desenvolvimento em Python 3.13 (64 bits), sujeito a
validação de compatibilidade.

## Estado atual — Módulo 01, Etapa 01, Bloco 01, Entrega 01

Esta entrega contém **somente a estrutura e os arquivos-base**.
Os pontos de entrada exibem mensagens informativas; não iniciam uma interface
gráfica, uma API ou um banco de dados. Isso será feito em entregas posteriores.

## Estrutura

- `main.py`: ponto de entrada reservado ao cliente.
- `server_main.py`: ponto de entrada reservado ao servidor.
- `app/client/`: código do cliente (PySide6 em etapa posterior).
- `app/server/`: código do servidor (FastAPI em etapa posterior).
- `app/shared/`: contratos e recursos neutros compartilhados.
- `config/`: código de configuração, sem segredos reais.
- `tests/`: testes automatizados futuros.
- `docs/`: documentação técnica.
- `pyproject.toml`: metadados; dependências serão adicionadas na Entrega 02.

## Instalação dos arquivos

1. Escolha uma pasta vazia para o projeto, conforme o planejamento:
   `C:\Projetos\CatalogoEstampas2`.
2. Extraia o conteúdo do ZIP preservando a estrutura.
3. Se já houver arquivos no destino, **não sobrescreva** antes de conferi-los.
4. Não instale dependências nesta entrega.

## Verificação básica (opcional)

Com Python 3.13 disponível, na pasta do projeto:

```powershell
python main.py
python server_main.py
```

Ambos devem exibir uma mensagem informando que sua inicialização funcional
será implementada na Entrega 03. Nenhum serviço será aberto.

## Próximas entregas

- Entrega 02: ambiente virtual e dependências.
- Entrega 03: inicialização mínima PySide6/FastAPI e configurações.
- Entrega 04: testes e validação integrados.

**Não incluir bancos de dados reais, certificados privados ou senhas no Git.**

## Entrega 02 — Dependências e ambiente (em validação)

O Python 3.13 e a pasta `.venv` são locais e não fazem parte do ZIP.
Veja `docs/ENTREGA_02.md` para instalação, verificações e congelamento de versões.
A inicialização da interface e da API permanece reservada à Entrega 03.
