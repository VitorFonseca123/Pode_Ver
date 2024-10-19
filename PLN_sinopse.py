import pandas as pd
from transformers import pipeline

def analisar_sentimento(sinopses):
    # Carregar o modelo pré-treinado para análise de sentimentos
    analisador_sentimento = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    
    # Aplicar o analisador de sentimento em cada sinopse
    resultados = []
    for sinopse in sinopses:
        sentimento = analisador_sentimento(sinopse[:512])  # Limitar o texto a 512 tokens
        resultados.append(sentimento[0])

    return resultados

def main():
    # Carregar o arquivo CSV
    filmes = pd.read_csv('filmes_populares_completos.csv')
    filmes = pd.read_csv('filmes_populares_completos.csv')
    print(filmes.head())  # Ver os primeiros 5 registros
    if 'sinopse' in filmes.columns:
        print("Coluna de sinopse encontrada!")
        print(filmes['sinopse'].head())  # Ver algumas sinopses
    else:
        print("Coluna de sinopse não encontrada!")

    # Obter a coluna de sinopses
    sinopses = filmes['sinopse'].dropna()
    print("Iniciando análise de sentimentos...")

    # Analisar o sentimento das sinopses
    resultados_sentimento = analisar_sentimento(sinopses)
    
    # Exibir os resultados
    for sinopse, resultado in zip(sinopses, resultados_sentimento):
        print(f"Sinopse: {sinopse[:100]}...")  # Mostrar apenas os primeiros 100 caracteres da sinopse
        print(f"Sentimento: {resultado['label']}, Score: {resultado['score']:.2f}")
        print("-" * 50)

    
if __name__ == "__main__":
    main()
