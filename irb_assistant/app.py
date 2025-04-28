import os
import streamlit as st
import openai
from chromadb import PersistentClient
from dotenv import load_dotenv

# ----------------------------------------------------------------------------
# API Key Setup
# ----------------------------------------------------------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API key not found. Set OPENAI_API_KEY in your .env.")
    st.stop()

# ----------------------------------------------------------------------------
# ChromaDB Setup (PersistentClient uses DuckDB+Parquet by default)
# ----------------------------------------------------------------------------
try:
    chroma_client = PersistentClient(path="./irb_db")
    collection = chroma_client.get_collection("appendix_b_data")
except Exception as e:
    st.error(f"ChromaDB error: {e}")
    st.stop()

# ----------------------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------------------
st.set_page_config(page_title="IRB Appendix B Assistant")
st.title("IRB Appendix B Assistant")
user_query = st.text_input("Enter your question about Appendix B:")

# ----------------------------------------------------------------------------
# Retrieval & Response Logic
# ----------------------------------------------------------------------------
if user_query:
    with st.spinner("Searching docs..."):
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

    if context:
        prompt = (
            "Answer based strictly on the provided IRB Appendix B context below.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {user_query}\n\n"
            "If the info isn't in the context, reply: 'I don't know based on the provided document.'"
        )
        with st.spinner("Generating answer..."):
            try:
                res = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.2
                )
                answer = res.choices[0].message.content.strip()
            except Exception as e:
                st.error(f"OpenAI error: {e}")
                answer = ""

        if answer:
            st.markdown("**Answer:**")
            st.write(answer)
    else:
        st.warning("No relevant context found.")
