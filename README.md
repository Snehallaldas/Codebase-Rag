# 🔍 Codebase RAG — AI-Powered Code Understanding System

A Retrieval-Augmented Generation (RAG) system that lets you upload any GitHub repository and ask natural language questions about the codebase. Supports Python, JavaScript, TypeScript, HTML, JSON, and Markdown files.

Built as a Final Year CS Project.

---

## 🚀 What it does

- **Ingests** any public GitHub repository via URL (clones via Git or downloads as ZIP if Git is unavailable)
- **Parses** files using AST-based chunking for Python and regex-based chunking for JavaScript/TypeScript
- **Embeds** code chunks using Mistral AI embeddings and stores them in **Pinecone Cloud Vector Database**
- **Answers** natural language questions with file path + line number citations
- **Critiques** its own answers using a second Mistral AI agent (faithfulness, relevance, completeness)
- **Summarizes** entire codebase architecture automatically

---

## 💬 Example Questions You Can Ask

- "Where is authentication handled?"
- "How are resumes parsed?"
- "What database models exist?"
- "Explain the architecture"
- "What is the name of the person in this portfolio?"
- "What happens on app startup?"

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Vector Store | **Pinecone** (Cloud) |
| Embeddings | Mistral AI (`mistral-embed`) |
| LLM | Mistral AI |
| Python Parsing | Python `ast` module |
| JS/TS Parsing | Regex-based chunker |
| Repo Ingestion | GitPython + ZIP fallback |
| Frontend | Streamlit |

---

## 📁 Project Structure
```
codebase_rag/
├── architect/
│   ├── __init__.py
│   └── summarizer.py        # Broad sampling → architecture summary
├── critic/
│   ├── __init__.py
│   ├── critic_agent.py      # Score answers (faithfulness, relevance, completeness)
│   └── feedback_store.py    # Log feedback to JSONL
├── ingestion/
│   ├── __init__.py
│   ├── ast_chunker.py       # AST chunking (Python) + regex chunking (JS/HTML/JSON/MD)
│   ├── embedder.py          # Embed + store chunks in Pinecone
│   ├── repo_loader.py       # Clone GitHub repos (with ZIP fallback), collect supported files
│   └── run_ingest.py        # Standalone ingestion script
├── retrieval/
│   ├── __init__.py
│   ├── embeddings.py        # Mistral AI embedding API wrapper
│   ├── generator.py         # Mistral AI answer generation
│   ├── prompt_builder.py    # Build code-aware prompts with citations
│   └── retriever.py         # Query Pinecone
├── .gitignore
├── config.py                # Centralized configuration (env vars)
├── feedback_log.jsonl        # Auto-generated query feedback log
├── main.py                  # FastAPI app
├── README.md
├── render.yaml              # Render deployment config
├── requirements.txt
└── ui.py                    # Streamlit frontend
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
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=codebase-rag
```

> **Get your API keys:**
> - Mistral AI: https://console.mistral.ai/
> - Pinecone: https://app.pinecone.io/ (free tier available)

Optional:
```
ENABLE_INGEST=true
API_URL=http://127.0.0.1:8000
```

---

## ▶️ Running the App

**Terminal 1 — Start the backend:**
```bash
uvicorn main:app --reload
```

**Terminal 2 — Start the frontend:**
```bash
python -m streamlit run ui.py
```

Then open:
- **Streamlit UI** → `http://localhost:8501`
- **Swagger API** → `http://localhost:8000/docs`

---

## 📥 Ingesting a Repository

You can ingest any public GitHub repository either through the UI or the CLI.

### Via Streamlit UI
1. Open `http://localhost:8501`
2. Paste a GitHub URL in the **Ingest a Repo** section
3. Click **Ingest**

### Via CLI (Offline / Local)
```bash
python ingestion/run_ingest.py https://github.com/owner/repo
```

This will clone the repo (or download it as a ZIP if Git is unavailable), chunk supported files, generate Mistral embeddings, and upload vectors to your Pinecone index.

---

## ☁️ Render Deployment

Use `render.yaml` or configure a Render web service with:

- `buildCommand`: `pip install -r requirements.txt`
- `startCommand`: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**

| Key | Value |
|---|---|
| `MISTRAL_API_KEY` | Your Mistral API key |
| `PINECONE_API_KEY` | Your Pinecone API key |
| `PINECONE_INDEX_NAME` | `codebase-rag` (or your index name) |
| `ENABLE_INGEST` | `true` |

> **Note**: Since all vectors are stored in Pinecone Cloud, your data is **persistent across Render restarts** with no extra configuration needed.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Ingest a GitHub repo into Pinecone |
| POST | `/query` | Ask a question, get cited answer |
| POST | `/query/evaluated` | Ask + get critic scores |
| GET | `/architecture` | Generate full architecture summary |
| GET | `/feedback/summary` | View average critic scores |

---

## 🌐 Supported File Types

| Language | Extensions |
|---|---|
| Python | `.py` |
| JavaScript / TypeScript | `.js` `.ts` `.jsx` `.tsx` |
| HTML | `.html` `.htm` |
| JSON | `package.json` `data.json` `content.json` |
| Markdown | `.md` |

---

## 📊 Sample Evaluation Results

| Question | Faithfulness | Relevance | Completeness | Overall |
|---|---|---|---|---|
| How are resumes parsed? | 7 | 9 | 6 | 7 |
| What is the app's architecture? | 8 | 9 | 7 | 8 |

---

## 🗺️ System Architecture
```
GitHub URL
    ↓
Repo Loader (GitPython / ZIP fallback)
    ↓
AST / Regex Chunker (Python, JS, HTML, JSON, MD)
    ↓
Mistral AI Embeddings
    ↓
Pinecone Cloud Vector Database
    ↓
User Question → Semantic Retrieval → Mistral AI → Cited Answer
                                          ↓
                                    Critic Agent
                                    (faithfulness / relevance / completeness)
                                          ↓
                                   Feedback Log (JSONL)
```

---

## 🔮 Future Work

- Multi-language support via tree-sitter (Java, Go, Rust)
- Call graph tracing for dependency analysis
- Auto TOP_K tuning based on feedback scores
- Fine-tuning embeddings on code-specific datasets
- Support for private GitHub repositories

---

## 👤 Author

**Snehal Laldas**
Final Year CS Project
GitHub: [@Snehallaldas](https://github.com/Snehallaldas)