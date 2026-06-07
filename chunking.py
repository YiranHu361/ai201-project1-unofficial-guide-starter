"""Milestone 3 — chunking.

Implements the paragraph-aware strategy from planning.md:

  - Split each document on blank lines into paragraphs, since each paragraph in
    this corpus is one venue's review, i.e. one complete thought.
  - Merge any fragment shorter than MIN_CHARS into its neighbor, so tiny header
    or label lines (a bare "Crossroads") never become standalone chunks.
  - Split any paragraph longer than MAX_CHARS into ~TARGET_CHARS pieces with one
    unit of overlap. For list-style blocks (the Telegraph directory) the unit is
    a line; for long prose it is a sentence.

No overlap is used between separate paragraphs, because each is already
self-contained.
"""

from __future__ import annotations

import re

MIN_CHARS = 200      # below this, a piece is a fragment and gets merged forward
TARGET_CHARS = 600   # aim for chunks around this size
MAX_CHARS = 900      # above this, a paragraph is too big and gets split


def _split_oversized(paragraph: str) -> list[str]:
    """Split a paragraph longer than MAX_CHARS into ~TARGET_CHARS chunks.

    We break the paragraph into units: each line becomes a unit (this keeps the
    Telegraph directory's one-restaurant-per-line entries intact), but any line
    that is itself long prose is further broken into sentences. We then greedily
    pack units up to TARGET_CHARS, carrying one unit of overlap into the next
    chunk so a thought spanning the split stays retrievable from both sides. A
    chunk is only emitted once it has reached MIN_CHARS, so a short heading line
    never gets flushed on its own.
    """
    units: list[str] = []
    for line in paragraph.split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) > TARGET_CHARS:
            sentences = re.findall(r"[^.!?]+[.!?]*", line)
            units.extend(s.strip() for s in sentences if s.strip())
        else:
            units.append(line)

    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for unit in units:
        if current and length + len(unit) > TARGET_CHARS and length >= MIN_CHARS:
            chunks.append("\n".join(current))
            current = [current[-1], unit]            # one unit of overlap
            length = len(current[0]) + len(unit)
        else:
            current.append(unit)
            length += len(unit)
    if current:
        chunks.append("\n".join(current))
    return chunks


def chunk_text(text: str) -> list[str]:
    """Turn one document's cleaned body into a list of chunk strings."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # First expand any oversized paragraph into smaller pieces.
    expanded: list[str] = []
    for p in paragraphs:
        if len(p) > MAX_CHARS:
            expanded.extend(_split_oversized(p))
        else:
            expanded.append(p)

    # Then greedily merge fragments forward until each chunk reaches MIN_CHARS.
    merged: list[str] = []
    buffer = ""
    for piece in expanded:
        buffer = piece if not buffer else buffer + "\n" + piece
        if len(buffer) >= MIN_CHARS:
            merged.append(buffer)
            buffer = ""
    if buffer:  # leftover short tail: attach to the previous chunk
        if merged:
            merged[-1] = merged[-1] + "\n" + buffer
        else:
            merged.append(buffer)
    return merged


def build_chunks(documents: list[dict]) -> list[dict]:
    """Chunk every document and attach source metadata to each chunk.

    Returns a flat list of dicts: {id, text, source_name, url, filename,
    chunk_index}. chunk_index is the position of the chunk within its document,
    which we store so retrieval results can point back to a precise location.
    """
    all_chunks: list[dict] = []
    for doc in documents:
        for i, chunk in enumerate(chunk_text(doc["text"])):
            all_chunks.append(
                {
                    "id": f"{doc['filename']}::chunk_{i}",
                    "text": chunk,
                    "source_name": doc["source_name"],
                    "url": doc["url"],
                    "filename": doc["filename"],
                    "chunk_index": i,
                }
            )
    return all_chunks


if __name__ == "__main__":
    from ingest import load_documents

    docs = load_documents()
    chunks = build_chunks(docs)

    lengths = [len(c["text"]) for c in chunks]
    print(f"Documents: {len(docs)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Chunk size chars: min {min(lengths)}, max {max(lengths)}, "
          f"avg {sum(lengths) // len(lengths)}")
    print(f"Chunks under {MIN_CHARS} chars: {sum(1 for n in lengths if n < MIN_CHARS)}")
    print(f"Chunks over {MAX_CHARS} chars: {sum(1 for n in lengths if n > MAX_CHARS)}")

    print("\n----- 5 sample chunks (first from five different documents) -----")
    seen_files = set()
    shown = 0
    for c in chunks:
        if c["filename"] in seen_files:
            continue
        seen_files.add(c["filename"])
        shown += 1
        print(f"\n[{shown}] source: {c['source_name']}  ({c['id']})  {len(c['text'])} chars")
        print(c["text"])
        if shown == 5:
            break
