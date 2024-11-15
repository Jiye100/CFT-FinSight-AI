import google.generativeai as genai
import datascraping
import sys
sys.path.append("..")
from config import GEMINI_API_KEY #containing the API key
import sqlite3
from sentence_transformers import SentenceTransformer
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
raw_documents = TextLoader('../../../state_of_the_union.txt').load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)
db = Chroma.from_documents(documents, OpenAIEmbeddings())

# Path to the directory to save Chroma database
CHROMA_PATH = "chroma"
def save_to_chroma(chunks: list[Document]):
  """
  Save the given list of Document objects to a Chroma database.
  Args:
  chunks (list[Document]): List of Document objects representing text chunks to save.
  Returns:
  None
  """

  # Create a new Chroma database from the documents using OpenAI embeddings
  db = Chroma.from_documents(
    chunks,
    OpenAIEmbeddings(),
    persist_directory=CHROMA_PATH
  )

  # Persist the database to disk
  db.persist()
  print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

user_query = input("What can I help with?\n") #user enters a query
#response = model.generate_content(f"Here is a client's finance-related question: {user_query}. What are some main topics I could filter by to search for relevant news articles?")
#print(response)
#print("Converting response to dict...")
#data = response.to_dict() #converts the response to dictionary python
#response_text = data['candidates'][0]['content']['parts'][0]['text']
#print(response_text)
#TODO: revise prompt to output keywords that satisfy the formatting requirements
keyword = 'semiconductor OR microchip' # sample keyword
#df = datascraping.get_articles_using_rss(keyword)

df = datascraping.get_sample_articles()
print("Loaded the articles dataframe!")
print(df.head())
datascraping.store_to_db(df)
#TODO: Chunk data into sections
print("Stored the dataframe in the db.")

#RAG
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#TODO: Choose an embedding model
query_embedding = embedding_model.encode(user_query).tolist()
#TODO: Embed database

conn = sqlite3.connect('data.db')
cur = conn.cursor()

# First, search for the most relevant documents
#TODO: Fix this
cur.execute(
    "SELECT document_id FROM document_embeddings ORDER BY embedding <-> %s::vector LIMIT 2",
    (query_embedding,)
)
relevant_documents = [row[0] for row in cur.fetchall()]
sections = []
# Then, search for the most relevant sections within those documents

for doc_id in relevant_documents:
    cur.execute(
        "SELECT section_name, content FROM section_embeddings WHERE document_id = %s ORDER BY embedding <-> %s::vector LIMIT 2",
        (doc_id, query_embedding)
    )
    sections.extend([(doc_id, section_name, content) for section_name, content in cur.fetchall()])

cur.close()