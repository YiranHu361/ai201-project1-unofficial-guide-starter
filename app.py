"""Milestone 5 — query interface.

A small Gradio web app over the RAG pipeline. Type a question about UC Berkeley
campus dining and get a grounded answer plus the documents it came from.

Run with:  python app.py   then open http://localhost:7860
"""

from __future__ import annotations

import gradio as gr

from generate import ask

EXAMPLES = [
    "Which dining hall has the best food?",
    "Why is Clark Kerr considered far from campus?",
    "Where can I study late at night near campus with coffee?",
    "Do flex dollars roll over between semesters?",
    "What's a cheap late-night food option near Telegraph?",
]


def handle_query(question: str):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = result["sources"]
    sources_text = "\n".join(f"• {s}" for s in sources) if sources else "(no sources — outside the guide's documents)"
    return result["answer"], sources_text


with gr.Blocks(title="The Unofficial Guide — UC Berkeley Dining") as demo:
    gr.Markdown(
        "# The Unofficial Guide: UC Berkeley Campus Dining\n"
        "Ask about the dining halls, cafes, late-night eats, or the meal plan. "
        "Answers come only from collected student reviews and guides, with sources shown."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Which dining hall has the best food?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    gr.Examples(examples=EXAMPLES, inputs=inp)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
