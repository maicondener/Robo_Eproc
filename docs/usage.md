# 🚀 Como Usar

O Robô Eproc pode ser executado de duas maneiras principais: via **Linha de Comando (CLI)** ou via **API Web**.

## 1. Execução via Linha de Comando (CLI)

Esta é a forma mais direta de rodar as automações, ideal para testes ou execuções agendadas.

### Comando Básico

```bash
python -m src.main --script <NOME_DO_SCRIPT>
```

### Opções Úteis

- `--show-browser`: Força a exibição do navegador (ignora a configuração `HEADLESS=True` do `.env`). Útil para depuração.

Exemplo:
```bash
python -m src.main --script loc_peticoes --show-browser
```

### 📜 Scripts Disponíveis

Atualmente, o robô possui os seguintes scripts de extração:

| Script | Descrição | Arquivo de Saída |
| :--- | :--- | :--- |
| **`loc_peticoes`** | Extrai processos do localizador **"PETIÇÃO"**. | `data/processos_peticao.csv` |
| **`loc_peticao_inicial`** | Extrai processos do localizador **"PETIÇÃO INICIAL"**. | `data/processos_peticao_inicial.csv` |
| **`loc_urgente`** | Extrai processos do localizador **"URGENTE"**. | `data/processos_urgente.csv` |
| **`exemplo_extracao`** | Script de demonstração/tutorial. | N/A |

### 📂 Saída de Dados (Integração Direta)

Os scripts agora são configurados para enviar os dados **diretamente para a API do LegalMind**.
Embora arquivos CSV ainda possam ser gerados como backup em `data/`, o fluxo principal de trabalho é a ingestão automática pelo sistema Core.

A integração é realizada através do módulo `src.utils.integracao_legalmind`, utilizando as variáveis de ambiente `LEGALMIND_API_URL` e `LEGALMIND_API_TOKEN`.

---

## 2. Execução via API Web

O projeto inclui uma API construída com **FastAPI**, permitindo que outros sistemas acionem os robôs.

### Iniciando o Servidor

```bash
uvicorn src.main:app --reload
```
O servidor iniciará em `http://127.0.0.1:8000`.

### Documentação da API (Swagger UI)

Acesse **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** para visualizar a documentação interativa da API. Lá você pode testar os endpoints diretamente pelo navegador.

### Endpoints Principais

- **`GET /`**: Verifica o status da API e as configurações carregadas.
- **`POST /run/{script_name}`**: Executa o script especificado.
    - Exemplo de chamada: `POST http://127.0.0.1:8000/run/loc_peticoes`
    - Retorna um JSON com o resultado da execução:
      ```json
      {
        "success": true,
        "data": {
          "processos": ["..."],
          "total": 50,
          "csv_path": "data/processos_peticao.csv"
        },
        "message": "Extração concluída...",
        "execution_time": 45.2
      }
      ```

## 3. Utilitários

### Teste de 2FA

Para verificar se sua chave secreta do 2FA está correta e gerando códigos válidos:

```bash
python -m src.scripts.test_2fa
```
Isso imprimirá o código atual no terminal. Compare com o do seu celular.
