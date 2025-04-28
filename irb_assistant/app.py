import os
import sys
import streamlit as st
import openai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
# from doc_parser import extract_text_from_pdf  # If you need to parse PDFs directly

# -----------------------------------------------------------------------------
# API Key Setup
# -----------------------------------------------------------------------------
load_dotenv()  # Load environment variables from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# ChromaDB Setup
# -----------------------------------------------------------------------------
try:
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./irb_db"
    ))
    # Attempt to get the existing collection
    collection = chroma_client.get_collection("appendix_b_data")
except Exception as e:
    st.error(f"ChromaDB error: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------
st.set_page_config(page_title="IRB Appendix B Assistant")
st.title("IRB Appendix B Assistant")

# Text input for user query
user_query = st.text_input("Enter your question about Appendix B:")

# -----------------------------------------------------------------------------
# Core Logic: Retrieval and Response Generation
# -----------------------------------------------------------------------------
if user_query:
    # Retrieve relevant context snippets from ChromaDB
    with st.spinner("Retrieving relevant context..."):
        try:
            results = collection.query(
                query_texts=[user_query],
                n_results=3,
                include=["documents"]
            )
            snippets = results["documents"][0]
            context = "\n\n".join(snippets)
        except Exception as e:
            st.error(f"Error querying ChromaDB: {e}")
            context = ""

    # If context was retrieved successfully, generate a response
    if context:
        prompt = (
            "You are an assistant that provides information based strictly on the provided context from an IRB Appendix B document.\n"
            f"Context:\n""{context}""\n\n"
            f"Question: {user_query}\n\n"
            "Answer based ONLY on the above context. If the answer is not in the context, respond with 'I don't know based on the provided document.'"
        )

        with st.spinner("Generating response..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip()
            except Exception as e:
                st.error(f"OpenAI API error: {e}")
                answer = ""

        # Display the answer
        if answer:
            st.markdown("**Answer:**")
            st.write(answer)
    else:
        st.warning("No relevant context found for your query.")