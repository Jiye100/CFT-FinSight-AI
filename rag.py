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
from config import GEMINI_API_KEY

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Config Gemini API Key
genai.configure(api_key=GEMINI_API_KEY)

# Directory to store the Chroma database
CHROMA_PATH = "chroma"

def generate_keyword(query):
    """
    Ask Gemini to generate a NewsAPI compatible query string based on the user's query
    Args:
        query (string): User's input query
    Returns:
        str: A single string of keywords in a format of keyword1 OR keyword2 OR ...
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"Here is a client's finance-related question: {query}. What are some main topics I could filter by to search for relevant news articles? Keep your answer short. Make sure the format is keyword1 OR keyword2 OR keyword3 ..."
    )

    data = response.to_dict()
    keywords = data['candidates'][0]['content']['parts'][0]['text']
    
    return keywords.strip()

def split_text(documents):
    """
    Split the text content of the given list of strings into smaller chunks.
    The goal is to split on semantic boundaries (e.g., sentences, paragraphs)
    and ensure that each chunk is of manageable size, so that embeddings
    can capture meaningful context.

    Strategy:
    - For each document:
      1. Split by sentences.
      2. Accumulate sentences into chunks until a certain word count limit is reached.
      3. If a chunk exceeds the limit, start a new chunk.

    Returns:
        list: List of strings representing the split text chunks.
    """
    # Maximum words per chunk (can be tuned)
    MAX_WORDS = 100
    
    all_chunks = []
    for doc in documents:
        # Rough sentence splitting on periods. More sophisticated methods could be used (e.g., nltk)
        sentences = doc.split('. ')
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Handle trailing periods:
            if sentence.endswith('.'):
                sentence = sentence[:-1].strip()
            
            words = sentence.split()
            if not words:
                continue
            
            # If adding this sentence would exceed the limit, start a new chunk
            if current_length + len(words) > MAX_WORDS:
                if current_chunk:
                    all_chunks.append(' '.join(current_chunk))
                current_chunk = words
                current_length = len(words)
            else:
                current_chunk.extend(words)
                current_length += len(words)
        
        # Add the last chunk if it exists
        if current_chunk:
            all_chunks.append(' '.join(current_chunk))

    return all_chunks

def split_text_modified(documents):
    """
    Split the text content of the given list of strings into smaller chunks.
    The goal is to split on semantic boundaries (e.g., sentences, paragraphs)
    and ensure that each chunk is of manageable size, so that embeddings
    can capture meaningful context.

    Strategy:
    - For each document:
      1. Split by sentences.
      2. Accumulate sentences into chunks until a certain word count limit is reached.
      3. If a chunk exceeds the limit, start a new chunk.

    Input: 
        documents: List of lists, where each list is a list of sentences
    Returns:
        list: List of strings representing the split text chunks.
    """
    # Maximum words per chunk (can be tuned)
    MAX_WORDS = 100
    
    all_chunks = []
    for doc in documents:
        # Rough sentence splitting on periods. More sophisticated methods could be used (e.g., nltk)
        current_chunk = []
        current_length = 0
        
        for sentence in doc:
            sentence = sentence.strip()
            # Handle trailing periods:
            if sentence.endswith('.'):
                sentence = sentence[:-1].strip()
            
            words = sentence.split()
            if not words:
                continue
            
            # If adding this sentence would exceed the limit, start a new chunk
            if current_length + len(words) > MAX_WORDS:
                if current_chunk:
                    all_chunks.append(' '.join(current_chunk))
                current_chunk = words
                current_length = len(words)
            else:
                current_chunk.extend(words)
                current_length += len(words)
        
        # Add the last chunk if it exists
        if current_chunk:
            all_chunks.append(' '.join(current_chunk))

    return all_chunks


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
    collection.add(documents=documents, ids=[str(i) for i in range(len(documents))])
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
    Generate a RAG prompt which includes a concise role description, the user's query, and relevant data.

    Args:
        query (str): User's input query
        relevant_passage (list): List of strings where each string is a relevant article chunk

    Returns:
         str: A string for the complete prompt for RAG
    """
    passages = "\n\n".join(relevant_passage)
    prompt = f"""You are an AI assistant specialized in finance-related inquiries. The user asked the following question:
"{query}"

Here are some relevant passages from external sources to help you answer the question:
{passages}

Please use the above context to provide a detailed and accurate answer to the user's query. If you refer to sources, call them "relevant external sources" without providing direct links."""
    return prompt

def generate_answer(query):
    """
    Generate a response using Gemini on the given prompt.
    The prompt should already be RAG formatted, containing both the user's query and relevant context.

    Args:
        query (str): A RAG-formatted prompt

    Returns:
       str: A formatted response including generated text and sources 
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{query}")

    data = response.to_dict()
    response = data['candidates'][0]['content']['parts'][0]['text']
    
    return response.strip()

#print(generate_answer("hello"))
