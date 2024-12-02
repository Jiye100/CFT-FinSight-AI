import google.generativeai as genai
from config import GEMINI_API_KEY
import chromadb
import sqlite3
from chromadb import Documents, EmbeddingFunction, Embeddings
from typing import List
import os
from chromadb import Client
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Directory to store the Chroma database
CHROMA_PATH = "chroma"

def split_text(documents):
    """
    Split the text content of the given list of string into smaller chunks
    Args:
        documents (list): List of string containing text content of the articles
    Returns:
        list: List of strings representing the split text chunks
    """
    # TODO

def create_chroma_db():
    """
    Initializes a Chroma database client and creates a collection for storing documents
    Returns:
        collection : Collection object named "document_store" that stores documents and their embeddings
    """
    # Configure Chroma
    if not os.path.exists(CHROMA_PATH):
        os.makedirs(CHROMA_PATH)

    client = Client(Settings(persist_directory=CHROMA_PATH))
    collection = client.get_or_create_collection(name="document_store", embedding_function=embedding_function)
    return collection

def add_documents_to_chroma(documents, collection):
    """
    Add documents to the Chroma collection.
    Args:
        documents (list): List of chunks (string)
        collection: Collection object that stores the documents
    """
    collection.add(documents=documents, ids=[str(id) for id in range(len(documents))])
    # for doc in documents:
    #     collection.add(
    #         documents=[doc["content"]],
    #         metadatas=[{"section_name": doc["section_name"], "document_id": doc["id"]}],
    #         ids=[doc["id"]]
    #     )
    print(f"Added {len(documents)} documents to Chroma.")

def query_chroma(user_query, collection, k=2):
    """
    Query Chroma for the most relevant documents based on the user query.
    Args:
        user_query (str): The search query from the user.
        k (int): Number of top results to return.
    Returns:
        list: Relevant document sections.
    """
    query_embedding = embedding_model.encode(user_query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    return results

def make_rag_prompt(query, relevant_passage):
    """
    Generate a RAG prompt which includes a concise role description, the user's query, and relevant data
    Args:
        query (str): User's input query
        relevant_passage (list): List of strings where each string is a relevant article chunk
    Returns:
         str: A string for the complete prompt for RAG
    """
    # TODO

def generate_answer(prompt):
    """
    Generate a response using Gemini on the given prompt
    Args:
        prompt (str): A string for the complete prompt for RAG
    Returns:
       str: A formatted response including generated text and sources 
    """
    # TODO
    