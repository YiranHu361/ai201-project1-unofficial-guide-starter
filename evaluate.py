"""Milestone 6 — evaluation harness.

Runs the five evaluation questions (plus an out-of-scope probe and a couple of
failure-hunting probes) through the full pipeline and prints, for each, the
retrieved chunks with distances and the grounded answer with sources. The output
is what populates the Evaluation Report and Failure Case sections of the README.

Run with:  python evaluate.py
"""

from __future__ import annotations

from retrieve import retrieve, TOP_K
from generate import ask

EVAL_QUESTIONS = [
    "Which dining hall has the best food?",
    "Why is Clark Kerr considered far or inconvenient?",
    "Where can I study late at night near campus with coffee?",
    "Do flex dollars roll over between semesters?",
    "What is a cheap late-night food option near Telegraph?",
]

PROBES = [
    "What is the best gym on campus?",          # out of scope -> should refuse
    "Where can I get ramen near campus?",        # stresses the Telegraph list chunks
]


def show(question: str) -> None:
    print("=" * 90)
    print("QUESTION:", question)
    print("\nRetrieved chunks (top %d):" % TOP_K)
    for i, h in enumerate(retrieve(question), 1):
        preview = h["text"].replace("\n", " ")
        if len(preview) > 160:
            preview = preview[:160] + "..."
        print(f"  [{i}] dist {h['distance']:.3f}  {h['filename']}")
        print(f"      {preview}")
    result = ask(question)
    print("\nANSWER:", result["answer"])
    print("SOURCES:", "; ".join(result["sources"]) if result["sources"] else "(none — refused)")
    print()


if __name__ == "__main__":
    print("\n########## EVALUATION QUESTIONS ##########\n")
    for q in EVAL_QUESTIONS:
        show(q)
    print("\n########## PROBES ##########\n")
    for q in PROBES:
        show(q)
