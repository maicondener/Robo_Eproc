# ⚙️ Configuração do Ambiente

Este guia detalha como preparar o ambiente para executar o Robô Eproc.

## 1. Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **[Python](https://www.python.org/downloads/)** (versão 3.10 ou superior).
- **[Git](https://git-scm.com/downloads/)** (para clonar o repositório).

## 2. Instalação

### Passo 1: Clonar o Repositório

Abra seu terminal e execute:

```bash
git clone <URL_DO_REPOSITORIO>
cd Robo_Eproc
```

### Passo 2: Criar Ambiente Virtual

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Cria o ambiente virtual chamado .venv
python -m venv .venv

# Ativa o ambiente (Windows)
.venv\Scripts\activate

# Ativa o ambiente (macOS/Linux)
source .venv/bin/activate
```

### Passo 3: Instalar Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### Passo 4: Instalar Navegadores

O Playwright precisa baixar os binários dos navegadores para funcionar:

```bash
playwright install
```

## 3. Configuração (.env)

O robô utiliza variáveis de ambiente para gerenciar credenciais e configurações sensíveis.

1.  Copie o arquivo de exemplo:
    ```bash
    cp .env.example .env
    ```
    *(No Windows, você pode copiar e colar manualmente o arquivo e renomeá-lo para `.env`)*

2.  Edite o arquivo `.env` com suas informações:

### Parâmetros Obrigatórios

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `EPROC_LOGIN` | Seu usuário de acesso ao Eproc. | `123456` |
| `EPROC_SENHA` | Sua senha de acesso. | `MinhaSenhaForte` |

### Parâmetros Opcionais (Recomendados)

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `EPROC_2FA_SECRET` | Chave secreta (Secret Key) do seu autenticador 2FA. Permite login 100% automático. **Não use espaços.** | `JBSWY3DPEHPK3PXP` |
| `EPROC_PERFIL` | Nome exato do perfil a ser selecionado após o login (caso você tenha múltiplos perfis). | `DIRETOR DE SECRETARIA` |

### Configurações do Sistema

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `EPROC_URL` | URL base do sistema Eproc. | `https://eproc1.tjto.jus.br/...` |
| `HEADLESS` | Se `True`, roda o navegador em segundo plano (invisível). Se `False`, mostra o navegador. | `True` |
| `BROWSER_CHANNEL` | Canal do navegador a ser usado (`chrome`, `msedge`, `chromium`). | `chrome` |
| `LOG_LEVEL` | Nível de detalhe dos logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

---

## 🔒 Configurando o 2FA (Autenticação de Dois Fatores)

Para que o robô faça login automaticamente, ele precisa gerar o código TOTP (aquele de 6 dígitos que muda a cada 30s).

1.  Acesse o Eproc e vá nas configurações de 2FA.
2.  Ao invés de apenas escanear o QR Code, procure pela opção **"Exibir chave secreta"** ou **"Setup Key"**.
3.  Copie essa chave (geralmente uma sequência de letras e números como `JBSWY3DPEHPK3PXP`).
4.  Cole essa chave na variável `EPROC_2FA_SECRET` do seu arquivo `.env`.

> **Teste:** Você pode testar se a chave está correta rodando:
> ```bash
> python -m src.scripts.test_2fa
> ```
> O código gerado deve ser igual ao do seu aplicativo autenticador (Google Authenticator, Microsoft Authenticator, etc).
