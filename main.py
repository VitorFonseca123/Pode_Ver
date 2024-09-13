import os
from flask import Flask, request, jsonify, render_template, session
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PODEVER'

# Definir o caminho correto para o CSV
csv_path = os.path.join(os.path.dirname(__file__), 'dataset.csv')

# Carregar o dataset CSV
try:
    print(f"Tentando carregar o arquivo CSV de: {csv_path}")
    df = pd.read_csv(csv_path, delimiter=',', encoding='utf-8', engine='python', on_bad_lines='skip')
    print("Arquivo CSV carregado com sucesso.")
    print(f"Colunas disponíveis no DataFrame: {df.columns.tolist()}")
    if 'Title' not in df.columns or 'Poster_Url' not in df.columns:
        raise KeyError("As colunas 'Title' ou 'Poster_Url' não foram encontradas no arquivo CSV.")
except (pd.errors.ParserError, KeyError) as e:
    print(f"Erro ao ler o arquivo CSV: {e}")
    df = pd.DataFrame()  # Cria um DataFrame vazio em caso de erro

@app.route('/', methods=['GET', 'POST'])
def Home():
    error = None
    movies = []
    search_term = ""
    if request.method == 'POST':
        search_term = request.form.get('movie_name')
        # Verificar se o DataFrame não está vazio e contém as colunas 'Title' e 'Poster_Url'
        if not df.empty and 'Title' in df.columns and 'Poster_Url' in df.columns:
            print(f"Pesquisando por filmes com o nome: {search_term}")
            # Lógica para pesquisar o filme no dataset
            results = df[df['Title'].str.contains(search_term, case=False, na=False)]
            movies = results.to_dict(orient='records')
            if not movies:
                error = "Nenhum filme encontrado."
            else:
                print(f"Filmes encontrados: {movies}")
        else:
            error = "Erro ao carregar o dataset."
    return render_template('AdicionarFilme.html', movies=movies, error=error, search_term=search_term)

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
    
    if primeiro_filme and not df.empty:
        # Buscar o filme no DataFrame
        filme_info = df[df['Title'] == primeiro_filme]
        if not filme_info.empty:
            poster = filme_info.iloc[0]['Poster_Url']
            descricao = filme_info.iloc[0]['Overview'] if 'Overview' in filme_info.columns else 'Descrição não disponível'
        else:
            poster = None
            descricao = None
    else:
        poster = None
        descricao = None
    
    # Renderizar o template passando o nome do filme, pôster e descrição
    return render_template('Resultados.html', filme=primeiro_filme, poster=poster, descricao=descricao)

if __name__ == '__main__':
    app.run(debug=True)