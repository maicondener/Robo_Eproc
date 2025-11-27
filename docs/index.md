# Bem-vindo ao Robô de Extração Eproc

O **Robô de Extração Eproc** é uma ferramenta profissional de automação desenvolvida para extrair dados e realizar tarefas no sistema Eproc do TJTO.

## 📚 Documentação

A documentação foi dividida em seções para facilitar o acesso:

- **[⚙️ Configuração e Instalação](setup.md)**: Guia passo a passo para instalar o Python, configurar o ambiente virtual e definir as credenciais (incluindo 2FA e Perfil).
- **[🚀 Como Usar](usage.md)**: Instruções de execução via Linha de Comando (CLI) e API, lista de scripts disponíveis e formato dos dados extraídos.
- **[💻 Desenvolvimento e Arquitetura](development.md)**: Detalhes técnicos sobre a estrutura do projeto e como criar novos scripts de automação.

## ✨ Principais Características

- **Automação Robusta:** Construído com [Playwright](https://playwright.dev/python/), capaz de lidar com sites dinâmicos modernos.
- **Autenticação Completa:** Suporte nativo a **2FA (TOTP)** e seleção automática de **Perfil de Usuário**.
- **Sessão Persistente:** Reutiliza a sessão de login para evitar autenticações desnecessárias e bloqueios.
- **Extensível:** Arquitetura modular que permite criar novos robôs de extração com pouquíssimas linhas de código.
- **API Integrada:** Inclui uma API REST (FastAPI) para integração com outros sistemas.

## 🛠️ Tecnologias

- **Python 3.10+**
- **Playwright** (Automação Web)
- **FastAPI** (Interface API)
- **Pydantic** (Gestão de Configuração)
- **Loguru** (Logs Estruturados)
