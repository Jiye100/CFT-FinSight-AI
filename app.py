import google.generativeai as genai
import pandas as pd
import datascraping
from config import GEMINI_API_KEY
import rag

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

user_query = input("What can I help you with?\n")

keyword = rag.generate_keyword(user_query)

# df = datascraping.process_articles()
# datascraping.store_to_db(pd.read_csv('scraping/articles.csv'))

document = datascraping.retrieve_data()

collection = rag.create_chroma_db()
rag.add_documents_to_chroma(document, collection)

relevant_text = rag.query_chroma(user_query, collection)