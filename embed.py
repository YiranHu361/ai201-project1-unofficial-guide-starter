"""Milestone 4 — embedding and vector store.

Loads the chunks from the ingestion/chunking pipeline, embeds them with
all-MiniLM-L6-v2 (local, no API key), and stores them in a persistent ChromaDB
collection together with their source metadata so retrieval results can be
attributed back to a specific document and position.

Run this once to build the index:  python embed.py
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import load_documents
from chunking import build_chunks

EMBED_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "berkeley_dining"

# Cache the model so embed.py and retrieve.py don't each reload it.
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def get_collection(reset: bool = False):
    """Return the Chroma collection, optionally recreating it from scratch.

    We use cosine distance so the scores are easy to read: identical meaning is
    near 0, unrelated text approaches 1.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_index() -> int:
    """Embed all chunks and (re)load them into ChromaDB. Returns chunk count."""
    docs = load_documents()
    chunks = build_chunks(docs)
    model = get_model()

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    collection = get_collection(reset=True)
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=[
            {
                "source_name": c["source_name"],
                "url": c["url"],
                "filename": c["filename"],
                "chunk_index": c["chunk_index"],
            }
            for c in chunks
        ],
    )
    return len(chunks)


if __name__ == "__main__":
    n = build_index()
    print(f"\nEmbedded and stored {n} chunks in ChromaDB collection "
          f"'{COLLECTION_NAME}' at {CHROMA_PATH}")
    print(f"Embedding model: {EMBED_MODEL}")
