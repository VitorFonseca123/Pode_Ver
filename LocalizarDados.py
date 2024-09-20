import os
import pandas as pd
import requests

def buscar_titulo_tmdb(nome_filme, api_key):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={nome_filme}&language=pt-BR"
    response = requests.get(url)
    data = response.json()

    # Verifica se encontrou resultados
    if data['total_results'] > 0:
        return data['results'][0]['title']  # Retorna o primeiro título encontrado
    else:
        return nome_filme  # Se não encontrar, retorna o título original

def carregar_csv(csv_path):
    try:
        print(f"Tentando carregar o arquivo CSV de: {csv_path}")
        df = pd.read_csv(csv_path, delimiter=',', encoding='utf-8', engine='python', on_bad_lines='skip')
        print("Arquivo CSV carregado com sucesso.")
        print(f"Colunas disponíveis no DataFrame: {df.columns.tolist()}")
        if 'Title' not in df.columns or 'Poster_Url' not in df.columns:
            raise KeyError("As colunas 'Title' ou 'Poster_Url' não foram encontradas no arquivo CSV.")
        return df
    except (pd.errors.ParserError, KeyError) as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()  # Cria um DataFrame vazio em caso de erro

def atualizar_titulos(df, api_key):
    def buscar_e_substituir_titulo(titulo_original):
        titulo_portugues = buscar_titulo_tmdb(titulo_original, api_key)
        print(f"Título original: {titulo_original} -> Título em português: {titulo_portugues}")
        return titulo_portugues

    df['titulo_portugues'] = df['Title'].apply(buscar_e_substituir_titulo)
    df.to_csv('dataset_com_titulos_portugues.csv', index=False)
    print("Arquivo atualizado salvo como 'dataset_com_titulos_portugues.csv'")
    
def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'dataset_translate.csv')
    df = carregar_csv(csv_path)
    
    if not df.empty:
        api_key = 'eacbb5672cdec9802677d54f5cb3b881'
        atualizar_titulos(df, api_key)
    else:
        print("DataFrame está vazio. Nenhuma operação será realizada.")

if __name__ == "__main__":
    main()