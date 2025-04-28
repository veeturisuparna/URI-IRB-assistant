#!/usr/bin/env python3
"""
populate_vector_store.py

Extract text from a specified PDF file and add it to a persistent ChromaDB
vector store using the recommended PersistentClient. Assumes required packages
(chromadb, PyPDF2/etc. via doc_parser) and their dependencies are installed.
"""
import sys
from pathlib import Path
import argparse

# --- ChromaDB Import ---
# Import the main chromadb library
import chromadb
# Note: Removed 'from chromadb.config import Settings' as it's deprecated for this use case

# --- doc_parser Import ---
# Assumes doc_parser.py exists in the Python path (e.g., same directory)
# and provides an 'extract_text_from_pdf' function.
try:
    from doc_parser import extract_text_from_pdf
except ImportError:
    print("❌ Error: Failed to import 'extract_text_from_pdf' from 'doc_parser'.")
    print("Ensure 'doc_parser.py' exists and is accessible.")
    sys.exit(1)


def main(pdf_path: str):
    """
    Extract text from the given PDF and store it in a ChromaDB collection.

    Args:
        pdf_path (str): Path to the PDF file.
    """
    try:
        # Resolve the path to get a clear, absolute path
        pdf_file = Path(pdf_path).expanduser().resolve(strict=True)
    except FileNotFoundError:
        # Provide the path that was attempted for clarity
        attempted_path = Path(pdf_path).expanduser().resolve()
        print(f"❌ Error: PDF file not found at resolved path: {attempted_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error processing path '{pdf_path}': {e}")
        sys.exit(1)

    # --- ChromaDB Setup ---
    # Define the path for the persistent database directory.
    # This will be created in the current working directory if it doesn't exist.
    persist_directory = "./irb_db"
    db_path = Path(persist_directory).resolve()
    print(f"ℹ️  Using ChromaDB persistent storage at: {db_path}")

    try:
        # --- Use the NEW PersistentClient method ---
        # This is the recommended way to create a client that saves data to disk.
        # It automatically uses duckdb+parquet by default for persistence.
        client = chromadb.PersistentClient(path=str(db_path))
    except Exception as e:
        # Catch potential errors during client initialization (e.g., permissions)
        print(f"❌ Error initializing ChromaDB PersistentClient: {e}")
        sys.exit(1)

    collection_name = "appendix_b_data"
    # Consider making the collection name configurable if needed
    # Get or create the collection. This operation is idempotent.
    collection = client.get_or_create_collection(name=collection_name)

    # --- Text Extraction ---
    print(f"ℹ️  Processing '{pdf_file.name}'...")
    try:
        # >>> Consider implementing text chunking here <<<
        # For better vector search, chunk the text into smaller segments
        # (e.g., paragraphs) instead of adding the whole document at once.
        text = extract_text_from_pdf(str(pdf_file))

        if not text or not text.strip():
            print(f"⚠️ Warning: No text extracted from '{pdf_file.name}'. Check the PDF content or the parser logic.")
            # Skip adding if no text found
            return

    except Exception as err:
        print(f"❌ Error extracting text from '{pdf_file.name}': {err}")
        sys.exit(1) # Exit if extraction fails

    # --- Add to ChromaDB ---
    # Using filename stem for a simple, unique-ish ID. Adjust if needed.
    doc_id = f"appendix_b_{pdf_file.stem}"
    metadata = {"source": pdf_file.name}

    try:
        # Add the extracted text (or chunks) to the collection
        # Use upsert=True to overwrite if the ID already exists, or add if new.
        collection.add(
            ids=[doc_id],        # Use chunk IDs if chunking
            documents=[text],    # Use list of chunks if chunking
            metadatas=[metadata] # Add chunk-specific metadata if needed
        )
        print(f"✅ Successfully added/updated document ID '{doc_id}' from '{pdf_file.name}' to collection '{collection_name}'.")
        # Note: PersistentClient handles saving automatically, client.persist() is not needed.
    except Exception as e:
        print(f"❌ Error adding document ID '{doc_id}' to ChromaDB: {e}")
        # Decide if you want to exit or continue if processing multiple files
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF and populate a ChromaDB vector store."
    )
    # pdf_path is a required argument
    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file."
    )
    args = parser.parse_args()

    # argparse handles the check for missing required arguments automatically.
    main(args.pdf_path)