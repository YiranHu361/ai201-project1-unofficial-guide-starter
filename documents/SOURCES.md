# Document Sources — UC Berkeley Campus Dining

## Domain summary (2–3 sentences)

This Unofficial Guide covers **UC Berkeley campus dining** — the real, student-generated take on
the four dining halls (Crossroads, Foothill, Café 3, Clark Kerr), on-campus cafés and eateries,
nearby/late-night eats around Telegraph, and how the meal-plan/flex-dollar system actually works.
This knowledge is valuable because official dining webpages list menus and hours but never tell you
which hall has the best food, where the lines are brutal, which café actually has open outlets for
studying, or whether the trek to Clark Kerr is worth it — the things students only learn from each
other. A new student can ask a plain question ("Which dining hall is best?", "Where can I study with
coffee late at night?") and get a grounded, cited answer drawn from these collected reviews.

## Sources (12 collected)

| # | File | Source | Type | URL |
|---|------|--------|------|-----|
| 1 | 01_dailycal_dining_halls_power_rankings.txt | The Daily Californian (The Clog) | Student newspaper opinion ranking | https://www.dailycal.org/archives/power-rankings-uc-berkeley-dining-halls/article_d883d836-1b8f-5343-8191-735a6d732bc1.html |
| 2 | 02_visitberkeley_dining_halls_ranked.txt | UC Berkeley Visitor Services blog | Student-written ranking | https://visit.berkeley.edu/news/crossroads-cal's-dining-halls-ranked |
| 3 | 03_hercampus_dining_halls_ranked.txt | Her Campus UC Berkeley | Student lifestyle ranking | https://www.hercampus.com/school/uc-berkeley/uc-berkeley-dining-halls-ranked/ |
| 4 | 04_dailycal_coffee_shop_study_rankings.txt | The Daily Californian (Food Blog) | Student cafe/study ranking | https://www.dailycal.org/blogs/power-ranking-every-coffee-shop-ive-tried-to-study-at/article_a52694d2-bedc-11ee-bac6-ebe56c64bdec.html |
| 5 | 05_spoonuniversity_9_cafes_for_studying.txt | Spoon University UC Berkeley | Student cafe guide | https://spoonuniversity.com/school/uc-berkeley/9-berkeley-cafes-for-studying/ |
| 6 | 06_lifeberkeley_late_night_in_berkeley.txt | Berkeley Life | Campus life guide (late-night) | https://life.berkeley.edu/late-night-in-berkeley/ |
| 7 | 07_berkeley_dining_meal_plan_faq.txt | UC Berkeley Dining (official) | Official meal-plan FAQ (factual contrast) | https://dining.berkeley.edu/meal-plans/2025-2026/faq/ |
| 8 | 08_dailycal_swipe_on_campus_dining_locations.txt | The Daily Californian (Food Blog) | Student on-campus eatery guide | https://www.dailycal.org/blogs/food-blog/swipe-into-these-on-campus-dining-locations/article_ebd0243b-6819-4d53-bdc1-4d00ca9daeb5.html |
| 9 | 09_hercampus_midterms_macchiatos_top3_cafes.txt | Her Campus UC Berkeley | Student cafe/study ranking | https://www.hercampus.com/school/uc-berkeley/midterms-macchiatos-top-3-cafes-on-campus-for-midterm-cramming/ |
| 10 | 10_spoonuniversity_top5_coffee_on_campus.txt | Spoon University UC Berkeley | Student on-campus coffee guide | https://spoonuniversity.com/place/berkeley-students-top-5-places-coffee-campus |
| 11 | 11_telegraph_district_dining_guide.txt | Telegraph Business Improvement District | Nearby-restaurant directory | https://www.telegraphberkeley.org/dine/ |
| 12 | 12_lifeberkeley_northside_study_spots.txt | Berkeley Life | Campus life guide (Northside cafes) | https://life.berkeley.edu/northside-study-spots/ |

## Coverage / subtopics

- **Dining hall reviews & rankings:** docs 1, 2, 3, 8 (multiple independent opinions on the same 4 halls — useful for "what do students *consistently* say")
- **Cafés & study spots (on- and off-campus):** docs 4, 5, 9, 10, 12
- **Late-night & nearby eats:** docs 6, 11
- **Meal-plan / flex-dollar facts:** doc 7 (official, included to test grounding & contrast with opinion)

## 5 specific questions this corpus can answer (for eval plan)

1. Which dining hall is considered the best, and why?
2. Why do students say Clark Kerr is worth (or not worth) the trip?
3. Where can you study late at night near campus with good coffee?
4. Do flex dollars roll over between semesters?
5. What are some cheap late-night food options near Telegraph?

## Collection notes

- Text extracted via web fetch from each public page, then cleaned (nav/ads/footers removed) and
  saved as plain `.txt` with a source header.
- No content was fabricated — all opinions/quotes are from the real source pages.
- The assignment-spec PDF was moved out of `documents/` into `project_spec/` so it is **not**
  ingested as domain content.
