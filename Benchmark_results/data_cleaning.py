# Import libraries
import pandas as pd
import pickle

# Get rag model response
df_rag_date = pd.read_csv('./rag_result/rag.csv')
df_gpt_date = pd.read_csv('./rag_result/dates_2026.csv')

# merge df_rag_date and df_gpt_date on the date column
df_rag = pd.merge(df_rag_date, df_gpt_date, on='Date', how='inner')

print(df_rag.head())

# Get other model response:
LLM_DIR = './llm_result'
models = ['claude', 'deepseek', 'gemini', 'gpt', 'qwen', 'ollama8b']

def load_results():
    results = {}
    for model in models:
        df = pd.read_csv(f'{LLM_DIR}/{model}.csv')
        results[model] = df
    return results

results = load_results()

# Add the RAG results to the results dictionary
results['rag'] = df_rag

# some cleaning of non-trivial columns
# drop these columns if they exist (won't error if a model df doesn't have them)
cols_to_drop = [
    "Close", "Log_Return", "Monetary", "Fiscal", "Geopolitics", "News_Context",
    "Volatility_Baseline", "Volatility_Augmented"
]

for key, df_ in results.items():
    results[key] = df_.drop(columns=cols_to_drop, errors="ignore")

with open("results.pkl", "wb") as f:
    pickle.dump(results, f)

print('Done')