import google.generativeai as genai
import pandas as pd
import datascraping
from config import GEMINI_API_KEY
import rag

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

user_query = input("What can I help you with?\n")

response = model.generate_content(f"Here is a client's finance-related question: {user_query}. What are some main topics I could filter by to search for relevant news articles? Keep your answer short. Make sure the format is keyword1 OR keyword2 OR keyword3 ...")

data = response.to_dict()
keyword = data['candidates'][0]['content']['parts'][0]['text']

# df = datascraping.process_articles()
# datascraping.store_to_db(pd.read_csv('articles.csv'))

document = datascraping.retrieve_data()

collection = rag.create_chroma_db()
rag.add_documents_to_chroma(document, collection)

relevant_text = rag.query_chroma(user_query, collection)
