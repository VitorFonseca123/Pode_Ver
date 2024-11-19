import nltk
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.neighbors import NearestNeighbors
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
    
    filmes = filmes[['titulo','titulo_original', 'sinopse', 'generos', 'diretor', 'elenco', 'data_lancamento',
                     'popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao',
                     'idioma', 'classificacao_etaria', 'palavras_chave', 'id']].copy()
                     
    filmes.rename(columns={'titulo_original': 'tittle', 'data_lancamento': 'lancamento',
                           'classificacao_etaria': 'idade', 'palavras_chave': 'keywords'}, inplace=True)
    
    # Preprocessamento de colunas de texto
    filmes['tittle'] = filmes['tittle'].apply(preprocess_text)
    filmes['elenco'] = filmes['elenco'].apply(preprocess_text)
    filmes['sinopse'] = filmes['sinopse'].apply(lambda x: preprocess_text(str(x)))
    
    # Vetorização TF-IDF para 'sinopse' e 'keywords'
    tfidf_vectorizer = TfidfVectorizer(max_features=500)
    
    # Transformação para cada uma das colunas
    sinopse_tfidf = tfidf_vectorizer.fit_transform(filmes['sinopse'].fillna('')).toarray()
    keywords_tfidf = tfidf_vectorizer.fit_transform(filmes['keywords'].fillna('')).toarray()
    diretor_tfidf = tfidf_vectorizer.fit_transform(filmes['diretor'].fillna('')).toarray()
    idioma_tfidf = tfidf_vectorizer.fit_transform(filmes['idioma'].fillna('')).toarray()
    elenco_tfidf = tfidf_vectorizer.fit_transform(filmes['elenco'].fillna('')).toarray()

    # Convertendo os arrays para DataFrame para manter as dimensões e dar nome às colunas
    sinopse_tfidf_df = pd.DataFrame(sinopse_tfidf, columns=[f'sinopse_tfidf_{i}' for i in range(sinopse_tfidf.shape[1])])
    keywords_tfidf_df = pd.DataFrame(keywords_tfidf, columns=[f'keywords_tfidf_{i}' for i in range(keywords_tfidf.shape[1])])
    diretor_tfidf_df = pd.DataFrame(diretor_tfidf, columns=[f'diretor_tfidf_{i}' for i in range(diretor_tfidf.shape[1])])
    idioma_tfidf_df = pd.DataFrame(idioma_tfidf, columns=[f'idioma_tfidf_{i}' for i in range(idioma_tfidf.shape[1])])
    elenco_tfidf_df = pd.DataFrame(elenco_tfidf, columns=[f'elenco_tfidf_{i}' for i in range(elenco_tfidf.shape[1])])

    # Concatenando as novas colunas de TF-IDF ao DataFrame original
    filmes = pd.concat([filmes, sinopse_tfidf_df, keywords_tfidf_df, diretor_tfidf_df, idioma_tfidf_df, elenco_tfidf_df], axis=1)
    
    # Extrair ano e calcular idade do filme
    filmes['ano_lancamento'] = pd.to_datetime(filmes['lancamento'], errors='coerce').dt.year
    filmes['idade_filme'] = 2024 - filmes['ano_lancamento']
    
    return filmes


def modelo(filmes_processados, filmes):
    
    filmes_processados = filmes_processados[filmes['votos'] > 100]
    filmes_prever = filmes
    # Garantir que todos os nomes de colunas são strings
   
    filmes_processados.columns = filmes_processados.columns.astype(str)
    filmes_prever.columns = filmes_prever.columns.astype(str)

    filmes_processados = filmes_processados.fillna(0)
    colunas_numericas = filmes_processados.select_dtypes(include=['number']).columns
    
    # Ajustando o modelo NearestNeighbors com as colunas numéricas
    model = NearestNeighbors(algorithm='auto', leaf_size=30, metric='euclidean', n_jobs=None, n_neighbors=10)
    model.fit(filmes_processados[colunas_numericas])

    ids_para_prever = [86] 
    filmes_para_prever = filmes_prever[filmes_prever['id'].isin(ids_para_prever)]
    filmes_para_prever = filmes_para_prever.fillna(0)  
    print(filmes_para_prever['titulo'])
    distance, sugestion = model.kneighbors(filmes_para_prever[colunas_numericas])
    suggestion_list = sugestion[0].tolist()  
    #print(suggestion_list[0])
    
    for i in range(suggestion_list.__len__()):
        if i != 0:
            print(filmes.iloc[[suggestion_list[i]]])
    # Salvar o modelo treinado
    #joblib.dump(model, 'modelo_nearest_neighbors.joblib')

def main():
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes_processados = pre_processamento(filmes)
    filmes = pre_processamento(filmes)
    filmes_processados.to_csv('filmes_processados.csv', index=False)
    modelo(filmes_processados, filmes)


if __name__ == "__main__":
    main()
