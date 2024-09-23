import os
from flask import Flask, request, jsonify, render_template, session
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PODEVER'

# Definir o caminho correto para o CSV
csv_path = os.path.join(os.path.dirname(__file__), 'dataset_com_titulos_portugues.csv')

# Carregar o dataset CSV
try:
    print(f"Tentando carregar o arquivo CSV de: {csv_path}")
    df = pd.read_csv(csv_path, delimiter=',', encoding='utf-8', engine='python', on_bad_lines='skip')
    print("Arquivo CSV carregado com sucesso.")
    print(f"Colunas disponíveis no DataFrame: {df.columns.tolist()}")
    if 'titulo_portugues' not in df.columns or 'Poster_Url' not in df.columns:
        raise KeyError("As colunas 'titulo_portugues' ou 'Poster_Url' não foram encontradas no arquivo CSV.")
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
        if not df.empty and 'titulo_portugues' in df.columns and 'Poster_Url' in df.columns:
            print(f"Pesquisando por filmes com o nome: {search_term}")
            results = df[df['titulo_portugues'].str.contains(search_term, case=False, na=False)]
            movies = results.to_dict(orient='records')
            if not movies:
                error = "Nenhum filme encontrado."
            else:
                print(f"Filmes encontrados: {movies}")
        else:
            error = "Erro ao carregar o dataset."
    else:
        if not df.empty and 'titulo_portugues' in df.columns and 'Poster_Url' in df.columns:
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
    
    filmes = data.get('filmes', [])
    
    # Pegar apenas o primeiro filme, se a lista não estiver vazia
    primeiro_filme = filmes[0] if filmes else None
    
    if primeiro_filme:
        print(f"Primeiro filme: {primeiro_filme}")
    else:
        print("Nenhum filme recebido")
    
    # Armazenar apenas o primeiro filme na sessão
    session['primeiro_filme'] = primeiro_filme
    
    return jsonify({'status': 'success', 'primeiro_filme': primeiro_filme})

@app.route('/resultados')
def resultados():
    # Pegar o primeiro filme da sessão (ou None se não houver)
    primeiro_filme = session.get('primeiro_filme')
    
    # Debug: Verificar se primeiro_filme está na sessão
    print(f"Primeiro filme na sessão: {primeiro_filme}")
    
    if primeiro_filme and not df.empty:
        # Debug: Verificar o conteúdo do DataFrame
        print(f"Conteúdo do DataFrame: {df.head()}")
        
        # Buscar o filme no DataFrame
        filme_info = df[df['titulo_portugues'] == primeiro_filme]
        
        # Debug: Verificar se a busca no DataFrame retornou resultados
        print(f"Informações do filme encontrado: {filme_info}")
        
        if not filme_info.empty:
            poster = filme_info.iloc[0]['Poster_Url']
            descricao = filme_info.iloc[0]['Overview'] if 'Overview' in filme_info.columns else 'Descrição não disponível'
        else:
            poster = None
            descricao = None
    else:
        poster = None
        descricao = None
    
    # Debug: Verificar os valores de poster e descricao
    print(f"Poster: {poster}, Descrição: {descricao}")
    
    return render_template('Resultados.html', filme=primeiro_filme, poster=poster, descricao=descricao)

@app.route('/Quizz')
def Quizz():
    return render_template('Quizz.html')


if __name__ == '__main__':
    app.run(debug=True)