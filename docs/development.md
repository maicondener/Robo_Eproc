# 💻 Desenvolvimento e Arquitetura

Este documento descreve a estrutura técnica do projeto e como estendê-lo criando novos scripts.

## Arquitetura do Projeto

O projeto segue uma arquitetura modular, separando configurações, logs, lógica base e scripts específicos.

### Componentes Principais

1.  **`src/main.py`**: O "cérebro" da aplicação.
    - Gerencia a execução via CLI e API.
    - Carrega dinamicamente os scripts da pasta `src/scripts/`.
    - Inicializa o navegador (Playwright) e gerencia a sessão (`state.json`).

2.  **`src/scripts/base.py` (`BaseScraper`)**:
    - Classe abstrata que todo script deve herdar (direta ou indiretamente).
    - Implementa métodos comuns: `login()`, `navigate_to_home()`.
    - Gerencia o 2FA e a seleção de perfil.

3.  **`src/scripts/loc_base.py` (`LocBaseScraper`)**:
    - Uma especialização de `BaseScraper` focada em **extração por localizador**.
    - Implementa toda a lógica repetitiva: clicar no localizador, iterar páginas, extrair regex, salvar CSV.
    - Novos scripts de localizador devem herdar desta classe.

4.  **`src/config.py`**:
    - Centraliza as configurações usando `pydantic-settings`.
    - Lê e valida as variáveis do arquivo `.env`.

## 📂 Estrutura de Pastas

```
Robo_Eproc/
├── .venv/                # Ambiente virtual Python
├── data/                 # Saída dos dados (CSVs gerados)
├── docs/                 # Documentação do projeto
├── logs/                 # Arquivos de log (rotação automática)
├── src/
│   ├── scripts/          # Scripts de automação
│   │   ├── base.py       # Classe BaseScraper
│   │   ├── loc_base.py   # Classe LocBaseScraper (Lógica compartilhada)
│   │   ├── loc_peticoes.py
│   │   ├── loc_peticao_inicial.py
│   │   └── ...
│   ├── utils/            # Funções utilitárias (ex: csv_handler.py)
│   ├── config.py         # Configurações
│   ├── logger.py         # Configuração de Logs
│   └── main.py           # Executor principal
├── .env                  # Credenciais (NÃO COMMITAR)
├── .gitignore            # Arquivos ignorados pelo Git
└── requirements.txt      # Dependências do projeto
```

## 🛠️ Criando um Novo Script de Localizador

Graças à classe `LocBaseScraper`, criar um novo robô para extrair processos de um localizador específico é extremamente simples.

### Exemplo: Criar um extrator para o localizador "URGENTE"

1.  Crie um arquivo `src/scripts/loc_urgente.py`.
2.  Defina uma classe que herde de `LocBaseScraper`.
3.  Defina as constantes `LOCATOR_NAME` e `OUTPUT_FILENAME`.

```python
from src.scripts.loc_base import LocBaseScraper

class LocUrgente(LocBaseScraper):
    # O nome exato que aparece na tabela "Processos com Localizador"
    LOCATOR_NAME = "URGENTE"
    
    # O nome do arquivo CSV que será salvo em data/
    OUTPUT_FILENAME = "processos_urgente.csv"
```

**Pronto!** O `main.py` irá reconhecer automaticamente o novo script.
Para rodar:
```bash
python -m src.main --script loc_urgente
```

## 🧪 Criando um Script Customizado (Avançado)

Se você precisa de uma lógica que não se encaixa no padrão de "extrair processos de um localizador", você pode herdar diretamente de `BaseScraper`.

```python
from playwright.async_api import Page
from src.scripts.base import BaseScraper, ScraperResult

class MeuScriptCustomizado(BaseScraper):
    async def run(self, page: Page) -> ScraperResult:
        # Sua lógica aqui
        await self.login(page)
        # ...
        return ScraperResult(success=True, message="Feito!")
```
