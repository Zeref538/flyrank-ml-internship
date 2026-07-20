# The Prompt Ladder — John Andrei Martinez

Track: Machine Learning (FlyRank refresh-scoring work). I took a lazy prompt I actually would have typed early on and improved it one layer at a time, comparing the output at every step.

---

## Baseline — the embarrassing one

**Prompt:**
> Explain this data.

**Output (excerpt):**
> Sure! Data is a collection of facts, such as numbers, words, measurements, or observations. To explain your data, I'd need to know more about it. Could you share the dataset or describe its columns? In general, explaining data involves looking at what each column means, checking for missing values, and summarizing trends...

**Why it's bad:** I didn't say what data, what I wanted, or who it's for. It couldn't do anything but ask me to try again.

---

## Version 1 — layer added: real context

**Prompt:**
> I have a CSV of 30,000 web pages. Each row is one page with columns like impressions_90d, ctr, avg_position, days_since_last_update, and trend_direction (up/down/flat). Explain this data.

- **What changed in the prompt:** I pasted in what the dataset actually is and named the columns.
- **What improved in the output:** it stopped asking me questions and started describing my real columns — it explained that avg_position is Google ranking, that ctr is click rate, and guessed the rows were about SEO performance. Actually useful now.
- **What still failed:** it just defined each column one by one. It didn't tell me what I could *do* with the data or what problem it fits.
- **What I'd try next:** tell it the goal, not just the columns.

---

## Version 2 — layer added: a clearer goal

**Prompt:**
> I have a CSV of 30,000 web pages (columns: impressions_90d, ctr, avg_position, days_since_last_update, trend_direction). My goal is to decide which pages to refresh first. Explain what in this data helps me do that.

- **What changed in the prompt:** I added the actual goal — pick which pages to fix first.
- **What improved in the output:** it stopped listing columns and started ranking them by usefulness. It pointed at trend_direction and days_since_last_update as the signals for "decaying page," and suggested combining low ctr with high impressions as an opportunity. It felt like it was helping me think, not defining terms.
- **What still failed:** it suggested using trend_direction as a feature to predict decline — which is circular, because my label comes from trend_direction. It didn't know that.
- **What I'd try next:** give it the audience/level so it talks to me like an ML intern, and maybe it'll catch traps like that.

---

## Version 3 — layer added: a defined audience  (this one didn't really help)

**Prompt:**
> I have a CSV of 30,000 web pages (columns as above). Goal: decide which pages to refresh first. I'm a machine-learning intern. Explain what in this data helps me do that.

- **What changed in the prompt:** I told it I'm an ML intern.
- **What improved in the output:** honestly, not much. It threw in more jargon — "feature engineering," "multicollinearity," "you may want to standardize" — but the actual advice was the same as Version 2. It still didn't catch the circular-label problem.
- **What still failed:** adding "I'm an ML intern" made it *sound* smarter without being more correct. It was longer and harder to read for no real gain. This layer was a miss.
- **What I'd try next:** drop the audience label and instead give it a real constraint — tell it the trap directly and ask it to watch for that kind of thing.

---

## Version 4 — layer added: a constraint

**Prompt:**
> I have a CSV of 30,000 web pages (columns as above). Goal: decide which pages to refresh first. Constraint: my label is "declining" which comes from trend_direction, so trend_direction and trend_pct can NOT be used as features — that would leak the answer. Given that, which columns are safe, useful features?

- **What changed in the prompt:** I added the leakage rule as a hard constraint.
- **What improved in the output:** big jump. It dropped trend_direction and trend_pct from its suggestions on its own, and gave me a clean list of safe features — impressions, ctr, avg_position, freshness, word count. It even flagged that avg_position = 0 might mean "no data" and I should check. That's the first time it caught something I'd have to catch myself.
- **What still failed:** the answer was a wall of text. If I wanted to reuse it or hand it to a teammate, I'd have to reformat it.
- **What I'd try next:** ask for a specific output format so it's usable, not just readable.

---

## Version 5 — layer added: a specified output format

**Prompt:**
> I have a CSV of 30,000 web pages (columns as above). Goal: decide which pages to refresh first. Constraint: label "declining" comes from trend_direction, so trend_direction and trend_pct can NOT be features (leakage). List the safe, useful features as a table with three columns: feature name, what it measures, one gotcha to watch. Then one sentence on the single strongest feature.

- **What changed in the prompt:** I asked for a table with set columns plus a one-line takeaway.
- **What improved in the output:** it came back as a clean table I could paste straight into my notebook notes, one gotcha per feature (like the avg_position = 0 thing), and a clear closing line picking avg_position as the strongest signal. Zero cleanup needed.
- **What still failed:** nothing blocking. If I'm picky, its "strongest feature" pick is just its opinion — I'd still confirm it against my own data.
- **What I'd try next:** nothing to add. Adding more layers here would just bloat it. This is the one I'd keep.

---

## Final reusable prompt (works without me in the room)

> I have a CSV where each row is one web page. Columns include impressions_90d, ctr, avg_position, days_since_last_update, and trend_direction (up/down/flat).
>
> My goal is to decide which pages to refresh first.
>
> Important constraint: my label "declining" is derived from trend_direction, so trend_direction and trend_pct must NOT be used as features — using them would leak the answer.
>
> Given that, list the safe and useful features as a table with three columns: feature name | what it measures | one gotcha to watch when using it. Then add one sentence naming the single strongest feature and why.

---

## What I learned

The layer that helped most was the **constraint** (Version 4) — telling the AI the leakage trap directly is what made it stop giving me a wrong answer. The layer that helped least was the **audience** (Version 3); saying "I'm an ML intern" just added jargon and made it worse to read. So more layers isn't automatically better — the right single layer, aimed at the current weakness, is what moves the output.
