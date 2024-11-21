import os
import pickle
from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PODEVER'

# Definir o caminho correto para o CSV
csv_path = os.path.join(os.path.dirname(__file__), 'filmes_populares_completos.csv')

# Carregar o dataset CSV
try:
    print(f"Tentando carregar o arquivo CSV de: {csv_path}")
    df = pd.read_csv(csv_path, delimiter=',', encoding='utf-8', engine='python', on_bad_lines='skip')
    print("Arquivo CSV carregado com sucesso.")
    print(f"Colunas disponíveis no DataFrame: {df.columns.tolist()}")
    if 'titulo' not in df.columns or 'poster_url' not in df.columns:
        raise KeyError("As colunas 'titulo' ou 'poster_url' não foram encontradas no arquivo CSV.")
except (pd.errors.ParserError, KeyError) as e:
    print(f"Erro ao ler o arquivo CSV: {e}")
    df = pd.DataFrame()  # Cria um DataFrame vazio em caso de erro
@app.route('/')
def Home():
    return render_template('Home.html')

@app.route('/AdicionarFilme', methods=['GET', 'POST'])
def AdicionarFilme():
    error = None
    movies = []
    search_term = ""

    if request.method == 'POST':
        search_term = request.form.get('movie_name')
    elif request.method == 'GET':
        search_term = request.args.get('movie_name')

    if search_term:
        if not df.empty and 'titulo' in df.columns and 'poster_url' in df.columns:
            print(f"Pesquisando por filmes com o nome: {search_term}")
            results = df[df['titulo'].str.contains(search_term, case=False, na=False)]
            movies = results.to_dict(orient='records')
            if not movies:
                error = "Nenhum filme encontrado."
            else:
                print(f"Filmes encontrados: {movies}")
        else:
            error = "Erro ao carregar o dataset."
    else:
        if not df.empty and 'titulo' in df.columns and 'poster_url' in df.columns:
            movies = df.sample(n=10).to_dict(orient='records')  # Seleciona 5 filmes aleatórios
            print(f"Filmes aleatórios exibidos: {movies}")
        else:
            error = "Erro ao carregar o dataset."

    return render_template('AdicionarFilme.html', movies=movies, error=error)

@app.route('/enviar_filmes', methods=['POST'])
def enviar_filmes():
    print("Endpoint /enviar_filmes foi chamado")
    data = request.get_json()
    print(f"Dados recebidos: {data}")
    
    # Obter a lista de filmes da solicitação
    filmes = data.get('filmes', [])
    
    if filmes:
        print(f"Filmes recebidos: {filmes}")
    
    # Armazenar todos os filmes na sessão
    session['filmesAdicionados'] = filmes
    
    # Retornar todos os filmes na resposta
    return jsonify({'status': 'success', 'filmes': filmes})

def load_model_from_chunks(base_filename, num_chunks):
    serialized_model = b""
    for idx in range(1, num_chunks + 1):
        file_name = f"{base_filename}_part{idx}.pkl"
        with open(file_name, "rb") as f:
            data = f.read()
            serialized_model += data
            print(f"Lido: {file_name}, tamanho: {len(data)} bytes")
    return pickle.loads(serialized_model)

@app.route('/resultados')
def resultados():
    # Carregar o arquivo CSV contendo os filmes processados
    filmes_completos = pd.read_csv('filmes_processados.csv')

    # Obter a lista de filmes armazenados na sessão
    filmes = session.get('filmesAdicionados', [])
    
    # Lista para armazenar os filmes cujo título seja igual ao do csv
    filmes_resultados = []
    id_filmes = []
    
    for i in filmes:
        filme_info = filmes_completos[filmes_completos['titulo'] == i]
        id_filmes.append(filme_info['id'].iloc[0].tolist())
    
    filmes_para_prever = filmes_completos[filmes_completos['id'].isin(id_filmes)]
    filmes_para_prever = filmes_para_prever.fillna(0)
    
    model_Reload = load_model_from_chunks('modelo_filmes', 3)
    colunas_numericas = filmes_completos.select_dtypes(include=['number']).columns
    distance, sugestion = model_Reload.kneighbors(filmes_para_prever[colunas_numericas])
    
    # Agora vamos pegar todos os filmes sugeridos para todos os filmes em filmes_para_prever
    filmes_sugeridos = []
    for i in range(len(sugestion)):  # Iterar sobre todos os filmes em filmes_para_prever
        for j in range(1, len(sugestion[i])):  # Começar de 1 para não pegar o próprio filme
            filme_sugerido = filmes_completos.iloc[sugestion[i][j]]  # Adiciona a linha completa do filme
            filmes_sugeridos.append(filme_sugerido)  # Adiciona o DataFrame completo à lista
    #print(len(filmes_sugeridos))
    # Filtrar os filmes sugeridos que não estão na lista de filmes já escolhidos
    filmes_sugeridos_unicos = [filme for filme in filmes_sugeridos if filme['titulo'] not in filmes]

    # Sortear um filme único
    filme_sorteado = random.choice(filmes_sugeridos_unicos)

    if not filme_sorteado.empty:
        filme_nome = filme_sorteado['titulo']
        poster = filme_sorteado['poster_url']
        descricao = filme_sorteado['sinopse'] if 'sinopse' in filme_sorteado else 'Descrição não disponível'
    else:
        poster = None
        descricao = None
    
    return render_template('Resultados.html', filme=filme_nome, poster=poster, descricao=descricao)



@app.route('/Quizz')
def Quizz():
    return render_template('Quizz.html')


if __name__ == '__main__':
    app.run(debug=True)