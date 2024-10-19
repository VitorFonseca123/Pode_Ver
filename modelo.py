import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def pre_processamento(filmes):
    filmes = filmes[['titulo_original','sinopse','generos','diretor','elenco','data_lancamento',
                     'popularidade', 'classificacao','votos','orcamento','receita','duracao',
                     'idioma','classificacao_etaria', 'palavras_chave']]
    filmes.rename(columns={'titulo_original':'tittle', 'data_lancamento':'lancamento',
                           'classificacao_etaria':'idade', 'palavras_chave':'keywords'}, inplace=True)
    
    return filmes
    
def main():
    print("teste")
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes = pre_processamento(filmes)
    print(filmes)
if __name__ == "__main__":
    main()