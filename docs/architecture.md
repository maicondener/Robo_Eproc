# Arquitetura do Robô Eproc

A estrutura do projeto está dividida em módulos independentes que mantêm uma separação limpa (Clean Code) entre o orquestrador (CLI/API) e a lógica de negócios da automação.

## Estrutura de Diretórios Básica

```text
Robo_Eproc/
├── docs/                # Documentação técnica e de negócio.
├── src/                 # Código principal
│   ├── scripts/         # Scripts que executam as tarefas do Playwright (Scrapers)
│   ├── utils/           # Ferramentas auxiliares, como chamadas HTTP de integração.
│   ├── config.py        # Configuração com pydantic-settings baseado no arquivo .env
│   ├── logger.py        # Módulo de formatação de logs e exibição no console
│   └── main.py          # Entrypoint do sistema (API, CLI, carregador de scripts)
├── .env                 # Arquivo com chaves e senhas reais (ignorado pelo git)
└── requirements.txt     # Relatório das bibliotecas externas em uso
```

## 1. Módulo Principal (`src/main.py` / `main.py`)
O sistema possui a capacidade inteligente de carregar os scripts sob demanda, inspecionando a pasta `src/scripts`. Não é necessário importar todos os códigos em `main.py`, ele utiliza os pacotes nativos do python (`importlib` e `inspect`) para ler a o nome do arquivo, carregar a classe que herda a classe pai de Scraping (`BaseScraper`) e executá-la dentro de um contexto seguro do navegador Chromium gerido pelo Playwright.

O fluxo prevê uma função global (`execute_script()`) e duas abstrações principais:
- O Modo CLI utiliza a `argparse` para interações por shell.
- O Modo REST/API carrega todo esse fluxo como dependência assíncrona nas rotas controladas pelo `FastAPI`.

## 2. A Lógica dos Scrapers (`src/scripts/`)
Este diretório age como a "receita" do robô, com Padrões de Projeto (como Template Method).

- `base.py` -> Contém `BaseScraper`, um contrato básico abstrato que todo e qualquer Web Scraper do projeto deve seguir. Tem apenas uma assinatura assíncrona mandatória, o método `run(page: Page) -> ScraperResult`.
  
### Localizadores
Os web scrapers de localizadores possuem uma classe genérica intermediária `LocBaseScraper` (`loc_base.py`).
Esta classe cuida especificamente de fluxos do Eproc TJTO, isto é:
1. Faz o Login via SSO com as credenciais contidas no `.env`.
2. Acessa a barra lateral e navega na árvore de *Localizadores*.
3. Pega o nome do localizador (a ser implementado nas classes filhas) e raspa por todas as tabelas o texto exposto identificando o **Padrão CNJ de um Processo**, utilizando `regex`.
4. Transforma todos estes processos detectados em listas e envia utilizando os utilitários de integração para o Banco de Dados.

- Subclasses: `loc_peticao_inicial.py`, `loc_peticoes.py` e `loc_urgente.py` são as adaptações de cada pesquisa e herdam de `loc_base.py`, fornecendo apenas nome do localizador específico na variável de classe `LOCATOR_NAME`.

### Relatórios Complexos (`eproc_concluso.py`)
Relatórios maiores são gerados através da emissão interna no botão "Emitir CSV" da plataforma do Eproc, para depois passarem por manipulação avançada de processamento de dados usando o **Pandas**. O script de conversão readequa nomes e valida formatação de datas.

## 3. O Módulo Utilitário e de Integrações (`src/utils/`)
Sempre que uma etapa (`run`) do Scraper terminar o seu escopo, os dados raspados não devem ficar persistidos ou largados localmente. Esse módulo fornece sub-rotinas acionadas do Eproc (o cliente requereu via `requests`) de modo a expor interfaces HTTP POST enviando JSON das listas encontradas ao ambiente na nuvem.
- `integracao_legalmind.py`
  1. `enviar_para_legalmind`: Submete processos mapeados por Localizador.
  2. `enviar_relatorio_concluso`: Envia dicionários com data, vara e prioridade manipulados pelo Pandas.
