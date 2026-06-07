"""Milestone 5 — grounded generation.

Takes a user question, retrieves the most relevant chunks, and asks Groq's
llama-3.3-70b-versatile to answer using only those chunks. Grounding is enforced
in two ways: a relevance gate drops chunks that are too far from the question (so
an out-of-scope question ends up with no context and gets a refusal without even
calling the model), and a system prompt that instructs the model to answer only
from the provided context and to say it doesn't have enough information otherwise.

Source attribution is added programmatically from the metadata of the chunks that
were actually used, not left to the model to invent.

Needs a Groq API key in .env as GROQ_API_KEY (free at https://console.groq.com).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve, TOP_K

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"

# Chunks farther than this cosine distance are treated as not relevant. In
# testing, in-scope questions retrieve top chunks around 0.27-0.40 while
# off-topic questions sit at 0.52+, so this cleanly separates them.
RELEVANCE_THRESHOLD = 0.48

REFUSAL = "I don't have enough information on that based on the documents I have."

SYSTEM_PROMPT = (
    "You are The Unofficial Guide to UC Berkeley campus dining. Answer the user's "
    "question using ONLY the information in the provided documents below. Do not use "
    "any outside or general knowledge. If the documents do not contain enough "
    "information to answer, reply exactly: "
    f'"{REFUSAL}" '
    "Keep your answer concise and specific, and base every claim on the documents. "
    "When sources disagree, say so rather than picking one as definitive."
)


def _client() -> Groq:
    key = os.environ.get("GROQ_API_KEY")
    if not key or key == "your_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your free "
            "Groq API key from https://console.groq.com"
        )
    return Groq(api_key=key)


def _format_context(hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(f"[Document {i}] (source: {h['filename']})\n{h['text']}")
    return "\n\n".join(blocks)


def ask(question: str, k: int = TOP_K) -> dict:
    """Answer a question from the corpus.

    Returns {answer, sources}, where sources is a de-duplicated list of the
    documents the answer was actually drawn from (empty on a refusal).
    """
    hits = retrieve(question, k=k)
    relevant = [h for h in hits if h["distance"] <= RELEVANCE_THRESHOLD]

    # No sufficiently relevant context -> refuse without calling the model.
    if not relevant:
        return {"answer": REFUSAL, "sources": []}

    context = _format_context(relevant)
    user_prompt = (
        f"Documents:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the documents above."
    )

    completion = _client().chat.completions.create(
        model=LLM_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    answer = completion.choices[0].message.content.strip()

    # Programmatic source attribution: unique source/url from the chunks used.
    sources = []
    seen = set()
    for h in relevant:
        key = h["filename"]
        if key not in seen:
            seen.add(key)
            label = h["source_name"]
            sources.append(f"{label} ({h['url']})" if h["url"] else label)

    # If the model refused anyway, don't attach sources.
    if answer.strip().lower().startswith(REFUSAL[:30].lower()):
        sources = []

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    for q in [
        "Which dining hall has the best food?",
        "Do flex dollars roll over between semesters?",
        "What is the best gym on campus?",  # out of scope -> should refuse
    ]:
        print("=" * 80)
        print("Q:", q)
        result = ask(q)
        print("\nA:", result["answer"])
        print("\nSources:")
        for s in result["sources"]:
            print("  -", s)
        print()
