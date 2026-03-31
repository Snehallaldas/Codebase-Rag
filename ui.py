# ui.py
import streamlit as st
import requests

API = "https://codebase-rag-h9hm.onrender.com"

st.title("Codebase RAG")

# Ingest
st.header("1. Ingest a Repo")
url = st.text_input("GitHub URL")
if st.button("Ingest"):
    res = requests.post(f"{API}/ingest", json={"github_url": url})
    st.success(f"Stored {res.json()['chunks_stored']} chunks")

# Architecture
st.header("2. Architecture Summary")
if st.button("Generate"):
    res = requests.get(f"{API}/architecture")
    st.markdown(res.json()["summary"])

# Query
st.header("3. Ask a Question")
question = st.text_input("Question")
if st.button("Ask"):
    res = requests.post(f"{API}/query/evaluated", json={"question": question})
    data = res.json()
    st.markdown(data["answer"])
    st.json(data["scores"])
    st.subheader("Sources")
    for s in data["sources"]:
        st.code(f"{s['file']} — {s['name']} (lines {s['lines']}) | score: {s['score']}")