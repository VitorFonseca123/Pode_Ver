import nltk
import numpy as np
import pandas as pd
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
     # Remover filmes duplicados com base no título e sinopse (ajuste conforme necessário)
    filmes = filmes.drop_duplicates(subset=['titulo', 'sinopse'], keep='last')
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
    
    # Concatenar todas as características em um DataFrame final
    filmes = pd.concat([filmes[['tittle', 'diretor', 'ano_lancamento', 'idade_filme', 'popularidade', 'classificacao', 'votos', 'orcamento', 'receita', 'duracao']],
                        pd.DataFrame(filmes['sinopse_tfidf'].to_list()), pd.DataFrame(filmes['keywords_tfidf'].to_list())], axis=1)

    filmes = filmes[filmes['votos'] > 100]
    
    # Garantir que todos os nomes de colunas são strings
    filmes.columns = filmes.columns.astype(str)
    filmes = filmes.fillna(0)
    
    return filmes


def modelo(filmes):
    # Selecionando apenas colunas numéricas para o modelo
    filmes_numericos = filmes.select_dtypes(include=[np.number])

    # Ajustando o modelo NearestNeighbors com as colunas numéricas
    model = NearestNeighbors(algorithm='auto', leaf_size=30, metric='euclidean', n_jobs=None, n_neighbors=10)
    model.fit(filmes_numericos)

    print(filmes.iloc[[98]]['tittle']) 
    filme_para_sugerir = filmes_numericos.iloc[[98]]  
    
    # Realizando a busca por filmes semelhantes
    distance, sugestion = model.kneighbors(filme_para_sugerir)
    suggestion_list = sugestion[0].tolist()  
    #print(suggestion_list[0])
    for i in range(suggestion_list.__len__()):
        if i != 0:
            print(filmes.iloc[[suggestion_list[i]]]['tittle'])

def main():
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes = pre_processamento(filmes)
    filmes.to_csv('filmes_processados.csv', index=False)
    modelo(filmes)


if __name__ == "__main__":
    main()
