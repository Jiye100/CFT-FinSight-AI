import google.generativeai as genai
import pandas as pd
import datascraping
from config import GEMINI_API_KEY
import rag
from scraping import scrape_bbc_articles
import ast 

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

user_query = input("What can I help you with?\n")

keyword = rag.generate_keyword(user_query)

#Only need to run this once to fill bbc_articles.csv
#scrape_bbc_articles.scrape_samples()
#df = datascraping.process_articles()
df = pd.read_csv("Articles/bbc_articles.csv")

# Convert string representations of lists to actual lists
df['Headlines'] = df['Headlines'].apply(ast.literal_eval)
df['Text Body'] = df['Text Body'].apply(ast.literal_eval)
    
documents = df["Text Body"]
titles = df["Title"]
#print(documents)
print(type(documents))
chunks = rag.split_text_modified(documents)
print("----CHUNKS------")
print(len(chunks))
ids = [str(i) for i in range(len(chunks))]
print("----DOCUMENTS------")
print(len(documents))

#print (chunks[0])

#print(chunks)
# datascraping.store_to_db(pd.read_csv('scraping/articles.csv'))
#document = datascraping.retrieve_data()

# collection = rag.create_chroma_db()
# rag.add_documents_to_chroma(document, collection)

# relevant_text = rag.query_chroma(user_query, collection)

#print(documents[0])
print("\n\n\nHI HIHIHI CHUNKS BELOW\n\n\n\n")
print(chunks[0])

import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name="news_collection")

collection.upsert(
    documents=chunks,
    ids = ids
)

results = collection.query(
    query_texts=[user_query], # Chroma will embed this for you
    n_results=1 # how many results to return
)

print(results)
print(type(results))
print(type(results["documents"][0]))

print("\n\n\n\nRELEVANT CONTEXT:\n\n")
print(results["documents"][0])

final_prompt = rag.make_rag_prompt(user_query, results["documents"][0])
final_answer = rag.generate_answer(final_prompt)

print("\n\n\n\nANSWER\n\n")
print(final_answer)