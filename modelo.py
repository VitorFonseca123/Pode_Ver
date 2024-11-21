import nltk
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.neighbors import NearestNeighbors
import pickle

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
    num_chunks = save_model_in_chunks(model, 'modelo_filmes', chunk_size=50)
    print(num_chunks)
    ids_para_prever = [86] 
    filmes_para_prever = filmes_prever[filmes_prever['id'].isin(ids_para_prever)]
    filmes_para_prever = filmes_para_prever.fillna(0)  
    print(filmes_para_prever['titulo'])
    model_Reload = load_model_from_chunks('modelo_filmes', num_chunks)
    distance, sugestion = model_Reload.kneighbors(filmes_para_prever[colunas_numericas])
    suggestion_list = sugestion[0].tolist()  
    #print(suggestion_list[0])
    
    for i in range(suggestion_list.__len__()):
        if i != 0:
            print(filmes.iloc[[suggestion_list[i]]])
    

def save_model_in_chunks(model, base_filename, chunk_size=50):
    serialized_model = pickle.dumps(model)

    chunk_size_bytes = chunk_size * 1024 * 1024
    chunks = [serialized_model[i:i + chunk_size_bytes] for i in range(0, len(serialized_model), chunk_size_bytes)]

    for idx, chunk in enumerate(chunks):
        file_name = f"{base_filename}_part{idx + 1}.pkl"
        with open(file_name, "wb") as f:
            f.write(chunk)
        print(f"Salvou: {file_name}, tamanho: {len(chunk)} bytes")

    return len(chunks)  # Retorna o número total de partes


def load_model_from_chunks(base_filename, num_chunks):
    serialized_model = b""
    for idx in range(1, num_chunks + 1):
        file_name = f"{base_filename}_part{idx}.pkl"
        with open(file_name, "rb") as f:
            data = f.read()
            serialized_model += data
            print(f"Lido: {file_name}, tamanho: {len(data)} bytes")
    return pickle.loads(serialized_model)

def main():
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes_processados = pre_processamento(filmes)
    filmes = pre_processamento(filmes)
    filmes_processados.to_csv('filmes_processados.csv', index=False)
    modelo(filmes_processados, filmes)


if __name__ == "__main__":
    main()
