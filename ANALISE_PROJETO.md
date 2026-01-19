# Análise Detalhada do Projeto: Robô de Extração Eproc

## 1. Visão Geral
O **Robô de Extração Eproc** é uma ferramenta de automação desenvolvida em Python destinada a extrair números de processos judiciais do sistema Eproc do Tribunal de Justiça do estado do Tocantins (TJTO). O projeto foca em robustez e flexibilidade, suportando autenticação moderna (2FA), persistência de sessão para eficiência e execução via CLI ou API REST.

## 2. Estrutura do Projeto
O projeto segue uma estrutura organizada e compatível com microsserviços modernos.

```text
Robo_Eproc/
├── venv/                   # Ambiente virtual Python
├── data/                   # Diretório de saída para arquivos CSV
├── docs/                   # Documentação do projeto (MkDocs)
├── logs/                   # Logs de execução
├── src/                    # Código fonte
│   ├── main.py             # Ponto de entrada (Entry Point) - CLI e FastAPI
│   ├── config.py           # Gerenciamento de configurações (Pydantic Settings)
│   ├── logger.py           # Configuração de logs (Loguru)
│   ├── scripts/            # Lógica de negócio (Scrapers)
│   │   ├── base.py         # Classe base abstrata com lógica de login/nav
│   │   ├── loc_base.py     # Classe base especializada para Localizadores
│   │   ├── loc_peticoes.py       # Implementação para localizador "PETIÇÃO"
│   │   ├── loc_peticao_inicial.py # Implementação para "PETIÇÃO INICIAL"
│   │   └── loc_urgente.py        # Implementação para "URGENTE"
│   └── utils/
│       └── csv_handler.py  # Manipulação e limpeza de dados CSV
├── requirements.txt        # Dependências do projeto
├── .env                    # Variáveis de ambiente (Credenciais)
├── state.json              # Estado da sessão do navegador (Cookies/Storage)
└── README.md               # Documentação inicial
```

## 3. Arquitetura e Tecnologias

### Tecnologias Principais
- **Linguagem**: Python 3.x
- **Automação Web**: `playwright` (Async API) - Escolhido pela velocidade e estabilidade em navegadores modernos.
- **API Framework**: `fastapi` & `uvicorn` - Permite que o robô seja acionado como um serviço web.
- **Configuração**: `pydantic-settings` - Validação robusta de variáveis de ambiente.
- **Logging**: `loguru` - Sistema de logs simplificado e poderoso.
- **2FA**: `pyotp` - Geração de códigos TOTP para autenticação de dois fatores.

### Padrões de Design
1.  **Herança e Polimorfismo**:
    - `BaseScraper` define o contrato e implementa o núcleo comum (Login, Navegação).
    - `LocBaseScraper` implementa a lógica complexa de varredura de tabelas e paginação.
    - Scripts específicos (`LocPeticoes`) apenas definem constantes, mantendo o código "DRY" (Don't Repeat Yourself).
2.  **Injeção de Dependência/Configuração Global**: O módulo `config.py` centraliza todas as configurações, injetando credenciais onde necessário.
3.  **Carregamento Dinâmico**: O `main.py` utiliza `importlib` para carregar scripts da pasta `src/scripts` dinamicamente, facilitando a adição de novos localizadores sem alterar o código principal.

## 4. Análise de Código e Funcionalidades

### 4.1 Autenticação e Sessão (`BaseScraper`)
- **Login Inteligente**: Verifica se já está logado antes de tentar preencher formulários.
- **Suporte a 2FA**: Detecta campos de token TOTP e gera códigos automaticamente usando o segredo configurado (`EPROC_2FA_SECRET`).
- **Seleção de Perfil**: Lida com a tela intermediária de seleção de perfil (ex: "DIRETOR DE SECRETARIA"), comum em sistemas judiciários.
- **Persistência**: Salva cookies e local storage em `state.json`, permitindo execuções subsequentes mais rápidas sem necessidade de login completo.

### 4.2 Lógica de Extração (`LocBaseScraper`)
- **Navegação via Regex**: Encontra o link do localizador usando Expressões Regulares, tornando a navegação resiliente a pequenas variações de texto ou espaços.
- **Paginação Automática**: Itera sobre todas as páginas de resultados, detectando botões de "Próxima" e tratando estados de carregamento.
- **Captura de Dados**: Extrai números de processos (formato NNNNNNN-NN.NNNN.N.NN.NNNN) de qualquer lugar do texto da tabela, garantindo que nada seja perdido.
- **Tratamento de Erros**: Inclui timeouts e retries para elementos que demoram a carregar.

### 4.3 Utilitários
- **CSV Handler**: Normaliza os números dos processos (remove pontuação) antes de salvar, facilitando o uso posterior por outros sistemas ou importação em bancos de dados. Salva automaticamente em `data/`.

## 5. Pontos Fortes
- **Robustez**: O uso de `playwright` com esperas explícitas e tratamento de 2FA torna o robô muito confiável.
- **Modularidade**: Adicionar um novo localizador é trivial (basta criar um arquivo de 5 linhas).
- **Híbrido**: Funciona tanto para um usuário rodando localmente (CLI) quanto integrado em um pipeline maior (API).

## 6. Sugestões de Melhoria
1.  **Tratamento de Captchas**: Atualmente não há menção explícita de tratamento de Captchas complexos (apenas o login padrão), o que pode ser um ponto de falha se o Eproc aumentar a segurança.
2.  **Métricas**: Adicionar contadores de falhas por página ou tempo médio por página nos logs.
3.  **Testes**: A cobertura de testes automatizados parece baixa (apenas `test_2fa.py` visto). Adicionar testes unitários para os parsers seria ideal.

## 7. Conclusão
O projeto demonstra uma maturidade técnica alta. Não é apenas um script simples, mas uma aplicação bem estruturada pronta para produção, que considera casos de borda reais do dia a dia (como quedas de sessão e múltiplos perfis).
