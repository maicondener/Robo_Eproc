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

---

## 📊 Configurando a API do Google Sheets v4

Para que o script `loc_mandados` possa ler e gravar dados diretamente na sua planilha do Google Sheets, siga os passos abaixo para configurar as credenciais de acesso:

### Passo 1: Criar credenciais no Google Cloud Console
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Crie um novo projeto (ex: *Robo-Eproc-Sheets*).
3. No painel, vá em **Biblioteca** e pesquise por **Google Sheets API**. Clique em **Ativar**.
4. Vá para a guia de **Tela de Consentimento OAuth** (OAuth Consent Screen):
   - Selecione **Externo**.
   - Preencha os dados básicos necessários (Nome do app, e-mail de suporte).
   - Na seção de usuários de teste, **adicione o e-mail da sua conta Google** que tem acesso à planilha a ser editada.
5. Acesse a guia **Credenciais**:
   - Clique em **+ Criar Credenciais** e selecione **ID do cliente OAuth**.
   - Escolha o tipo de aplicativo **Aplicativo de desktop** (Desktop App).
   - Nomeie como desejar e clique em **Criar**.
6. Uma vez criado, clique em **Fazer download do JSON** do cliente gerado.

### Passo 2: Adicionar o Arquivo ao Projeto
1. Renomeie o arquivo JSON baixado para exatamente `credentials.json`.
2. Mova ou cole o arquivo `credentials.json` na **raiz** do projeto `Robo_Eproc/` (onde o arquivo `.env` está localizado).

### Passo 3: Primeira Execução e Geração de Token
Na primeira vez que você rodar o robô que utiliza a API do Google Sheets (ex: `python -m src.main --script loc_mandados`), o terminal pausará e abrirá uma aba no seu navegador web padrão:
1. Faça login na conta do Google que você cadastrou como usuário de teste e que tem acesso à planilha.
2. Se aparecer um aviso informando que o Google não verificou o app, clique em **Avançado** e em **Acessar [Nome do seu App] (não seguro)**.
3. Permita os escopos solicitados para leitura e gravação nas planilhas.
4. Após o sucesso da autenticação, o navegador exibirá uma mensagem confirmando e você poderá fechar a aba.
5. O script criará automaticamente o arquivo `token.json` na raiz do projeto. Esse token expira em alguns dias, mas o robô possui mecanismo de atualização automática em segundo plano (*auto-refresh*), permitindo que você nunca mais precise interagir de forma visual no navegador!

> 🔒 **Segurança:** O arquivo `credentials.json` e o `token.json` contêm credenciais de acesso às suas planilhas e já estão adicionados no arquivo `.gitignore` do projeto para impedir que sejam expostos acidentalmente em repositórios Git públicos.
