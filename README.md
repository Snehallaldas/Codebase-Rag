# 🔍 Codebase RAG — AI-Powered Code Understanding System
 
> Ask natural language questions about any GitHub repository and get accurate, cited answers with file names and line numbers.
 
Built as a Final Year CS Project.
 
---
 
## 🎯 Problem Statement
 
Every developer has faced this — you join a new project, there are thousands of lines of code across hundreds of files, and you have no idea where anything is. You can't just read every file. Senior developers are busy. Documentation is outdated or missing.
 
**Codebase RAG solves this by letting you ask the codebase questions directly.**
 
---
 
## 🚀 What It Does
 
- **Ingests** any public GitHub repository via URL
- **Parses** files using AST-based chunking for Python and regex-based chunking for JavaScript/TypeScript
- **Embeds** code chunks into a ChromaDB vector store with rich metadata
- **Answers** natural language questions with exact file path and line number citations
- **Critiques** its own answers using a second Mistral AI agent (faithfulness, relevance, completeness)
- **Summarizes** entire codebase architecture automatically
- **Logs** all feedback for continuous improvement over time
 
---
 
## 💬 Example Questions
 
- "Where is authentication handled?"
- "How are resumes parsed?"
- "What database models exist?"
- "Explain the architecture of this project"
- "What happens on app startup?"
- "What is the name of the person in this portfolio?"
 
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Frontend | Streamlit |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Mistral AI |
| Python Parsing | Python built-in `ast` module |
| JS/TS Parsing | Regex-based chunker |
| Repo Ingestion | GitPython |
 
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
 
## 📁 Project Structure
 
```
codebase_rag/
├── architect/
│   ├── __init__.py
│   └── summarizer.py        # Broad sampling → architecture summary
├── critic/
│   ├── __init__.py
│   ├── critic_agent.py      # Score answers on faithfulness, relevance, completeness
│   └── feedback_store.py    # Log feedback to JSONL for continuous improvement
├── ingestion/
│   ├── __init__.py
│   ├── ast_chunker.py       # AST chunking (Python) + regex chunking (JS/HTML/JSON/MD)
│   ├── embedder.py          # Embed + store chunks in ChromaDB
│   ├── repo_loader.py       # Clone GitHub repos, collect supported files
│   └── run_ingest.py        # Standalone ingestion script
├── retrieval/
│   ├── __init__.py
│   ├── generator.py         # Mistral AI answer generation
│   ├── prompt_builder.py    # Build code-aware prompts with citations
│   └── retriever.py         # Query ChromaDB using cosine similarity
├── .gitignore
├── main.py                  # FastAPI app — all endpoints
├── README.md
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
# Windows
python -m venv venv
venv\Scripts\activate
 
# Mac/Linux
python -m venv venv
source venv/bin/activate
```
 
**3. Install dependencies**
```bash
pip install -r requirements.txt
```
 
**4. Create a `.env` file in the project root**
```
MISTRAL_API_KEY=your_mistral_api_key_here
```
 
> Get your free Mistral API key at [console.mistral.ai](https://console.mistral.ai)
 
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
- **Swagger API docs** → `http://localhost:8000/docs`
 
---
 
## 📡 API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| POST | `/ingest` | Ingest a GitHub repository |
| POST | `/query` | Ask a question, get a cited answer |
| POST | `/query/evaluated` | Ask a question + get critic scores |
| GET | `/architecture` | Generate full architecture summary |
| GET | `/feedback/summary` | View average critic scores across all queries |
 
### Example — Ingest a repo
```json
POST /ingest
{
  "github_url": "https://github.com/Snehallaldas/JobGenie-AI"
}
```
 
### Example — Ask a question
```json
POST /query/evaluated
{
  "question": "How are resumes parsed?",
  "top_k": 5
}
```
 
### Example — Response
```json
{
  "answer": "Resumes are parsed in app/services/resume_parser.py lines 1–102 using pdfplumber for PDF extraction and spaCy for NLP processing...",
  "scores": {
    "faithfulness": 7,
    "relevance": 9,
    "completeness": 6,
    "overall": 7,
    "reasoning": "Answer correctly identifies the file and accurately describes the parsing logic."
  },
  "sources": [
    {
      "file": "app/services/resume_parser.py",
      "name": "resume_parser.py",
      "lines": "1–102",
      "score": 0.81
    }
  ]
}
```
 
---
 
## 🗺️ System Architecture
 
```
GitHub URL
    ↓
Repo Loader (GitPython)
    ↓
AST / Regex Chunker
(Python → AST  |  JS/TS → Regex  |  HTML/JSON/MD → Text)
    ↓
ChromaDB Vector Store
(chunk + metadata: file path, function name, line numbers, language)
    ↓
User Question
    ↓
Semantic Retrieval (cosine similarity)
    ↓
Mistral AI → Cited Answer
    ↓
Critic Agent
(faithfulness / relevance / completeness)
    ↓
Feedback Log (JSONL)
```
 
---
 
## 📊 Evaluation Results
 
| Question | Faithfulness | Relevance | Completeness | Overall |
|---|---|---|---|---|
| How are resumes parsed? | 7 / 10 | 9 / 10 | 6 / 10 | 7 / 10 |
| What is the app architecture? | 8 / 10 | 9 / 10 | 7 / 10 | 8 / 10 |
| Where is authentication handled? | 7 / 10 | 9 / 10 | 6 / 10 | 7 / 10 |
 
> Relevance consistently scores highest (8–9), confirming the retrieval pipeline is working correctly. Completeness (6–7) reflects the top-K retrieval limit — a known improvement area.
 
---
 
## 🧠 How Chunking Works
 
Most RAG systems split code by token count — this cuts through functions mid-body and destroys semantic meaning. Codebase RAG uses semantic chunking:
 
**Python** — uses the built-in `ast` module to parse files and extract functions and classes as individual chunks. Each chunk is a complete, coherent unit of logic.
 
**JavaScript / TypeScript** — uses regex pattern matching to identify function declarations, arrow functions, class definitions, and method shorthands.
 
**HTML / JSON / Markdown** — stored as whole-file text chunks with HTML tags stripped for cleaner embedding.
 
---
 
## 🔮 Future Work
 
- Call graph tracing — follow function dependencies across files for more complete answers
- Auto TOP-K tuning — use the feedback log to automatically optimise retrieval depth
- Support for more languages via tree-sitter (Java, Go, Rust)
- Support for private GitHub repositories
- Fine-tuning embeddings on code-specific datasets
 
---
 
## 👤 Author
 
**Snehal Laldas**
Final Year CS Project
GitHub: [@Snehallaldas](https://github.com/Snehallaldas)
Repo: [Codebase-Rag](https://github.com/Snehallaldas/Codebase-Rag)
 
---
 
## 📄 License
 
MIT License — feel free to use, modify and build on this project.
