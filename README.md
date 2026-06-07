# The Unofficial Guide: UC Berkeley Campus Dining

This is a retrieval-augmented question answering system over student-generated knowledge about eating
at UC Berkeley. You ask a plain-language question like which dining hall has the best food or whether
flex dollars roll over, and it answers using only a collection of real student reviews and campus
guides, citing which documents the answer came from. It runs entirely on a free stack: local
all-MiniLM-L6-v2 embeddings, a local ChromaDB vector store, and Groq's llama-3.3-70b-versatile for
generation.

To run it, create the virtual environment and install requirements, put a free Groq API key in a .env
file as GROQ_API_KEY, build the index once with python embed.py, and then launch the interface with
python app.py and open http://localhost:7860. You can also run python evaluate.py to reproduce the
evaluation below from the command line.

## Domain

My domain is UC Berkeley campus dining: the real, student-generated take on the four dining halls
(Crossroads, Foothill, Cafe 3, and Clark Kerr), the on-campus cafes and eateries, the nearby and
late-night food around Telegraph and Durant, and how the meal plan and flex dollar system actually
works once you are living it.

This knowledge is valuable and hard to find through official channels because the campus dining
website only lists menus, hours, and prices. It never tells you which hall has the best food, where
the lines get brutal, whether the fifteen to twenty minute walk to Clark Kerr is worth it, which cafe
actually has open outlets for a late-night study session, or where to get cheap food at one in the
morning. Those judgments only live in student blogs, campus life guides, and reviews, and this system
makes that unofficial layer searchable so a new student can ask one question and get a grounded, cited
answer instead of reading ten blog posts.

## Document Sources

I collected twelve documents. They deliberately overlap on the same venues so the system can answer
what students consistently say rather than trusting one opinion, and they mix subjective blogs with
one official factual source so grounding can be tested on both opinion and fact. Every document is a
plain text file extracted from a public web page, cleaned of navigation, ads, and footers, and saved
with a short header noting the source and URL. The full source table also lives in documents/SOURCES.md.

The four dining-hall sources are a Daily Californian scoring and ranking piece
(https://www.dailycal.org/archives/power-rankings-uc-berkeley-dining-halls/article_d883d836-1b8f-5343-8191-735a6d732bc1.html),
a UC Berkeley Visitor Services student ranking
(https://visit.berkeley.edu/news/crossroads-cal's-dining-halls-ranked), a Her Campus ranking
(https://www.hercampus.com/school/uc-berkeley/uc-berkeley-dining-halls-ranked/), and a Daily Cal guide
to on-campus eateries you can swipe into
(https://www.dailycal.org/blogs/food-blog/swipe-into-these-on-campus-dining-locations/article_ebd0243b-6819-4d53-bdc1-4d00ca9daeb5.html).

The five cafe and study-spot sources are a Daily Cal coffee shop power ranking
(https://www.dailycal.org/blogs/power-ranking-every-coffee-shop-ive-tried-to-study-at/article_a52694d2-bedc-11ee-bac6-ebe56c64bdec.html),
a Spoon University list of nine study cafes
(https://spoonuniversity.com/school/uc-berkeley/9-berkeley-cafes-for-studying/), a Her Campus top three
for midterm cramming
(https://www.hercampus.com/school/uc-berkeley/midterms-macchiatos-top-3-cafes-on-campus-for-midterm-cramming/),
a Spoon University top five on-campus coffee spots
(https://spoonuniversity.com/place/berkeley-students-top-5-places-coffee-campus), and a Berkeley Life
Northside guide (https://life.berkeley.edu/northside-study-spots/).

The two late-night and nearby food sources are a Berkeley Life late-night guide
(https://life.berkeley.edu/late-night-in-berkeley/) and the Telegraph business district restaurant
directory (https://www.telegraphberkeley.org/dine/). The last source is the official UC Berkeley
Dining meal plan FAQ (https://dining.berkeley.edu/meal-plans/2025-2026/faq/), included on purpose as a
factual contrast to all the opinion.

## Chunking Strategy

My chunker is paragraph-aware rather than fixed-size. It targets chunks of roughly six hundred
characters, with a minimum of about two hundred and a hard cap of about nine hundred. It uses overlap
of about one sentence only when it has to split an oversized paragraph; between separate paragraphs it
uses no overlap, because each paragraph is already a self-contained review.

I chose this after inspecting the corpus rather than guessing. These documents are not flowing prose.
They are structured as one paragraph per venue, where a single dining hall, cafe, or restaurant is
reviewed as one complete thought. In the Daily Cal dining ranking, for example, the paragraphs run
from about two hundred to about seven hundred characters and each covers exactly one hall. So the
natural unit to retrieve is the paragraph. A fixed five-hundred-character split would cut a review
like Crossroads is a solid choice but the brutalist decor is depressing right down the middle, and
then neither half could answer a question about the downsides of Crossroads.

Concretely, the chunker first strips the source header, then splits each document on blank lines into
paragraphs. It merges any fragment shorter than two hundred characters into its neighbor, which
absorbs tiny heading lines like a bare Crossroads so they never become a standalone chunk. It splits
any paragraph longer than nine hundred characters into roughly six-hundred-character pieces with one
unit of overlap; for the Telegraph directory, whose sixty restaurants sit in one block, the unit is a
line, and for long prose the unit is a sentence.

Before this pass I caught and fixed a real bug where the splitter duplicated headings like 2.
Crossroads and produced a 1308-character chunk because it only split on line breaks and not on
sentences. After the fix, the final corpus is 84 chunks across the twelve documents, comfortably inside
the fifty to two thousand range. The smallest chunk is 223 characters and the largest is 890, with an
average of 449, so there are no meaningless fragments and nothing oversized.

## Sample Chunks

The following are five real chunks from the pipeline, each labeled with the source document it came
from. Each reads as a complete, answerable thought on its own.

Chunk from 01_dailycal_dining_halls_power_rankings.txt (The Daily Californian, The Clog):
Clark Kerr Campus. Quality of Food: 9/10. The highest-quality dining hall food at UC Berkeley. We
can't quite figure out why, but all we know is that we're grateful for it. Variety of Food Options:
6/10. Hours Open: 4/10, open an average of 5.4 hours a day. Proximity to Campus: 4/10. We love Clark
Kerr, but it's notoriously far from campus. Total: 23/40.

Chunk from 02_visitberkeley_dining_halls_ranked.txt (UC Berkeley Visitor Services blog):
1. Clark Kerr. Clark Kerr Campus' dining hall obtains the #1 spot for a few reasons. At dinner the
entire dining hall is filled with a beautiful golden glow. Although relatively small, Clark Kerr always
seems to have the best food, from steak to biscuits, the chefs here REALLY know what they're doing. The
downside is the trek it takes to get there, a whopping 15-20 minute walk from the south side of campus.

Chunk from 04_dailycal_coffee_shop_study_rankings.txt (The Daily Californian, Food Blog):
Strada. One of the more iconic Berkeley coffee shops, Strada is my go-to place to study with friends
or have meetings. The outdoor seating options are especially great for fresh air after being crammed
in lecture halls all day. A huge plus is that they also stay open until 12 a.m., so you have time to
grind out that paper or submit that assignment by 11:59 p.m.

Chunk from 07_berkeley_dining_meal_plan_faq.txt (UC Berkeley Dining, official):
What are my options as a UC Berkeley student for meal plans? On-campus residents receive the Blue &
Gold Plan as part of their housing contract, combining meal swipes, flex dollars, and flex+ dollars.
Off-campus undergraduates and graduate students can purchase Standard, Premium, or Platinum plans, or
Advantage, Blue & Gold, and Ultimate plans. Add-on flex+ dollars are available anytime.

Chunk from 12_lifeberkeley_northside_study_spots.txt (Berkeley Life):
On Euclid Avenue. Delah Coffee: This eye-catching cafe features Arabian coffee for less than $5, a
tiled ceiling, comfy velvet chairs, and barstool seating between outlets. The establishment offers
quiet music in the background and delivers excellent study vibes with its dark tones and glittering
silver chandeliers.

## Embedding Model

I used all-MiniLM-L6-v2 from sentence-transformers. It runs locally with no API key and no rate
limits, produces 384-dimensional vectors, and has a context window that comfortably fits my short
paragraph chunks. For a free student tool this is the right default, since it costs nothing per query
and depends on nothing external.

If I were deploying this for real users and cost were not a constraint, I would weigh a few tradeoffs
in choosing a different model. A larger model such as bge-large or one of the OpenAI embedding models
would likely capture the nuance of opinion phrasing better, where worth the trek and too far to bother
mean opposite things despite sharing words, which is exactly the kind of mismatch that hurt me on the
harder questions. Context length is not a concern here because my chunks are short, but it would matter
for long-form guides. Multilingual support is low priority for this English corpus but would matter if
I added international-student forums. Latency and the local-versus-hosted question matter most: local
MiniLM has zero per-query cost, so I would only move to a hosted model if the accuracy gain clearly
justified the cost and the added dependency.

## Retrieval Test Results

Retrieval embeds the query with the same model and asks ChromaDB, using cosine distance, for the top
six chunks. Lower distance means a closer match. Here are three of the evaluation queries with their
top results.

For the query do flex dollars roll over between semesters, the top chunk is at distance 0.153 and is
the exact FAQ entry titled Do my flex dollars roll over, which says on-campus plans roll fall to spring
and off-campus plans only if you buy a spring plan. The next chunks, at 0.458 and 0.467, are other
flex-dollar FAQ entries. This is a strong retrieval: the closest chunk is almost an exact semantic
match for the question, and everything returned is from the right source. It is relevant because the
question and the chunk share the precise concept of flex dollars rolling over, not just shared words.

For the query why is Clark Kerr considered far or inconvenient, the top chunks at 0.531 and 0.562 are
the two Clark Kerr reviews, one noting the 15-20 minute walk from the south side of campus and the
other noting its location at the farthest campus distance. These are relevant because both chunks are
specifically about Clark Kerr's location and inconvenience, which is exactly what the question asks,
even though the distance scores are higher than the flex-dollar example. The higher scores are a sign
that this question is phrased less like its answer than the flex-dollar one is.

For the query where can I study late at night near campus with coffee, the top chunks at 0.352 to 0.405
are all coffee and study-spot reviews, including the Strada review that mentions staying open until
midnight. These are on-topic and from the right sources, although as discussed below the answer ended
up narrower than the corpus could have supported.

## Grounded Generation

Grounding is enforced primarily through the system prompt. The model is told to answer using only the
provided documents, to use no outside or general knowledge, and to reply with a fixed line, I don't
have enough information on that based on the documents I have, whenever the documents do not contain
the answer. It is also told that when sources disagree it should say so rather than pick one as
definitive. Generation runs at a low temperature of 0.2 to keep it close to the retrieved text.

I deliberately do not rely on a distance threshold as the refusal mechanism. I tried that first and it
failed, for a reason worth recording: a legitimate but hard in-scope question, why Clark Kerr is far,
has a top distance of about 0.53, while an out-of-scope question, what is the best gym on campus, has a
top distance of about 0.52. They overlap, so no threshold can separate them. The model, reading the
actual chunk text, can tell that dining reviews do not answer a gym question, which a number cannot. I
keep only a loose distance backstop of 0.70 to trim clearly unrelated chunks from the context so they
do not dilute it.

Source attribution is added programmatically. After generation, the system collects the source names
and URLs from the metadata of the chunks that were actually used and returns them alongside the answer,
so the citation does not depend on the model choosing to add it. If the model returns the refusal line,
no sources are attached.

## Example Responses

Question: why is Clark Kerr considered far or inconvenient.
Answer: According to Document 1, Clark Kerr is a whopping 15-20 minute walk from the south side of
campus, which makes it inconvenient. Document 2 also mentions that its location is at the farthest
campus distance, reducing its convenience ranking. Additionally, Document 3 rates its proximity to
campus as 4/10, stating it's notoriously far from campus.
Sources: UC Berkeley Visitor Services blog, At a Crossroads: Cal's Dining Halls, Ranked; Her Campus UC
Berkeley, UC Berkeley Dining Halls Ranked; The Daily Californian, Power Rankings: UC Berkeley Dining
Halls.

Question: do flex dollars roll over between semesters.
Answer: According to Document 1, for on-campus plans, yes, flex and flex+ dollars will roll over from
the fall semester to the spring semester. However, for off-campus plans, they only roll over if you
purchase a spring plan.
Sources: UC Berkeley Dining, Meal Plans FAQ (2025-2026).

Out-of-scope question: what is the best gym on campus.
Answer: I don't have enough information on that based on the documents I have.
Sources: none. The system correctly declines because the retrieved chunks are dining and cafe reviews,
none of which address gyms, and it does not fall back on general knowledge to invent an answer.

## Query Interface

The interface is a small Gradio web app, launched with python app.py and reached at
http://localhost:7860. It has one input field, a text box labeled Your question, and two output fields,
a text box labeled Answer and a text box labeled Retrieved from that lists the source documents. It
also shows the five evaluation questions as clickable examples, and you can submit either by pressing
the Ask button or by pressing enter in the question box.

A sample interaction looks like this. You type, where can I study late at night near campus with
coffee, and press Ask. The Answer box fills with: According to Document 3, Strada is a coffee shop that
stays open until 12 a.m., making it a suitable option for studying late at night near campus with
coffee. The Retrieved from box fills with the three source documents the answer drew on, the Daily Cal
coffee shop ranking, the Spoon University study cafes list, and the Her Campus midterm cafes piece.

## Evaluation Report

I ran all five evaluation questions through the full system. The honest summary is that two are fully
accurate, three are partially accurate in that they are correct but narrower or more hedged than they
could be, and the separate failure probe below is an outright failure.

Question one, which dining hall has the best food. Expected answer: Clark Kerr, repeatedly called the
highest quality though far from campus. The system answered that Document 6 says Clark Kerr always
seems to have the best food while Document 4 calls its quality merely acceptable, and concluded that
Clark Kerr has the best food. Retrieval was partially relevant, because the most explicit highest
quality reviews ranked fifth and sixth and the top result was a generic dining-halls overview.
Response accuracy: partially accurate. It reaches the right answer but hedges and leans on a lukewarm
source rather than the strongest one.

Question two, why is Clark Kerr considered far or inconvenient. Expected answer: a 15-20 minute walk
from the south side of campus, and it only serves breakfast and dinner. The system answered that it is
a 15-20 minute walk from the south side, at the farthest campus distance, with a 4/10 proximity rating.
Retrieval was relevant. Response accuracy: accurate.

Question three, where can I study late at night near campus with coffee. Expected answer: Caffe Strada
open until midnight, Main Stacks until 2 a.m., and other late cafes. The system named Strada open until
midnight and stopped there. Retrieval returned coffee and study chunks but not the late-night guide
that lists Main Stacks and Cafe Milano. Response accuracy: partially accurate. What it said is correct
but it missed other valid options the corpus contains.

Question four, do flex dollars roll over between semesters. Expected answer: yes fall to spring on
on-campus plans, but not to summer or the next year, and unused funds are forfeited. The system
answered that on-campus plans roll fall to spring and off-campus plans roll only if you buy a spring
plan. Retrieval was an almost exact match at 0.153. Response accuracy: accurate on the core question,
though it did not volunteer the forfeiture detail.

Question five, what is a cheap late-night food option near Telegraph. Expected answer: spots like Top
Dog, King Pin Donuts, the late-hours pizza places, La Burrita, and the Durant food court. The system
named Top Dog, Tacos Sinaloa, and Seniore's Pizza for its late hours, and honestly noted that the
documents do not say which is cheapest. Retrieval was partially relevant. Response accuracy: partially
accurate, correct and honest but not complete.

## Failure Case Analysis

Question that failed: where can I get ramen near campus.

What the system returned: I don't have enough information on that based on the documents I have. It
refused, even though the corpus clearly contains ramen options. The Telegraph directory lists BanSho
Ramen and Bear's Ramen House by name.

Root cause, tied to a specific pipeline stage: this is a chunking and embedding failure, and it is the
exact risk I anticipated in planning. The Telegraph directory is a flat list of sixty one-line
restaurant entries, and my chunker groups roughly six to eight of them per chunk to avoid tiny
fragments. As a result, the chunk that contains BanSho Ramen also contains pizza, burgers, Mediterranean
food, and a dozen addresses. When that chunk is embedded, the word ramen is one token in an averaged
vector dominated by unrelated cuisines, so its semantic signal is washed out. When I query for ramen,
none of the Telegraph chunks rank in the top six; instead the system retrieves dining-hall and cafe
overview chunks at distances of 0.55 and above, and because none of those actually mention ramen, the
grounding prompt correctly refuses. The retrieval never surfaced the chunk that holds the answer.

What I would change to fix it: chunk the directory one restaurant per chunk, or attach each restaurant
name as metadata, so the embedding for a ramen place is about that place and not an average of eight
places. A second fix would be hybrid search that combines semantic similarity with a keyword match, so
an exact term like ramen retrieves the entry that literally contains it even when the embedding signal
is weak. Both are listed as stretch features, and this failure is a concrete motivation for the keyword
approach.

## Spec Reflection

One way the spec helped me during implementation: writing the chunking strategy before any code forced
me to look at the documents first, and that is where I noticed the one-paragraph-per-venue structure.
Because I had already decided on paragraph-aware chunking with explicit merge and cap thresholds, the
implementation had a precise target, and when I inspected the output I could immediately tell that a
duplicated heading and a 1308-character chunk were bugs rather than acceptable behavior. The evaluation
plan also did real work: running those five specific questions is what exposed that four retrieved
chunks were not enough and that my refusal mechanism was wrong, neither of which I would have caught
with vaguer questions.

One way my implementation diverged from the spec, and why: I planned to retrieve four chunks and to
gate refusals with a distance threshold. Both changed. I raised retrieval to six chunks because at four
the answer-bearing chunk for several questions ranked just outside the cutoff, and I replaced the
distance gate with prompt-based grounding because testing showed that a hard in-scope question and an
out-of-scope question can sit at the same distance, so no threshold could separate them. I updated the
planning document's retrieval section to reflect both changes, since the spec asks for that section to
be kept current.

## AI Usage

Instance one. I gave Claude my Chunking Strategy section from planning.md and the structure of my
documents, and asked it to implement the loader and the chunk_text function to match my paragraph-aware
rules, meaning merge fragments under two hundred characters, cap paragraphs over nine hundred, and add
a sentence of overlap on splits. It produced a working paragraph splitter, but when I inspected the
output I found two problems it had introduced: headings like 2. Crossroads were duplicated, and long
single-paragraph reviews were not being split because the splitter only broke on line breaks, producing
a 1308-character chunk. I directed the fix, which was to break each oversized paragraph into units by
splitting lines first and then splitting any long line into sentences, and to only emit a chunk once it
reached the minimum size so a short heading never flushed on its own. After that the corpus came out
clean at 84 chunks.

Instance two. I gave Claude my grounding requirement and asked it to implement generation against Groq
with source attribution and a Gradio interface. Its first version gated refusals with a hard cosine
distance threshold of 0.48, which I had initially suggested based on a couple of easy test queries.
When I ran all five evaluation questions through it, three legitimate questions were refused. I
diagnosed that the threshold was dropping valid chunks, found that in-scope and out-of-scope questions
had overlapping distances, and redirected the design to rely on the system prompt for refusal with the
retrieval raised to six chunks and only a loose distance backstop. That version answered all five
in-scope questions and still refused the out-of-scope ones.
