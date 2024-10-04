import os
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def buscar_filmes_populares(api_key, pagina=1):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=pt-BR&page={pagina}"
    response = requests.get(url)
    data = response.json()
    return data.get('results', [])

def buscar_classificacao_etaria(movie_id, api_key):
    release_info_url = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates?api_key={api_key}"
    release_info_response = requests.get(release_info_url)
    release_info_data = release_info_response.json()

    classificacao_etaria = 'Não disponível'
    
    for release in release_info_data.get('results', []):
        if release['iso_3166_1'] == 'BR':  # Filtra para o Brasil
            for info in release.get('release_dates', []):
                classificacao_etaria = info.get('certification', 'Não disponível')
            break
    return classificacao_etaria

def buscar_detalhes_completos(movie_id, api_key):
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=pt-BR"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
    
    details_response = requests.get(details_url)
    credits_response = requests.get(credits_url)
    
    details_data = details_response.json()
    credits_data = credits_response.json()

    # Extrai informações principais
    titulo_original = details_data.get('original_title', 'Título original não disponível')
    titulo = details_data.get('title', 'Título não disponível')
    sinopse = details_data.get('overview', 'Sinopse não disponível')
    generos = ', '.join([g['name'] for g in details_data.get('genres', [])])
    diretor = ', '.join([person['name'] for person in credits_data['crew'] if person['job'] == 'Director'])
    elenco = ', '.join([person['name'] for person in credits_data.get('cast', [])[:5]])  # Top 5 atores
    data_lancamento = details_data.get('release_date', 'Data não disponível')
    popularidade = details_data.get('popularity', 'Popularidade não disponível')
    classificacao = details_data.get('vote_average', 'Classificação não disponível')
    votos = details_data.get('vote_count', 'Votos não disponíveis')
    orcamento = details_data.get('budget', 'Orçamento não disponível')
    receita = details_data.get('revenue', 'Receita não disponível')
    duracao = details_data.get('runtime', 'Duração não disponível')
    idioma = details_data.get('original_language', 'Idioma não disponível')
    poster_url = f"https://image.tmdb.org/t/p/w500{details_data.get('poster_path', '')}"

    # Obtém a classificação etária
    classificacao_etaria = buscar_classificacao_etaria(movie_id, api_key)

    return {
        "titulo_original": titulo_original,
        "titulo": titulo,
        "sinopse": sinopse,
        "generos": generos,
        "diretor": diretor,
        "elenco": elenco,
        "data_lancamento": data_lancamento,
        "popularidade": popularidade,
        "classificacao": classificacao,
        "votos": votos,
        "orcamento": orcamento,
        "receita": receita,
        "duracao": duracao,
        "idioma": idioma,
        "poster_url": poster_url,
        "classificacao_etaria": classificacao_etaria
    }

def atualizar_filmes_populares(api_key, paginas=1):
    filmes_populares = []
    
    # Busca as listas de filmes populares em várias páginas
    for pagina in range(1, paginas + 1):
        filmes_populares.extend(buscar_filmes_populares(api_key, pagina))

    print(f"Encontrados {len(filmes_populares)} filmes populares.")

    # Usa o ThreadPoolExecutor para paralelizar as requisições
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(buscar_detalhes_completos, filme['id'], api_key): filme for filme in filmes_populares}
        resultados = []

        for future in as_completed(futures):
            filme = futures[future]  # Pega o filme original
            try:
                detalhes = future.result()
                resultados.append(detalhes)
            except Exception as exc:
                print(f"Erro ao processar o filme {filme['title']}: {exc}")
                resultados.append({"titulo": filme['title'], "sinopse": "Erro ao buscar detalhes", "generos": "N/A"})

    # Converte os resultados em DataFrame e salva em um CSV
    df = pd.DataFrame(resultados)
    df.to_csv('filmes_populares_completos.csv', index=False)
    print("Arquivo salvo como 'filmes_populares_completos.csv'")

def main():
    api_key = 'eacbb5672cdec9802677d54f5cb3b881'
    atualizar_filmes_populares(api_key, paginas=500)  # Pode ajustar o número de páginas para obter mais filmes

if __name__ == "__main__":
    main()
