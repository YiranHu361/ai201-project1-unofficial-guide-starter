# Project 1 Planning: The Unofficial Guide

I wrote this spec before writing any pipeline code. If my chunking or retrieval approach changes
during implementation, I will come back and update those sections.

## Domain

My domain is UC Berkeley campus dining. This is the real, student-generated take on eating at Cal:
the four dining halls (Crossroads, Foothill, Cafe 3, and Clark Kerr), the on-campus cafes and
eateries, the nearby and late-night food around Telegraph and Durant, and how the meal plan and flex
dollar system actually works once you are living it.

This knowledge is valuable and hard to find through official channels because the UC Berkeley dining
website only lists menus, hours, and prices. It never tells you the things that actually shape a
student's day: which hall has the best food, where the lines get brutal, whether the fifteen to
twenty minute walk to Clark Kerr is worth it, which cafe actually has open outlets for a late night
study session, or where to get cheap food at one in the morning. Those judgments only live in student
blogs, campus life guides, and reviews, which is the unofficial layer this system makes searchable. A
new student can ask one plain question and get a grounded, cited answer instead of reading ten
different blog posts to piece it together.

## Documents

I collected twelve sources. The full list with links lives in documents/SOURCES.md, so here I will
just describe them. They deliberately overlap on the same venues, which lets the system answer what
students consistently say rather than relying on one person's opinion. They also mix subjective blogs
with one official factual source (the meal plan FAQ), so I can test grounding both on opinion and on
fact.

Four of them review and rank the dining halls from different angles: a Daily Californian scoring
piece, a Visitor Services student ranking, a Her Campus ranking, and a Daily Cal guide to on-campus
eateries you can swipe into. Five cover cafes and study spots, both on and off campus: a Daily Cal
coffee shop power ranking, a Spoon University list of nine study cafes, a Her Campus top three for
midterm cramming, a Spoon University top five on-campus coffee spots, and a Berkeley Life Northside
guide. Two cover late-night and nearby food: a Berkeley Life late-night guide and the Telegraph
business district restaurant directory. The last one is the official UC Berkeley Dining meal plan
FAQ, which I included on purpose as a factual contrast to all the opinion.

Every document is a plain text file. I extracted the text from each public web page, cleaned out the
navigation, ads, and footers, and saved it with a short header noting the source and URL.

## Chunking Strategy

My chunk size targets roughly six hundred characters, with a hard cap around nine hundred and a
minimum merge threshold around two hundred. I use overlap only when I have to split an oversized
paragraph, and in that case it is about one sentence. Between separate paragraphs I use no overlap at
all, because each paragraph is already a self-contained review.

I made these choices after actually inspecting the corpus rather than guessing. These documents are
not flowing prose. They are structured as one paragraph per venue, where a single dining hall, cafe,
or restaurant is reviewed as one complete thought. In the Daily Cal dining ranking, for example, the
paragraphs run from about two hundred to about seven hundred characters, and each one covers exactly
one hall. So the natural unit to retrieve is the paragraph, not a fixed window of characters. If I
split every five hundred characters instead, I would cut a review like "Crossroads is a solid
choice... but the brutalist decor is depressing" right down the middle, and then neither half could
answer a question about the downsides of Crossroads.

So my strategy is paragraph-aware with a couple of guardrails. First I split each document on blank
lines into paragraphs, after stripping off the source header. Then I merge any chunk shorter than
about two hundred characters into the next one, which absorbs tiny fragments like a bare "Crossroads"
label line so they do not become meaningless one-line chunks. Finally I split any paragraph longer
than about nine hundred characters on sentence boundaries with a sentence of overlap. That last rule
matters for the Telegraph directory, where sixty restaurants sit in one big block, so it gets broken
into chunks of roughly six to eight restaurants instead of one enormous chunk. I expect this to
produce somewhere around eighty to a hundred and ten chunks across the twelve documents, which sits
comfortably inside the fifty to two thousand range, and each chunk should read as a standalone,
answerable thought.

## Retrieval Approach

I am using the all-MiniLM-L6-v2 model from sentence-transformers for embeddings. It runs locally with
no API key, produces 384-dimensional vectors, and has a 384-token context window, which is plenty for
my short paragraph chunks. I will retrieve the top four chunks per query. Several of my questions,
like which dining hall is best, are answered better when a few independent reviews agree, so I want
more than one chunk, but not so many that the Telegraph restaurant lists flood the context. I will
start at four and tune it after I see real distance scores in Milestone 4.

If I were deploying this for real users and cost were not a constraint, I would weigh a few tradeoffs
in picking a different model. A larger embedding model, like bge-large or one of the OpenAI embedding
models, would likely capture the nuance of opinion phrasing better, where "worth the trek" and "too
far to bother" mean opposite things despite sharing words. Context length is not a concern for me
since my chunks are short, but it would matter a lot for long-form guides. Multilingual support is
low priority for this English corpus, though it would matter if I added international student forums.
Latency and the local-versus-hosted question matter most here: the local MiniLM model has zero
per-query cost and no rate limits, which is exactly right for a free student tool, so I would only
move to a hosted model if the accuracy gain clearly justified the cost and the added dependency.

## Evaluation Plan

I chose five questions that span the corpus and that are specific enough to check against the
documents. I deliberately included a synthesis question that requires combining sources, and a purely
factual one, so I can see how grounding behaves in both cases.

The first question is which dining hall students rank as having the best food. The expected answer is
Clark Kerr, which is repeatedly called the highest quality, though reviewers note it is far from
campus. The second is why Clark Kerr is considered far or inconvenient, and the expected answer is
that it is a fifteen to twenty minute walk from the south side of campus and only serves breakfast
and dinner. The third is where you can study late at night near campus with coffee, and the expected
answer covers Caffe Strada, which is open until midnight with outdoor heaters, the Main Stacks open
until two in the morning, and other late cafes like Cafe Milano and Victory Point. The fourth is
whether flex dollars roll over between semesters, and the expected answer is that they do roll from
fall to spring on on-campus plans, but they do not roll over to summer or the next academic year and
unused funds are forfeited. The fifth is a cheap late-night food option near Telegraph, and the
expected answer covers spots like Top Dog, King Pin Donuts, the late-hours pizza places, La Burrita,
and the Durant food court.

## Anticipated Challenges

The first challenge is that my sources genuinely disagree, so there is no single ground truth. The
Daily Cal scoring piece ranks Crossroads first while the Visitor Services student ranks Clark Kerr
first, and both are reasonable given their criteria. Retrieval may surface contradictory chunks, and
the model needs to summarize the consensus or the disagreement rather than confidently pick one
winner. This is also why my first evaluation question expects Clark Kerr specifically for food
quality rather than naming a single objective best hall.

The second challenge is that the Telegraph directory is thin, list-style text. Each restaurant is a
one-line entry with a name, a cuisine, and an address, so it carries very little semantic signal.
Once those lines are grouped into a chunk, the chunk mixes several unrelated cuisines, so a query like
where can I get ramen might retrieve a chunk that merely happens to contain ramen among ten other
places, with a weak similarity score. I expect this to be a good failure case to document in the
README.

The third challenge is keeping opinion and fact separated when grounding. The official FAQ states
hard facts about flex dollar rules, while everything else is subjective. The system should not blend a
confident factual tone into an opinion answer, and it needs to cite which document an answer came
from so a user can tell a verified fact from a general vibe.

## Architecture

The pipeline has five stages, and the query interface sits on top of the last two. In order, the flow
is:

documents (.txt) -> ingestion -> chunking -> embedding + vector store -> retrieval -> generation -> answer with sources

Stage by stage, ingestion loads the twelve text files from the documents folder and strips the source
header, using plain Python file reading. Chunking runs my custom paragraph-aware splitter that merges
tiny fragments and caps oversized paragraphs. Embedding uses all-MiniLM-L6-v2 from
sentence-transformers to turn each chunk into a vector, which then goes into a ChromaDB vector store
along with metadata for the source filename and the chunk position. Retrieval takes a user query,
embeds it the same way, and asks ChromaDB for the top four most similar chunks with their metadata.
Generation passes those chunks to the Groq llama-3.3-70b-versatile model with a grounding prompt, and
the source filenames get attached to the response. On top of all that, a simple Gradio interface (or a
command line tool) takes a question and shows the answer together with the sources it came from.

## AI Tool Plan

For Milestone 3, ingestion and chunking, I will give Claude the Documents and Chunking Strategy
sections of this file along with the architecture description, and ask it to implement the loader and
the chunking function so they match my paragraph-aware rules, meaning merge anything under two hundred
characters, cap anything over nine hundred, and add a sentence of overlap on splits. I will verify by
printing five chunks and confirming each one stands on its own, and by checking that the total chunk
count lands in the fifty to two thousand range. If I see fragments or oversized chunks, I will adjust
the merge and cap thresholds.

For Milestone 4, embedding and retrieval, I will give Claude the Retrieval Approach section and the
architecture description, and ask it to embed the chunks with MiniLM, store them in ChromaDB with the
source and chunk position metadata, and write a retrieval function that returns the chunks, their
sources, and their distances for a given query. I will verify by running a few of my evaluation
questions and checking that the distance scores are low and the chunks are on topic. If the Telegraph
list chunks dominate with weak scores, I will revisit my chunk size.

For Milestone 5, generation and interface, I will give Claude my grounding requirement and ask it to
write a prompt template that answers only from the retrieved chunks and otherwise says it does not
have enough information, attaches the source filenames programmatically rather than trusting the model
to add them, and builds a Gradio interface. I will verify with an in-scope question that should cite a
source, the synthesis question about the best dining hall, and an out-of-scope question that the
system should refuse to answer.
