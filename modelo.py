import nltk
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.neighbors import NearestNeighbors

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
    # Fazendo uma cópia explícita para evitar o aviso SettingWithCopyWarning
    filmes = filmes[['titulo_original', 'sinopse', 'generos', 'diretor', 'elenco', 'data_lancamento',
                     'popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao',
                     'idioma', 'classificacao_etaria', 'palavras_chave']].copy()
                     
    filmes.rename(columns={'titulo_original': 'tittle', 'data_lancamento': 'lancamento',
                           'classificacao_etaria': 'idade', 'palavras_chave': 'keywords'}, inplace=True)

    # Preprocessamento de colunas de texto
    filmes['tittle'] = filmes['tittle'].apply(preprocess_text)
    filmes['sinopse'] = filmes['sinopse'].apply(lambda x: preprocess_text(str(x)))
    
    # Vetorização TF-IDF para 'sinopse' e 'keywords'
    tfidf_vectorizer = TfidfVectorizer(max_features=500)
    filmes['sinopse_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['sinopse'].fillna('')).toarray())
    filmes['keywords_tfidf'] = list(tfidf_vectorizer.fit_transform(filmes['keywords'].fillna('')).toarray())
    
    # Extrair ano e calcular idade do filme
    filmes['ano_lancamento'] = pd.to_datetime(filmes['lancamento'], errors='coerce').dt.year
    filmes['idade_filme'] = 2024 - filmes['ano_lancamento']
    
    # Normalizar colunas numéricas
    scaler = MinMaxScaler()
    filmes[['popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao']] = scaler.fit_transform(
        filmes[['popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao']].fillna(0)
    )
    
    # Concatenar todas as características em um DataFrame final
    filmes = pd.concat([
        filmes[['tittle', 'diretor', 'ano_lancamento', 'idade_filme', 'popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao']],
        pd.DataFrame(filmes['sinopse_tfidf'].to_list()), pd.DataFrame(filmes['keywords_tfidf'].to_list())
    ], axis=1)
    
    return filmes

def main():
    print("Teste de pré-processamento")
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes = pre_processamento(filmes)
    print(filmes.head())  # Mostrar as primeiras linhas para verificar o pré-processamento

    # Salvar o DataFrame final em um arquivo CSV
    filmes.to_csv('filmes_processados.csv', index=False)
    print("DataFrame salvo como 'filmes_processados.csv'")

if __name__ == "__main__":
    main()