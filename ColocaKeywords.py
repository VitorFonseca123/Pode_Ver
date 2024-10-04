import os
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def buscar_detalhes_tmdb(nome_filme, api_key):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={nome_filme}&language=pt-BR"
    response = requests.get(url)
    data = response.json()

    # Verifica se encontrou resultados
    if data['total_results'] > 0:
        movie_id = data['results'][0]['id']  # Obtém o ID do primeiro filme encontrado
        return buscar_keywords_e_sinopse(movie_id, api_key)
    else:
        return {"titulo": nome_filme, "sinopse": "Não encontrada", "keywords": "Não encontradas"}

def buscar_keywords_e_sinopse(movie_id, api_key):
    # Busca sinopse e keywords
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=pt-BR"
    keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={api_key}"

    details_response = requests.get(details_url)
    keywords_response = requests.get(keywords_url)

    details_data = details_response.json()
    keywords_data = keywords_response.json()

    sinopse = details_data.get('overview', 'Sinopse não disponível')
    keywords = ', '.join([kw['name'] for kw in keywords_data.get('keywords', [])])

    return {"titulo": details_data['title'], "sinopse": sinopse, "keywords": keywords}

def carregar_csv(csv_path):
    try:
        print(f"Tentando carregar o arquivo CSV de: {csv_path}")
        df = pd.read_csv(csv_path, delimiter=',', encoding='utf-8', engine='python', on_bad_lines='skip')
        print("Arquivo CSV carregado com sucesso.")
        print(f"Colunas disponíveis no DataFrame: {df.columns.tolist()}")
        if 'Title' not in df.columns:
            raise KeyError("A coluna 'Title' não foi encontrada no arquivo CSV.")
        return df
    except (pd.errors.ParserError, KeyError) as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return pd.DataFrame()  # Cria um DataFrame vazio em caso de erro

def atualizar_titulos(df, api_key):
    def buscar_e_atualizar_detalhes(titulo_original):
        return buscar_detalhes_tmdb(titulo_original, api_key)
    
    # Usa o ThreadPoolExecutor para paralelizar as requisições
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(buscar_e_atualizar_detalhes, titulo): index for index, titulo in df['Title'].items()}
        resultados = {}

        for future in as_completed(futures):
            index = futures[future]  # Pega o índice original
            try:
                detalhes = future.result()
                print(f"Título original: {df.at[index, 'Title']} -> Título em português: {detalhes['titulo']}")
                print(f"Sinopse: {detalhes['sinopse']}")
                print(f"Keywords: {detalhes['keywords']}")
                resultados[index] = detalhes
            except Exception as exc:
                print(f"Ocorreu um erro ao processar o título no índice {index}: {exc}")
                resultados[index] = {"titulo": df.at[index, 'Title'], "sinopse": "Erro ao buscar sinopse", "keywords": "Erro ao buscar keywords"}

    # Converte os resultados em DataFrame, alinhando pelo índice original
    detalhes_df = pd.DataFrame.from_dict(resultados, orient='index')
    df = pd.concat([df, detalhes_df], axis=1)

    df.to_csv('dataset_com_titulos_e_detalhes.csv', index=False)
    print("Arquivo atualizado salvo como 'dataset_com_titulos_e_detalhes.csv'")

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
