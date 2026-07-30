# FL-04 — Ship an Automation Workflow

**John Andrei Martinez · General AI Fluency · Week 4**

## The task I picked, and why

From my FL-01 audit, **Target 2: "first-pass summaries of long reading"** — classified *delegate with review*. It's the honest choice because it's the bottleneck I actually hit: this internship ships ~42,000 words of required reading (two long framework docs plus three hour-long session transcripts), and I'm carrying a full course load. My FL-01 done-well definition was: *≤30 min per document, 0 critical misses found on spot-check, a sections-to-read list I actually used.*

The variant I built is **source-grounded study notes**, with a third step most people skip: a verification pass that checks the summary's own numbers against the source. That step exists because my ML track has repeatedly proven that an unverified number is the one that's wrong.

---

## The flow (sketched before building)

```
   ┌──────────────────────┐
   │  INPUT: one long doc │
   │  (transcript or .md) │
   └──────────┬───────────┘
              │
   ┌──────────▼───────────────────────────────┐
   │ STEP 1 — MAP  (gather)                   │
   │ Extract the skeleton only: every section │
   │ heading, its size, and where numbers or  │
   │ claims cluster. No summarising yet.      │
   └──────────┬───────────────────────────────┘
              │  handoff: a section table
   ┌──────────▼───────────────────────────────┐
   │ STEP 2 — TRIAGE  (synthesize)            │
   │ Decide which 3-5 sections are load-      │
   │ bearing FOR MY LANE and must be read in  │
   │ full. Everything else = skim or skip.    │
   │ Emit the key claims with numbers.        │
   └──────────┬───────────────────────────────┘
              │  handoff: read-list + claim list
   ┌──────────▼───────────────────────────────┐
   │ STEP 3 — VERIFY  (review)                │
   │ Take each claim from Step 2 and check it │
   │ against the source text. Mark CONFIRMED, │
   │ CORRECTED, or UNVERIFIABLE.              │
   └──────────┬───────────────────────────────┘
              │
   ┌──────────▼───────────────────────────────┐
   │ OUTPUT: read-list I trust + a verified   │
   │ fact sheet + a list of what I must still │
   │ read myself                              │
   └──────────────────────────────────────────┘
```

Three distinct steps, clean handoffs: Step 1 hands Step 2 a **structure table**; Step 2 hands Step 3 a **claim list**. Each step's output is the next step's only input, which is what makes it a pipeline rather than one long prompt.

---

## The build: a Claude Project with three saved prompts

No code. One Claude Project named `Study Notes Pipeline`, with the project instructions below plus three prompt templates I paste in order.

### Project instructions (configuration)

```
You are my study-notes pipeline. I am an ML intern on FlyRank's Applied
Search Intelligence track; my lane is Refresh / Content Opportunity Scoring
(ranking pages for refresh review, evaluated with Precision@50 under a
client-holdout split).

Rules that apply to every step:
- Never summarise a section you were not given the text of. If you cannot
  see it, say "not in the provided text."
- Every number you report must be quoted from the source, not recalled.
- Judge relevance against MY lane, not against general interest.
- Prefer "this section is skippable for me" over padding the read-list.
  A short honest read-list beats a complete one.
- Plain words. Define a term the first time you use it.
```

### Step 1 prompt — MAP

```
STEP 1 of 3: MAP. Do not summarise yet.

Here is a long document: [PASTE]

Return only a table with one row per section:
| section | approx. words | contains numbers/claims? | one-line topic |

Then list any place the document points at ANOTHER document or resource
I would need.
```

### Step 2 prompt — TRIAGE

```
STEP 2 of 3: TRIAGE. Input is your Step 1 table.

1. Pick the 3-5 sections I must read IN FULL for my lane. For each, one
   line on why it is load-bearing for me specifically.
2. List the sections I can skip, grouped, with a one-line reason.
3. Extract every factual claim with a number in it, as a flat list. These
   go to Step 3 for checking — do not vouch for them yet.
```

### Step 3 prompt — VERIFY

```
STEP 3 of 3: VERIFY. Input is your Step 2 claim list plus the source text.

For each claim, search the source and mark it:
- CONFIRMED (quote the supporting line)
- CORRECTED (give the real figure and the quote)
- UNVERIFIABLE (not stated in the provided text)

Flag any claim that contradicts another claim in the same document.
End with: "What I must still read myself and why."
```

---

## The five runs

### Run 1 — `docs/ml-intern-dataset-and-lane-guide.md` (5,817 words, 17 sections)

**Step 1 output (abridged):** 17 sections mapped, §0–§16. Numbers cluster in §5 (starter results) and §2 (table row counts). Points outward to: the data dictionary, the HF dataset card, and `ml-core-foundation-framework.md`.

**Step 2 read-list:** §5 *Starter Playground* (the baseline-vs-model numbers my whole lane is benchmarked against), §8 *Lane Guide* (contains my Lane 2 spec and its "common mistakes" list), §7 *Decline vs Consolidation* (this is literally my label-definition problem), §12 *Validation Rules*, §14 *Public-Safe Output Rules* (my paper is public). **Skipped:** §0, §1, §16 (framing prose I already have), §9 (freestyle — not my lane), §3 (field types — covered by the data dictionary).

**Step 3 verification:**

| Claim | Verdict |
|---|---|
| baseline rules Precision@50 = 0.240 | **CONFIRMED** — and independently reproduced: my own pipeline run printed 0.240 |
| random forest Precision@50 = 0.740 | **CONFIRMED** — my run printed 0.740 |
| starter CSV = 30,000 rows × 44 columns, 32 clients | **CONFIRMED** — my own load reports 30,000 rows, 44 cols, 32 clients |
| daily fact = 78,835,655 rows | **CONFIRMED** — matches the HF dataset card |
| 9 of 70 clients have 12+ months of history | **UNVERIFIABLE from this doc alone** — stated, not shown; would need a `dim_clients` query |

**Must still read myself:** §8's Lane 2 "common mistakes" list, word for word — it's the rubric my capstone gets judged against.

---

### Run 2 — `docs/ml-core-foundation-framework.md` (5,600 words, 21 sections)

**Step 1 output:** 21 numbered sections (§0 *Executive Map* → §20 *Final Mental Model*), plus a table of contents. Question-heavy throughout rather than prose-heavy.

**Step 2 read-list:** §3 *Purpose And Problem Framing* (the week-2 session said everything it taught came from here), §4 *Data And Labels*, §8 *Evaluation And Validation*, §13 *Failure Modes*, §19 *Complete First-Principles Checklist*. **Skipped for now:** §14–§17 (deployment, MLOps, monitoring, cost — real topics, but nothing in my capstone ships to production), §12 (causality — explicitly out of scope, since my paper cannot make causal claims).

**Step 3 verification — this run caught something:**

| Claim | Verdict |
|---|---|
| "21 sections" (per the week-2 session) | **CONFIRMED** — exactly 21 numbered sections, §0 through §20 |
| "142 core questions" (per the week-2 session) | **CORRECTED → ~231.** Counting bullet lines ending in a question mark: **231 total** (181 across §0–§18, plus 50 in the §19 checklist). No slice of the file yields 142 — not the whole file, not §0–§18, not §19 alone. |

Worth being precise about the direction of the error: the file contains **more** guidance than advertised, not less, so the claim undersells the document rather than overselling it. Most likely the count comes from an earlier revision. Either way, the pipeline caught a stated figure that doesn't match the artifact — which is the entire reason Step 3 exists.

**Must still read myself:** §19 in full. It's a 50-question checklist meant to be *run*, not summarised.

---

### Run 3 — `tactiq-...-aTxLqzQ5Isg.txt` — ML Week 2 session (6,253 words)

**Step 2 read-list:** the framing-flow walkthrough (goal → decision → task type → target → metric → action, run live on the refresh lane — my lane), the supervised/unsupervised split, the overfitting explanation, and the pointer to the framework file. **Skipped:** the opening recap and the closing logistics.

**Step 3 verification:**

| Claim | Verdict |
|---|---|
| hand rule ≈ 24%, model ≈ 74% ("24 and 74") | **CONFIRMED** — repeated throughout, matches the lane guide's 0.240 / 0.740 |
| "around 54% of the pages" are declining | **CONFIRMED** — and independently reproduced: my own count gives 54.2% |
| team ships "around 50 refreshes a month" → hence Precision@50 | **CONFIRMED** as the stated premise (it's a capacity assumption, not a measurement) |
| some availability flags are "nil, not false" — filter with `IS TRUE` | **CONFIRMED**, and I acted on it: my ML-04 notebook filters `gsc_data_available IS TRUE` |

---

### Run 4 — `tactiq-...-ROEad3SDI9Q.txt` — ML Week 1 session (8,278 words)

**Step 2 read-list:** the concept-oriented/decompose-backwards method, the ML-as-a-loop model, the when-*not*-to-use-ML hierarchy, and the capstone framing. **Skipped:** the speaker's personal-background segment and the closing Q&A (useful once, not reference material).

**Step 3 verification — this run caught an internal contradiction:**

| Claim | Verdict |
|---|---|
| dataset is "**79 million** rows" | **CONFIRMED** — matches 78,835,655 daily fact rows |
| dataset is "**70 million** rows" | **CORRECTED** — the *same transcript* says both figures. 79M is the right one; 70M appears to be a slip. (70 is separately the number of *clients* in the daily source, which is likely where the confusion comes from.) |
| AI Overviews → page visited only ~8% of the time; ~1% click the source | **UNVERIFIABLE from this source** — an external industry statistic, asserted without a citation. Not something I would repeat in my public paper without finding the primary source. |
| ~70% of searches end with zero clicks | **UNVERIFIABLE from this source** — same reason. |

That last pair is the most useful thing this run produced: two headline statistics I'd have been tempted to quote in my research paper, correctly flagged as un-sourced. My paper's public-safety rules mean I can't launder someone else's uncited number into my own claim.

---

### Run 5 — `tactiq-...-Ez7DlKSvEFY.txt` — Cohort kickoff (16,056 words)

**Step 2 verdict: mostly skippable for my lane, and saying so is the win.** This is the longest input of the five (16k words, ~65 min to read) and almost none of it is technical. **Read in full:** only the completion-requirements and Anthropic-courses segments. **Skipped:** company history, the founder's background, the portal walkthrough, and the extended Q&A.

**Step 3 verification:**

| Claim | Verdict |
|---|---|
| ~38,000 applications; 130 countries represented | **CONFIRMED** as stated in the source (self-reported figures) |
| 19 free Anthropic courses via Skilljar | **CONFIRMED** as stated |
| program is free; no certificate fee | **CONFIRMED**, stated emphatically and repeatedly |

**Honest note on this run:** the pipeline's real value here was negative — it told me a 16,000-word document was worth ~5 minutes of my attention. A summary tool that only ever says "here's what's important" would have handed me a tidy digest of material I didn't need.

---

## Time accounting (honest, including setup)

**Method, stated plainly so the numbers can be judged:** the manual baseline is one document read end-to-end (Run 1's lane guide, which I *did* read in full earlier in this project before building any of this). The other four are compared using the same reading rate, not four separate stopwatch runs — I'm not going to pretend I timed all five by hand.

| | Manual | Pipeline |
|---|---|---|
| Run 1 — lane guide (5,817 w) | ~24 min (measured, full read) | ~7 min |
| Run 2 — framework (5,600 w) | ~23 min (est. @ 250 wpm) | ~7 min |
| Run 3 — week-2 transcript (6,253 w) | ~25 min (est.) | ~6 min |
| Run 4 — week-1 transcript (8,278 w) | ~33 min (est.) | ~7 min |
| Run 5 — kickoff transcript (16,056 w) | ~64 min (est.) | ~5 min |
| **Total** | **~169 min (2h 49m)** | **~32 min** |

**Setup cost, which the totals above exclude:** ~55 minutes to sketch the flow, write and revise the three prompts (the first version of Step 1 kept summarising instead of just mapping — I had to add "Do not summarise yet" explicitly), and set up the project.

**Net for this batch: ~169 min → ~87 min including setup, so roughly 82 minutes saved on five documents.** The setup is a one-time cost, so the honest framing is that the pipeline paid for itself inside this single batch and every future document is close to pure gain. I'd also note the pipeline's 32 minutes buys something the manual read didn't: a verified fact sheet, which is why Run 2 and Run 4 caught errors that a straight read-through would likely have absorbed as true.

---

## Where it breaks, and what a human must still check

**1. It cannot judge what it wasn't shown.** Long transcripts exceed a comfortable paste, so I chunk them — and a claim split across a chunk boundary can be triaged as "unverifiable" purely because of where I cut. **Human check:** if Step 3 says UNVERIFIABLE for something that matters, re-run it with the relevant chunk before believing the verdict.

**2. Triage is confidently wrong at the edges.** Step 2 skipped §14–§17 of the framework (deployment, MLOps, monitoring, cost) because my capstone doesn't ship to production. That's right today and wrong the moment I want a job where it does. **Human check:** the skip-list is a decision about *my current goal*, not a claim about value — I re-read it when the goal changes.

**3. "CONFIRMED" only means "the source says so."** Run 5's 38,000 applications is confirmed *as stated*; it isn't independently true. Step 3 verifies fidelity to the source, not the source's accuracy. **Human check:** for anything going into my public paper, a source-confirmed figure still needs a primary citation — which is exactly why Run 4's un-sourced statistics stay out.

**4. It reports rather than judges.** The pipeline told me the "142 questions" figure is really ~231 and that one transcript says both 70M and 79M. It did *not* decide what to do about either. **Human check:** interpretation is mine — I concluded the 142 is stale-count and 79M is correct, and both conclusions are my call, not the tool's.

**5. Numbers can be quoted correctly and still mean nothing.** Nothing in this pipeline knows that `avg_position = 0` means "no data" rather than rank zero, or that CTR is a ×100 percentage. It will faithfully quote a figure into a wrong conclusion. **Human check:** every number that reaches my notebooks gets re-derived from the data, not copied from notes.

**Does it run end to end on a brand new input?** Yes — Run 5 was a document I had not opened before building the pipeline, and it went through all three steps unmodified, correctly concluding that most of it wasn't worth my time.
