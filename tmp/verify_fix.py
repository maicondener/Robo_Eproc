import pandas as pd
import os
import json

# Simula o processamento que ocorre em relatorio_conclusos.py
def process_data(file_path):
    # A correção aplicada: dtype=str
    df = pd.read_excel(file_path, dtype=str)
    
    records = []
    for _, row in df.iterrows():
        records.append({
            "numero_processo": str(row.get('PROCESSO', row.get('Nº do Processo', ''))),
            "vara": str(row.get('VARA', '')),
        })
    return records

# 1. Criar Excel Mock
data = {
    'PROCESSO': ['00012345678901234567', '00000001234567890123'],
    'VARA': ['Vara 1', 'Vara 2']
}
df_mock = pd.DataFrame(data)
test_file = 'test_zeros.xlsx'
df_mock.to_excel(test_file, index=False)

# 2. Processar
print("Processando dados com a correção...")
results = process_data(test_file)

# 3. Validar
success = True
for i, rec in enumerate(results):
    original = data['PROCESSO'][i]
    processed = rec['numero_processo']
    print(f"Original: {original} | Processado: {processed}")
    if original != processed:
        print(f"❌ FALHA: Zeros perdidos no item {i}!")
        success = False
    else:
        print(f"✅ SUCESSO: Item {i} preservado.")

# Limpeza
if os.path.exists(test_file):
    os.remove(test_file)

if success:
    print("\n--- VERIFICAÇÃO CONCLUÍDA COM SUCESSO ---")
else:
    print("\n--- VERIFICAÇÃO FALHOU ---")
    exit(1)
