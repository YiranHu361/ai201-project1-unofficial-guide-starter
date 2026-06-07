"""Milestone 3 — document ingestion.

Loads the collected .txt documents from documents/, strips the Source/URL header
block we prepended during collection, and does a light cleaning pass (unescape any
stray HTML entities, drop any HTML tags, normalize whitespace).

Each document is returned as a dict with its cleaned body text plus the source
filename and URL, which we carry through chunking and into the vector store so
every retrieved chunk can be attributed back to where it came from.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"

# The collected files start with a small header block, then a line that is just
# "---", then the actual article body. We split on that marker.
HEADER_SEPARATOR = "---"


def _parse_header(raw: str) -> tuple[dict, str]:
    """Split a raw file into (header_fields, body_text).

    header_fields pulls out Source: and URL: lines if present. If there is no
    "---" separator, we treat the whole file as body and return empty fields.
    """
    if HEADER_SEPARATOR in raw:
        header_part, body = raw.split(HEADER_SEPARATOR, 1)
    else:
        header_part, body = "", raw

    fields = {}
    for line in header_part.splitlines():
        if line.lower().startswith("source:"):
            fields["source_name"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("url:"):
            fields["url"] = line.split(":", 1)[1].strip()
    return fields, body


def clean_text(text: str) -> str:
    """Light cleaning pass.

    Our documents were already cleaned when collected, but we still run this so
    the pipeline is honest about cleaning: unescape HTML entities like &amp;,
    remove any HTML tags, collapse runs of spaces/tabs, and trim blank lines down
    to single blank-line paragraph separators.
    """
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)          # strip any HTML tags
    text = re.sub(r"[ \t]+", " ", text)            # collapse spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)        # at most one blank line between paragraphs
    return text.strip()


def load_documents(docs_dir: Path = DOCS_DIR) -> list[dict]:
    """Load and clean every .txt document in docs_dir.

    Returns a list of dicts: {filename, source_name, url, text}. SOURCES.md and
    any non-.txt files are skipped.
    """
    documents = []
    for path in sorted(docs_dir.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        fields, body = _parse_header(raw)
        documents.append(
            {
                "filename": path.name,
                "source_name": fields.get("source_name", path.stem),
                "url": fields.get("url", ""),
                "text": clean_text(body),
            }
        )
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {DOCS_DIR}\n")
    for d in docs:
        print(f"  {d['filename']:<50} {len(d['text']):>5} chars  ({d['source_name']})")
    # Print one cleaned document in full so we can eyeball that cleaning worked
    # and no nav/HTML leftovers remain (per the Milestone 3 instructions).
    print("\n----- full text of first document after cleaning -----\n")
    print(docs[0]["text"])
