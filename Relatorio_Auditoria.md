# Relatório Técnico de Auditoria: Robo Eproc TJTO

Este documento apresenta uma auditoria detalhada da arquitetura, código e segurança do projeto **Robo Eproc**, uma ferramenta de automação para extração de dados do sistema Eproc (TJTO).

---

## 1. Arquitetura e Design System

O projeto apresenta uma arquitetura **modular e extensível**, baseada em herança, o que facilita a manutenção e a criação de novos robôs.

### Componentes Principais:
- **`BaseScraper`**: Classe base abstrata que centraliza a lógica de **Login**, **Autenticação 2FA (TOTP)**, **Seleção de Perfil** e **Persistência de Sessão** (`state.json`).
- **`LocBaseScraper`**: Especialização para localizadores, tratando de forma genérica a navegação por regex, extração de números de processo e **paginação automática**.
- **`main.py`**: Ponto de entrada híbrido (CLI e FastAPI), utilizando carregamento dinâmico de módulos (`importlib`).

> [!TIP]
> O padrão de persistência de sessão em `state.json` é um ponto forte, reduzindo drasticamente o tempo de execução e o risco de bloqueio por sucessivas tentativas de login.

---

## 2. Análise de Código e Segurança

### 2.1 Pontos Fortes
- **Resiliência de Seletores**: O uso de `get_by_role` com Regex para navegar em localizadores torna o script resistente a variações de espaços e aspas na interface web.
- **Validação de Configurações**: Uso do `pydantic-settings` garante que variáveis críticas (Login, Senha) sejam verificadas antes da execução.
- **Logging**: Implementação limpa com `loguru`, facilitando o rastreamento de fluxos de erro.

### 2.2 Pontos de Atenção (Riscos e Débito Técnico)

#### A. Hardcoding de Caminhos e URLs
No script `relatorio_conclusos.py`, foram identificados caminhos e URLs fixos no código:
- `self.output_csv_path = r"G:\Meu Drive\Processos_Conclusos.csv"`
- `self.webhook_url = "https://n8n.maicondener.dev.br/..."`

> [!WARNING]
> Isso impede a portabilidade do projeto. Se o robô rodar em um servidor (Linux/Docker), o caminho `G:\` falhará e a URL do webhook não poderá ser alterada sem mexer no código.

#### B. Navegação em Menus Multinível
A navegação no menu "Relatórios" -> "Relatórios Estatísticos" é feita via clique sequencial. Em sistemas legados como o Eproc, frames ou menus flutuantes podem ser instáveis em modo *headless*.

#### C. Tratamento de Erros no CSV
O `csv_handler.py` limpa a pontuação dos processos, mas se a lista for vazia, ele ainda escreve o cabeçalho. Não há validação de integridade do arquivo pós-gravação.

---

## 3. Recomendações de Melhoria

### Curto Prazo (Necessário para Estabilidade)
1.  **Parametrização**: Mover `OUTPUT_PATH` e `WEBHOOK_URL` para o arquivo `.env` e acessá-los via `settings` no `src/config.py`.
2.  **Retry Logic**: Implementar um decorador de `retry` para operações críticas de clique em menus de navegação.
3.  **Tratamento de Iframe**: Verificar se os "Relatórios Estatísticos" abrem em um `<iframe>`. Se sim, a lógica de `page.locator` precisará ser ajustada para `page.frame_locator`.

### Médio Prazo (Escalabilidade)
1.  **Interface de Tarefas**: Como há um modo API, considerar o uso de **Celery ou ARQ** para gerenciar as execuções em segundo plano, evitando timeouts de requisição HTTP em scripts longos (como o de relatórios que demora 5 min).
2.  **Notificação de Erro**: Adicionar o envio do erro para o webhook caso o script falhe, não apenas no sucesso.

---

## 4. Conclusão da Auditoria

O projeto **Robo Eproc** está em um nível técnico excelente, superando a média de scripts de automação. Sua estrutura é profissional e pronta para escala, necessitando apenas de refinamentos na gestão de constantes e paths para ser considerado "Production Ready" em ambientes diversos.

**Status de Auditoria: APROVADO COM RESSALVAS (Correções de constantes recomendadas)**
