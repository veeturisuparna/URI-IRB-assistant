# query_vector_store.py

import sys
import chromadb
from chromadb.config import Settings

def get_chroma_client(db_path: str = "./irb_db"):
    """
    Initialize and return a persistent ChromaDB client.
    """
    try:
        # Connect to the same persistent store used by populate_vector_store.py
        client = chromadb.PersistentClient(path=db_path)
        return client
    except Exception as e:
        print(f"Error initializing ChromaDB client: {e}", file=sys.stderr)
        sys.exit(1)

def get_collection(client, name: str):
    """
    Retrieve an existing collection by name. Exit if not found.
    """
    try:
        existing = [col.name for col in client.list_collections()]
        if name not in existing:
            print(f"Collection '{name}' not found. Available collections: {existing}", file=sys.stderr)
            sys.exit(1)
        return client.get_collection(name=name)
    except Exception as e:
        print(f"Error fetching collection '{name}': {e}", file=sys.stderr)
        sys.exit(1)

def query_appendix_b(collection, query_text: str, n_results: int = 3):
    """
    Query the 'appendix_b_data' collection for the given text.
    Returns a list of retrieved document strings.
    """
    try:
        result = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return result.get("documents", [])[0]  # documents is a list of lists
    except Exception as e:
        print(f"Error during query: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    # Example usage
    CLIENT = get_chroma_client(db_path="./irb_db")
    COLLECTION_NAME = "appendix_b_data"

    # Ensure the collection exists before querying
    collection = get_collection(CLIENT, COLLECTION_NAME)

    # Sample queries
    sample_queries = [
        "minimal risk",
        "category 7 research examples"
    ]

    for q in sample_queries:
        print(f"\nQuery: '{q}'")
        docs = query_appendix_b(collection, q, n_results=3)
        if not docs:
            print("  No results found.")
        else:
            for i, doc in enumerate(docs, start=1):
                print(f"  Result {i}: {doc}\n")
