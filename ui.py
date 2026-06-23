# ui.py
import os
import streamlit as st
import requests

API = os.getenv("API_URL", "https://codebase-rag-nz9j.onrender.com/").rstrip("/")

st.title("Codebase RAG")

# Ingest
st.header("1. Ingest a Repo")
url = st.text_input("GitHub URL")
if st.button("Ingest"):
    if not url.strip():
        st.warning("Please enter a GitHub repository URL.")
    else:
        with st.spinner("Ingesting repository... This can take up to a minute."):
            try:
                res = requests.post(f"{API}/ingest", json={"github_url": url.strip()}, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Successfully ingested! Stored {data.get('chunks_stored', 0)} chunks.")
                else:
                    try:
                        err_detail = res.json().get("detail", res.text)
                    except Exception:
                        err_detail = res.text
                    st.error(f"Ingestion failed (HTTP {res.status_code}): {err_detail}")
            except Exception as e:
                st.error(f"Failed to connect to backend API: {e}")

# Architecture
st.header("2. Architecture Summary")
if st.button("Generate"):
    with st.spinner("Generating architecture summary..."):
        try:
            res = requests.get(f"{API}/architecture", timeout=90)
            if res.status_code == 200:
                data = res.json()
                st.success("Architecture summary generated successfully!")
                st.markdown(data.get("summary", ""))
            else:
                try:
                    err_detail = res.json().get("detail", res.text)
                except Exception:
                    err_detail = res.text
                st.error(f"Failed to generate summary (HTTP {res.status_code}): {err_detail}")
        except Exception as e:
            st.error(f"Failed to connect to backend API: {e}")

# Query
st.header("3. Ask a Question")
question = st.text_input("Question")
if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching and generating answer..."):
            try:
                res = requests.post(f"{API}/query/evaluated", json={"question": question.strip()}, timeout=90)
                if res.status_code == 200:
                    data = res.json()
                    st.markdown(data.get("answer", ""))
                    st.json(data.get("scores", {}))
                    st.subheader("Sources")
                    sources = data.get("sources", [])
                    if not sources:
                        st.info("No sources cited.")
                    for s in sources:
                        st.code(f"{s.get('file', 'unknown')} — {s.get('name', 'unknown')} (lines {s.get('lines', 'unknown')}) | score: {s.get('score', 0)}")
                else:
                    try:
                        err_detail = res.json().get("detail", res.text)
                    except Exception:
                        err_detail = res.text
                    st.error(f"Query failed (HTTP {res.status_code}): {err_detail}")
            except Exception as e:
                st.error(f"Failed to connect to backend API: {e}")