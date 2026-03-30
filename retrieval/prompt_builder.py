# retrieval/prompt_builder.py

def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Builds a Mistral prompt that grounds the answer in retrieved code chunks.
    Each chunk is labelled with its file path and line range.
    """
    context_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        header = (
            f"[Chunk {i}] "
            f"File: {chunk['file_path']} | "
            f"{chunk['chunk_type'].capitalize()}: {chunk['name']} | "
            f"Lines {chunk['start_line']}–{chunk['end_line']}"
        )
        context_blocks.append(f"{header}\n```python\n{chunk['content']}\n```")

    context = "\n\n".join(context_blocks)

    prompt = f"""You are an expert code assistant. You have been given relevant code chunks from a codebase.
Answer the user's question using ONLY the provided code chunks.
Always cite the file path and line numbers in your answer (e.g. "in auth/middleware.py lines 42–78").
If the answer cannot be found in the chunks, say so clearly — do not hallucinate.

---

{context}

---

Question: {question}

Answer:"""

    return prompt