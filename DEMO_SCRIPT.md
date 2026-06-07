# Demo Video Script (3-5 minutes)

A simple walkthrough to record. Launch the app first with `python app.py` and open
http://localhost:7860.

## 0:00 - 0:30  Intro
Say what this is: The Unofficial Guide, a retrieval-augmented system that answers questions about UC
Berkeley campus dining using only collected student reviews and guides, with sources shown. Mention the
stack briefly: local all-MiniLM-L6-v2 embeddings, ChromaDB, and Groq llama-3.3-70b for generation, over
12 documents and 84 chunks.

## 0:30 - 1:30  Query one that works well (show source citation)
Ask: do flex dollars roll over between semesters.
Point out the answer (on-campus plans roll fall to spring; off-campus only if you buy a spring plan) and
that the Retrieved from box cites the official Meal Plans FAQ. Note that this is the strongest retrieval
in the system, the top chunk matched at distance 0.153, an almost exact match.

## 1:30 - 2:30  Two more queries with citations
Ask: why is Clark Kerr considered far or inconvenient. Show it cites three independent sources and gives
the 15-20 minute walk detail. This is a good example of the system combining several reviews.
Then ask: where can I study late at night near campus with coffee. Show it names Strada open until
midnight and cites the coffee-shop sources. Mention honestly that this answer is correct but narrower
than the corpus could support, since it did not surface Main Stacks.

## 2:30 - 3:30  A query that fails (narrate why)
Ask: where can I get ramen near campus. It will refuse, even though the Telegraph directory lists BanSho
Ramen and Bear's Ramen House. Explain the cause: the directory is a flat list, my chunker groups six to
eight restaurants per chunk, so the word ramen gets averaged into a vector dominated by unrelated
cuisines and never ranks high enough to retrieve. This is a chunking and embedding failure, and the fix
is one-restaurant-per-chunk or hybrid keyword search.
Optionally also ask: what is the best gym on campus, to show the out-of-scope refusal working as intended.

## 3:30 - 4:30  Walk through the evaluation report
Switch to the README Evaluation Report section. Summarize: two questions fully accurate, three partially
accurate (correct but narrower or hedged), and the ramen failure case explained with a specific cause
tied to the pipeline. Emphasize the honesty point: the system declines rather than inventing answers.

## 4:30 - 5:00  Close
Mention the spec reflection in one line: the biggest divergence from the plan was moving from a distance
threshold to prompt-based grounding and from four to six retrieved chunks, both driven by what the
evaluation questions exposed.
