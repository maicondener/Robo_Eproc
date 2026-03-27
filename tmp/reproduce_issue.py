import pandas as pd
import os

# Simula a criação de um arquivo Excel com zeros à esquerda
data = {
    'PROCESSO': ['00012345678901234567', '00000001234567890123'],
    'Nº do Processo': ['00000000000000000001', '12345678901234567890']
}
df_orig = pd.DataFrame(data)
temp_excel = 'repro_test.xlsx'
df_orig.to_excel(temp_excel, index=False)

print("--- Lendo sem dtype (Comportamento Atual) ---")
df_read = pd.read_excel(temp_excel)
print(df_read)
for col in df_read.columns:
    print(f"Tipo da coluna {col}: {df_read[col].dtype}")
    for val in df_read[col]:
        print(f"Valor: '{val}' (tipo: {type(val)})")

print("\n--- Lendo com dtype=str (Correção Proposta) ---")
df_fixed = pd.read_excel(temp_excel, dtype=str)
print(df_fixed)
for col in df_fixed.columns:
    print(f"Tipo da coluna {col}: {df_fixed[col].dtype}")
    for val in df_fixed[col]:
        print(f"Valor: '{val}' (tipo: {type(val)})")

# Limpeza
if os.path.exists(temp_excel):
    os.remove(temp_excel)
