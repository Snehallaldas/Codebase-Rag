# critic/critic_agent.py
import json
from retrieval.generator import generate_answer   # reuse same Mistral wrapper

CRITIC_PROMPT_TEMPLATE = """You are a strict code-answer evaluator.
You will be given a user question, the code chunks that were retrieved, and an AI-generated answer.
Score the answer on three dimensions. Respond ONLY in valid JSON — no extra text.

Question: {question}

Retrieved Code Chunks:
{context}

Generated Answer:
{answer}

Evaluate and respond with this exact JSON structure:
{{
  "faithfulness": <0-10>,       // Does the answer stick to what the code actually shows? Penalise hallucination.
  "relevance": <0-10>,          // Does the answer address the question asked?
  "completeness": <0-10>,       // Does the answer cover all relevant parts found in the chunks?
  "overall": <0-10>,            // Weighted summary score
  "reasoning": "<one sentence explaining the scores>"
}}"""


def score_answer(question: str, chunks: list[dict], answer: str) -> dict:
    """
    Sends question + chunks + answer to Mistral critic.
    Returns a dict with faithfulness, relevance, completeness, overall, reasoning.
    """
    # build readable context for the critic
    context_lines = []
    for i, chunk in enumerate(chunks, 1):
        context_lines.append(
            f"[{i}] {chunk['file_path']} — {chunk['name']} "
            f"(lines {chunk['start_line']}–{chunk['end_line']})\n{chunk['content'][:300]}"
        )
    context = "\n\n".join(context_lines)

    prompt = CRITIC_PROMPT_TEMPLATE.format(
        question=question,
        context=context,
        answer=answer,
    )

    raw = generate_answer(prompt, model="mistral-small-latest")

    try:
        # strip accidental markdown fences if Mistral wraps in ```json
        clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
        scores = json.loads(clean)
    except json.JSONDecodeError:
        # fallback if Mistral misbehaves
        scores = {
            "faithfulness": -1,
            "relevance": -1,
            "completeness": -1,
            "overall": -1,
            "reasoning": "Critic failed to parse JSON response.",
            "raw_critic_output": raw,
        }

    return scores