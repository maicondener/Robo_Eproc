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
| **`loc_mandados`** | Extrai processos do localizador **"MANDADOS - CITAÇÃO/INTIMAÇÃO ELETRÔNICA"** e sincroniza incrementalmente com Google Sheets. | Planilha ativa no Google Sheets (`1ZoB5WItw1KwY4zIkrfLhAtWmgIDMbLNJRaCSM0Il6po`) |
| **`alvaras_eletronicos`** | Extrai **Relatório de Alvarás** e sincroniza com Google Drive. | `dataset_alvarás.xlsx` (Drive) |
| **`relatorio_conclusos`** | Extrai **Relatório de Processos Conclusos** e envia para LegalMind API. | `data/relatorio_conclusos.csv` |
| **`exemplo_extracao`** | Script de demonstração/tutorial. | N/A |

### 📂 Saída de Dados e Sincronização Incremental

Os scripts agora são configurados para enviar os dados **diretamente para a API do LegalMind**.
Embora arquivos CSV ainda possam ser gerados como backup em `data/`, o fluxo principal de trabalho é a ingestão automática pelo sistema Core.

A integração é realizada através do módulo `src.utils.integracao_legalmind`, utilizando as variáveis de ambiente `LEGALMIND_API_URL` e `LEGALMIND_API_TOKEN`.

---

## 3. Sincronização do Localizador de Mandados (`loc_mandados`)

O script `loc_mandados` possui um fluxo de sincronização bidirecional e incremental com o Google Sheets v4 e o LegalMind Core.

### Fluxo de Trabalho do Script:
1. **Leitura de Dados Existentes:** Conecta-se à API do Google Sheets v4 e obtém os dados históricos já armazenados para identificar os processos inseridos anteriormente.
2. **Extração de Processos:** Navega no eproc até o localizador `"MANDADOS - CITAÇÃO/INTIMAÇÃO ELETRÔNICA"` e obtém o número de cada processo juntamente com a data de `"Inclusão no localizador"`.
3. **Mecanismo de Desduplicação Inteligente:**
   - **Formato Brasileiro Padrão:** As datas são processadas e formatadas como string literal no padrão `'DD/MM/AAAA - HH:MM:SS'`.
   - **Prevenção de Truncamento do Sheets:** O hífen separador no meio da data força o Google Sheets a aceitar a hora com segundos como texto bruto, impedindo que a formatação automática da planilha descarte a hora ou converta a célula para data simples (`DD/MM/AAAA`).
   - **Chave de Unicidade:** O robô utiliza a combinação de `Número do Processo` e `Data e Hora de Inclusão` para formar a chave exclusiva. Isso permite que um mesmo processo com múltiplos eventos no mesmo dia (ex: incluído às 10:00 e incluído novamente às 15:00 após alguma movimentação) seja registrado de forma limpa e separada, pulando apenas registros idênticos em segundo de precisão.
4. **Escrita em Lote (Batch Update):** Adiciona apenas registros realmente novos ao final da planilha usando lote para economizar cota de requisições.
5. **Ingestão Exclusiva no LegalMind Core:** Apenas os processos novos identificados no lote atual que foram gravados no Google Sheets são enviados para processamento na API do LegalMind Core, minimizando requisições redundantes.

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
