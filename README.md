# 🔍 Codebase RAG — AI-Powered Code Understanding System

A Retrieval-Augmented Generation (RAG) system that lets you upload any GitHub repository and ask natural language questions about the codebase. Built as a final year CS project.

---

## 🚀 What it does

- **Ingests** any public GitHub repository via URL
- **Parses** Python files using AST-based chunking (by function/class boundaries)
- **Embeds** code chunks into a ChromaDB vector store
- **Answers** natural language questions with file path + line number citations
- **Critiques** its own answers using a second Mistral AI agent
- **Summarizes** entire codebase architecture automatically

---

## 💬 Example Questions You Can Ask

- "Where is authentication handled?"
- "How are resumes parsed?"
- "What database models exist?"
- "Explain the architecture"
- "What happens on app startup?"

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Mistral AI |
| AST Parsing | Python `ast` module |
| Repo Ingestion | GitPython |
| Frontend | Streamlit |

---

## 📁 Project Structure
```
codebase_rag/
├── ingestion/
│   ├── repo_loader.py       # Clone GitHub repos, collect .py files
│   ├── ast_chunker.py       # AST-based code chunking
│   └── embedder.py          # Embed + store chunks in ChromaDB
├── retrieval/
│   ├── retriever.py         # Query ChromaDB
│   ├── prompt_builder.py    # Build code-aware prompts
│   └── generator.py         # Mistral AI answer generation
├── critic/
│   ├── critic_agent.py      # Score answers (faithfulness, relevance, completeness)
│   └── feedback_store.py    # Log feedback to JSONL
├── architect/
│   └── summarizer.py        # Generate full architecture summary
├── ui.py                    # Streamlit frontend
├── main.py                  # FastAPI app
└── requirements.txt
```

---

## ⚙️ Setup

**1. Clone the repo**
```bash
git clone https://github.com/Snehallaldas/Codebase-Rag.git
cd Codebase-Rag
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file**
```
MISTRAL_API_KEY=your_mistral_api_key_here
```

---

## ▶️ Running the App

**Start the API:**
```bash
uvicorn main:app --reload
```

**Start the UI (in a separate terminal):**
```bash
python -m streamlit run ui.py
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Ingest a GitHub repo |
| POST | `/query` | Ask a question, get cited answer |
| POST | `/query/evaluated` | Ask + get critic scores |
| GET | `/architecture` | Generate full architecture summary |
| GET | `/feedback/summary` | View average critic scores |

---

## 📊 Sample Critic Scores

| Question | Faithfulness | Relevance | Completeness | Overall |
|---|---|---|---|---|
| How are resumes parsed? | 7 | 9 | 6 | 7 |

---

## 🗺️ System Architecture
```
GitHub URL
    ↓
Repo Loader (GitPython)
    ↓
AST Chunker (function/class boundaries)
    ↓
ChromaDB (vector store)
    ↓
User Question → Semantic Retrieval → Mistral AI → Cited Answer
                                          ↓
                                    Critic Agent
                                          ↓
                                   Feedback Log
```

---

## 🔮 Future Work

- Multi-language support via tree-sitter (JS, Java, Go)
- Call graph tracing for dependency analysis
- Auto TOP_K tuning based on feedback scores
- Fine-tuning embeddings on code-specific data

---

## 👤 Author

**Snehal Laldas**  
Final Year CS Project  
GitHub: [@Snehallaldas](https://github.com/Snehallaldas)