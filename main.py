import time
import pandas as pd
import requests
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_CONCURRENT_REQUESTS = 10

def clean_cnpj(cnpj):
    return ''.join(filter(str.isdigit, str(cnpj))).zfill(14)

def get_cnpj_data(cnpj):
    url = f"https://minhareceita.org/{cnpj}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'cnpj_consultado': cnpj,
            'razao_social': data.get('razao_social'),
            'nome_fantasia': data.get('nome_fantasia'),
            'situacao_cadastral': data.get('descricao_situacao_cadastral'),
            'data_situacao': data.get('data_situacao_cadastral'),
            'cnae_principal': data.get('cnae_fiscal_descricao'),
            'logradouro': f"{data.get('logradouro')} {data.get('numero')}",
            'municipio': data.get('municipio'),
            'uf': data.get('uf'),
            'socios': '; '.join([socio['nome_socio'] for socio in (data.get('qsa', []) or []) if socio.get('nome_socio')]),
            'capital_social': data.get('capital_social'),
            'email': data.get('email'),
            'data_inicio_atividade': data.get('data_inicio_atividade'),
            'motivo_situacao': data.get('descricao_motivo_situacao_cadastral'),
            'telefone': '55' + data.get('ddd_telefone_1'),
            'erro': None
        }
    
    except Exception as e:
        return {
            'erro': str(e)
        }

def process_cnpj(cnpj, original_number: str):
    cleaned_cnpj = clean_cnpj(cnpj)
    if len(cleaned_cnpj) != 14:
        return {
            'cnpj': cnpj,
            'erro': 'CNPJ inválido',
            'telefone': original_number
        }
    
    data = get_cnpj_data(cleaned_cnpj)
    data['cnpj'] = cnpj
    data['telefone'] = original_number or data.get('telefone', '')
    return data

def main():
    files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.csv'))]
    if not files:
        raise FileNotFoundError("Nenhum arquivo .xlsx ou .csv encontrado")
    
    input_file = sorted(files)[0]
    output_dir = 'saida'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, input_file)
    
    df = pd.read_excel(input_file) if input_file.endswith('.xlsx') else pd.read_csv(input_file)
    
    lower_columns = [col.lower() for col in df.columns]
    if 'cnpj' not in lower_columns:
        raise ValueError("Coluna 'CNPJ' não encontrada na planilha")
    if 'number' not in lower_columns:
        df['number'] = ''
    
    cnpj_col = df.columns[lower_columns.index('cnpj')]
    
    results = []
    cnpj_numbers = list(zip(df[cnpj_col], df['number']))
    
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        futures = [executor.submit(process_cnpj, cn, num) for cn, num in cnpj_numbers]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processando CNPJs"):
            results.append(future.result())
    
    result_df = pd.DataFrame(results)
    cols_order = [
        'cnpj', 'razao_social', 'nome_fantasia',
        'situacao_cadastral', 'data_situacao', 'motivo_situacao',
        'socios', 'cnae_principal', 'capital_social', 'data_inicio_atividade',
        'logradouro', 'municipio', 'uf', 'telefone', 'email', 'erro'
    ]
    result_df = result_df.reindex(columns=cols_order)
    
    if input_file.endswith('.xlsx'):
        result_df.to_excel(output_file, index=False)
    else:
        result_df.to_csv(output_file, index=False)
    
    print(f"Arquivo processado: {output_file}")

if __name__ == "__main__":
    main()