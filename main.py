# main.py
import tempfile
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from architect.summarizer import generate_architecture_summary
from ingestion.embedder import store_chunks
from ingestion.repo_loader import load_from_github
from ingestion.ast_chunker import chunk_repository_multilang
from ingestion.repo_loader import collect_supported_files
from retrieval.retriever import retrieve_chunks
from retrieval.prompt_builder import build_prompt
from retrieval.generator import generate_answer
from critic.critic_agent import score_answer
from critic.feedback_store import log_feedback, load_feedback, average_scores
from config import CHROMA_PERSIST_DIR, ENABLE_INGEST

app = FastAPI(title="Codebase RAG")


# ── Pydantic Models (MUST be defined before routes) ──────
class IngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


# ── Ingest ───────────────────────────────────────────────
@app.post("/ingest")
def ingest(req: IngestRequest):
    if not ENABLE_INGEST:
        raise HTTPException(
            status_code=403,
            detail="Ingestion is disabled in this deployment. Use a dedicated ingestion job or enable ingestion with the ENABLE_INGEST environment variable."
        )

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = load_from_github(req.github_url, tmpdir)
            files_by_lang = collect_supported_files(repo_path)

            if not any(files_by_lang.values()):
                raise HTTPException(
                    status_code=400,
                    detail="No supported files found. Supported: Python, JavaScript, TypeScript."
                )

            chunks = chunk_repository_multilang(files_by_lang, repo_path)
            store_chunks(chunks, persist_dir=CHROMA_PERSIST_DIR)

        return {
            "status": "ok",
            "chunks_stored": len(chunks),
            "files_found": {
                "python": len(files_by_lang["python"]),
                "javascript": len(files_by_lang["javascript"]),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Basic Query ──────────────────────────────────────────
@app.post("/query")
def query(req: QueryRequest):
    try:
        chunks  = retrieve_chunks(req.question, top_k=req.top_k, persist_dir=CHROMA_PERSIST_DIR)
        prompt  = build_prompt(req.question, chunks)
        answer  = generate_answer(prompt)
        return {
            "answer":  answer,
            "sources": [
                {
                    "file":   c["file_path"],
                    "name":   c["name"],
                    "lines":  f"{c['start_line']}-{c['end_line']}",
                    "score":  c["score"],
                }
                for c in chunks
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Evaluated Query ──────────────────────────────────────
@app.post("/query/evaluated")
def query_evaluated(req: QueryRequest):
    try:
        chunks  = retrieve_chunks(req.question, top_k=req.top_k, persist_dir=CHROMA_PERSIST_DIR)
        prompt  = build_prompt(req.question, chunks)
        answer  = generate_answer(prompt)
        scores  = score_answer(req.question, chunks, answer)
        log_feedback(req.question, chunks, answer, scores)
        return {
            "answer":  answer,
            "scores":  scores,
            "sources": [
                {
                    "file":   c["file_path"],
                    "name":   c["name"],
                    "lines":  f"{c['start_line']}-{c['end_line']}",
                    "score":  c["score"],
                }
                for c in chunks
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Feedback Analytics ───────────────────────────────────
@app.get("/feedback/summary")
def feedback_summary():
    return {
        "averages":      average_scores(),
        "total_queries": len(load_feedback()),
    }

# ── Architecture Summary ─────────────────────────────────
@app.get("/architecture")
def architecture():
    try:
        return generate_architecture_summary()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
