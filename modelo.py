import nltk
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.cluster import KMeans
import joblib

# Função para tokenização e remoção de stopwords
def preprocess_text(text):
    # Garantir que o texto seja uma string
    text = str(text)
    
    stop_words = set(stopwords.words('portuguese'))
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)


# Função para pré-processamento do DataFrame
def pre_processamento(filmes):
    # Remover filmes duplicados com base no título e sinopse (ajuste conforme necessário)
    filmes = filmes.drop_duplicates(subset=['titulo', 'sinopse'], keep='last')
    
    filmes = filmes[['titulo_original', 'sinopse', 'generos', 'diretor', 'elenco', 'data_lancamento',
                     'popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao',
                     'idioma', 'classificacao_etaria', 'palavras_chave']].copy()
                     
    filmes.rename(columns={'titulo_original': 'tittle', 'data_lancamento': 'lancamento',
                           'classificacao_etaria': 'idade', 'palavras_chave': 'keywords'}, inplace=True)
    
    # Preprocessamento de colunas de texto
    filmes['tittle'] = filmes['tittle'].apply(preprocess_text)
    filmes['elenco'] = filmes['elenco'].apply(preprocess_text)
    filmes['sinopse'] = filmes['sinopse'].apply(lambda x: preprocess_text(str(x)))
    
    # Vetorização TF-IDF para 'sinopse' e 'keywords'
    tfidf_vectorizer = TfidfVectorizer(max_features=500)
    filmes['sinopse_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['sinopse'].fillna('')).toarray())
    filmes['keywords_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['keywords'].fillna('')).toarray())
    filmes['diretor_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['diretor'].fillna('')).toarray())
    filmes['idioma_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['idioma'].fillna('')).toarray())
    filmes['elenco_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['elenco'].fillna('')).toarray())

    # Extrair ano e calcular idade do filme
    filmes['ano_lancamento'] = pd.to_datetime(filmes['lancamento'], errors='coerce').dt.year
    filmes['idade_filme'] = 2024 - filmes['ano_lancamento']
    
    # Concatenar todas as características em um DataFrame final
    filmes.rename(columns={'titulo_original': 'title', 'data_lancamento': 'lancamento',
                       'classificacao_etaria': 'idade', 'palavras_chave': 'keywords'}, inplace=True)

   
    
    return filmes


def modelo(filmes_processados, filmes):
    filmes_processados = filmes_processados[filmes['votos'] > 100]
    
    # Garantir que todos os nomes de colunas são strings
    filmes_processados.columns = filmes_processados.columns.astype(str)

    filmes_processados = filmes_processados.fillna(0)
    filmes_processados = pd.DataFrame()
    model = KMeans(n_clusters=1000)   
    model.fit(filmes_processados[''])
    

def main():
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes_processados = pre_processamento(filmes)
    filmes = pre_processamento(filmes)
    filmes_processados.to_csv('filmes_processados.csv', index=False)
    #modelo(filmes_processados, filmes)


if __name__ == "__main__":
    main()
