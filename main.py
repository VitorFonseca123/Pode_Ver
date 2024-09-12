import os
from flask import Flask, render_template, request
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

if __name__ == '__main__':
    app.run(debug=True)