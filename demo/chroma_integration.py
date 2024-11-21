import os
from chromadb import Client
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Configure Chroma
CHROMA_PATH = "chroma"  # Directory to store the Chroma database
if not os.path.exists(CHROMA_PATH):
    os.makedirs(CHROMA_PATH)

client = Client(Settings(persist_directory=CHROMA_PATH))
collection = client.get_or_create_collection(
    name="document_store",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(embedding_model)
)

def add_documents_to_chroma(documents):
    """
    Add documents to the Chroma collection.
    Args:
        documents (list): List of dictionaries with 'id', 'section_name', and 'content'.
    """
    for doc in documents:
        collection.add(
            documents=[doc["content"]],
            metadatas=[{"section_name": doc["section_name"], "document_id": doc["id"]}],
            ids=[doc["id"]]
        )
    print(f"Added {len(documents)} documents to Chroma.")

def query_chroma(user_query, k=2):
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
