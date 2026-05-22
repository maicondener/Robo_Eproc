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

- Subclasses: `loc_peticao_inicial.py`, `loc_peticoes.py`, `loc_urgente.py` e `loc_mandados.py`. Elas herdam de `loc_base.py`. Enquanto as três primeiras fornecem apenas o nome do localizador específico na variável de classe `LOCATOR_NAME`, a classe `loc_mandados.py` estende a extração para ler as informações de data de inclusão diretamente das colunas da tabela do eproc, aplicando regras estritas de negócios para sincronização incremental no Sheets e posterior envio dos inéditos para o LegalMind Core.

### Relatórios Complexos (`eproc_concluso.py`)
Relatórios maiores são gerados através da emissão interna no botão "Emitir CSV" da plataforma do Eproc, para depois passarem por manipulação avançada de processamento de dados usando o **Pandas**. O script de conversão readequa nomes e valida formatação de datas.

## 3. O Módulo Utilitário e de Integrações (`src/utils/`)
Sempre que uma etapa (`run`) do Scraper terminar o seu escopo, os dados raspados não devem ficar persistidos ou largados localmente de forma inerte. Esse módulo fornece sub-rotinas acionadas do Eproc de modo a expor interfaces HTTP POST enviando JSON das listas encontradas ao ambiente na nuvem ou integrando dados com planilhas de forma segura.

- `integracao_legalmind.py`
  1. `enviar_para_legalmind`: Submete processos mapeados por Localizador.
  2. `enviar_relatorio_concluso`: Envia dicionários com data, vara e prioridade manipulados pelo Pandas.
- `google_sheets.py`
  Fornece a classe `GoogleSheetsClient` que orquestra a integração profissional com a Google Sheets API v4.
  1. **Autenticação Robusta:** Utiliza o fluxo de aplicativo de desktop OAuth2 via `credentials.json` para autorizar acessos e gerar o token local `token.json` com capacidade de atualização automática contínua.
  2. **Tratamento de Data com Hífen Separador:** Grava datas formatadas como `'DD/MM/AAAA - HH:MM:SS'` (forçando o Sheets a interpretá-las como texto simples), o que previne truncamentos automáticos e preserva as horas na leitura de verificação.
  3. **Proteção Contra Duplicidade:** Realiza desduplicação cruzando `Número do Processo` e `Data e Hora de Inclusão` antes de enviar as escritas em lote (*batch update*).
