import pandas as pd
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor, as_completed

def analisar_sentimento(sinopse):
    try:
        # Carregar o modelo de sentimento
        analisador_sentimento = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        
        # Limitar o texto a 512 tokens e fazer a análise de sentimento
        return analisador_sentimento(sinopse[:512])[0]  # Retorna o primeiro resultado
    except Exception as e:
        print(f"Erro ao analisar a sinopse: {e}")
        return {'label': 'Erro', 'score': 0.0}

def processar_sinopses(sinopses):
    
    resultados = []
    total = len(sinopses)
    batch_size = 100  
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(analisar_sentimento, sinopse): sinopse for sinopse in sinopses}

        for i, future in enumerate(as_completed(futures)):
            try:
                resultado = future.result()
                resultados.append(resultado)
            except Exception as exc:
                print(f"Erro ao processar: {exc}")

            # Imprimir progresso a cada batch_size sinopses processadas
            if (i + 1) % batch_size == 0 or (i + 1) == total:
                print(f"Progresso: {i + 1} de {total} sinopses processadas ({(i + 1)/total:.2%})")
    
    return resultados

def main():
    
    filmes = pd.read_csv('filmes_populares_completos.csv')

    
    sinopses = filmes['sinopse'].dropna()

    print(f"Iniciando análise de {len(sinopses)} sinopses com threads...")

    
    resultados_sentimento = processar_sinopses(sinopses)

    
    df_resultados = pd.DataFrame({
        'sinopse': sinopses,
        'sentimento': [resultado['label'] for resultado in resultados_sentimento],
        'score': [resultado['score'] for resultado in resultados_sentimento]
    })

    
    df_resultados.to_csv('resultados_sentimento.csv', index=False)
    
    print(f"Análise concluída e resultados salvos em 'resultados_sentimento.csv'.")

if __name__ == "__main__":
    main()
