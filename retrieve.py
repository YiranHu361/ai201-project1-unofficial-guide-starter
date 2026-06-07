"""Milestone 4 — retrieval.

Embeds a query with the same model used to build the index and asks ChromaDB for
the most similar chunks, returning each chunk's text, source, and distance score.

Run this to test retrieval on a few evaluation questions:  python retrieve.py
"""

from __future__ import annotations

from embed import get_model, get_collection

TOP_K = 4


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """Return the top-k most similar chunks to query.

    Each result is a dict with the chunk text, its source name, URL, filename,
    and the cosine distance (lower means more similar).
    """
    model = get_model()
    collection = get_collection()
    query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()

    result = collection.query(query_embeddings=[query_embedding], n_results=k)

    hits = []
    for doc, meta, dist in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append(
            {
                "text": doc,
                "source_name": meta["source_name"],
                "filename": meta["filename"],
                "url": meta["url"],
                "distance": dist,
            }
        )
    return hits


if __name__ == "__main__":
    # Three of the evaluation-plan questions, used to sanity-check retrieval.
    test_queries = [
        "Which dining hall has the best food?",
        "Where can I study late at night near campus with coffee?",
        "Do flex dollars roll over between semesters?",
    ]
    for q in test_queries:
        print("=" * 80)
        print("QUERY:", q)
        for i, hit in enumerate(retrieve(q), 1):
            preview = hit["text"].replace("\n", " ")
            if len(preview) > 240:
                preview = preview[:240] + "..."
            print(f"\n  [{i}] distance {hit['distance']:.3f}  source: {hit['filename']}")
            print(f"      {preview}")
        print()
