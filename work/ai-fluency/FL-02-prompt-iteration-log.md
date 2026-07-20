# FL-02 — Prompt Iteration Log — John Andrei Martinez

**The task (from my FL-01 audit, Target 1):** Writing FlyRank notebook code — specifically, code that scores which pages to refresh first and tests it honestly. I collaborate with AI on this, so getting the prompt right saves real time.

I worked through the basics chapters of the Anthropic Prompt Engineering Interactive Tutorial first, then applied the techniques below to my own task, one at a time.

---

## Version 0 — naive (what I'd have typed a month ago)

**Prompt:**
> Write code to score which pages to refresh.

**Output (excerpt):**
> ```python
> import pandas as pd
> df = pd.read_csv("data.csv")
> df["score"] = df["traffic"] * df["age"]
> df = df.sort_values("score", ascending=False)
> print(df.head(10))
> ```
> This scores pages by traffic times age...

**Problem:** it invented column names that don't exist in my data, made up a scoring formula, and there's no model and no honest test. Unusable.

---

## Version 1 — technique: role assignment

**Prompt:**
> You are a machine-learning engineer who cares about honest validation. Write code to score which pages to refresh.

- **What changed:** gave the model a role.
- **Observed difference in the output:** it stopped dumping a one-liner and started talking about train/test splitting and "avoiding overfitting." It added a `RandomForestClassifier` and a comment about validation. So the role pulled in better *habits* — but it still guessed my columns and still had no real label.
- **Still failing:** wrong column names, no honest split by client, no defined label.

---

## Version 2 — technique: context and motivation

**Prompt:**
> You are an ML engineer who cares about honest validation. My data is a CSV where each row is one web page, with columns impressions_90d, ctr, avg_position, days_since_last_update, and trend_direction (up/down/flat). I want to rank pages by how likely they are declining, so a content team can refresh the top ones first. Write the code.

- **What changed:** gave it my real columns and why I'm doing this.
- **Observed difference in the output:** it used my actual column names for the first time, built the label as `trend_direction == "down"`, and trained a model on the real features. The code would basically run. Huge jump in usefulness.
- **Still failing:** it fed `trend_direction` into the features *and* used it as the label — that's leakage (the answer is in the input). It didn't notice.

---

## Version 3 — technique: few-shot examples

**Prompt:** (same as V2, plus:)
> Here are examples of safe vs unsafe features:
> - SAFE: impressions_90d, ctr, avg_position, days_since_last_update
> - UNSAFE (leaks the label): trend_direction, trend_pct
> Use only safe features.

- **What changed:** showed it labeled examples of good vs bad features.
- **Observed difference in the output:** it dropped trend_direction and trend_pct from the feature list on its own and only used the safe ones. The leakage bug from V2 was gone. Showing examples fixed it faster than explaining would have.
- **Still failing:** it still used a plain random train/test split, so pages from the same client could land in both train and test — a subtler leak.

---

## Version 4 — technique: output structure

**Prompt:** (same as V3, plus:)
> Structure the code in four clearly commented sections: (1) load + build label, (2) select safe features, (3) train with a client-holdout split using GroupShuffleSplit on client_id, (4) print Precision@50.

- **What changed:** told it exactly how to organize the code and named the split I want.
- **Observed difference in the output:** the code came back in the four labeled blocks, and section 3 used `GroupShuffleSplit(groups=df["client_id"])` — so the client-holdout leak from V3 was closed. It was readable enough to paste into my notebook with section headers already there.
- **Still failing:** Precision@50 was written inline and slightly wrong (it sorted ascending once). Small bug, but a bug.

---

## Version 5 — technique: step decomposition

**Prompt:** (same as V4, plus:)
> Before writing code, list the steps in plain English and note where a mistake would cause leakage. Then write the code. For Precision@50, define it as a small helper function and show one assert that checks it on a tiny example.

- **What changed:** asked it to think in steps first and to self-check the tricky metric.
- **Observed difference in the output:** it wrote a short numbered plan (label → safe features → group split → rank → metric), flagged the two leakage points itself, then wrote cleaner code with a `precision_at_k` helper and an `assert` proving it on a 3-row example. The ascending-sort bug from V4 was gone because the assert would have caught it. This is the first version I'd trust without heavy editing.
- **Still failing:** nothing blocking. It's a bit long now, but every part earns its place.

---

## Cross-model comparison (final prompt on Claude vs ChatGPT)

I ran the Version 5 prompt on both.

- **Tone:** Claude explained *why* at each step (a short note before each block about the leakage risk). ChatGPT was more clipped — it wrote the plan and the code with fewer words, which was faster to skim but taught me less.
- **Accuracy:** both used the safe features and the group split correctly. The difference was the metric — Claude's `precision_at_k` and its assert were correct on the first try; ChatGPT's assert used a threshold comparison that passed even when the ranking was wrong, so its self-check was weaker.
- **Structure:** ChatGPT wrapped everything in a single `sklearn` Pipeline, which is tidy but hid the client-holdout split inside it and made it harder to see the honest-test part. Claude kept the four sections separate and visible, which fit the assignment better.
- **Failure point:** ChatGPT quietly filled missing values with 0 without saying so — which in this dataset is a real trap (avg_position = 0 means "no data," not rank zero). Claude called that out and added a comment. That one difference would have changed my results.

**Verdict:** for this task I'd use Claude — not because ChatGPT was bad, but because the honest-validation details (the assert that actually catches errors, the avg_position warning) are exactly what this task is about, and Claude got those right without me asking.

---

## Final reusable template (strip my specifics, keep the shape)

> You are an ML engineer who cares about honest validation.
>
> **Data:** [describe your rows and columns].
> **Goal:** [what decision the output supports, and for whom].
>
> **Safe vs unsafe features** (few-shot):
> - SAFE: [features known before the outcome]
> - UNSAFE (leaks the label): [anything derived from the label]
> Use only safe features.
>
> **Structure the code in these sections:** (1) load + build label, (2) select safe features, (3) train with [your validation split, e.g. group holdout on <id>], (4) print [your metric].
>
> Before writing code, list the steps in plain English and mark where a mistake would cause leakage. Then write the code, put [the tricky metric] in a small helper function, and add one `assert` that checks it on a tiny hand-made example.

---

## What I learned

Each technique fixed a specific weakness the last version still had, which is why doing them one at a time worked: role gave better habits, context stopped the guessing, few-shot killed the obvious leakage, structure closed the client-split leak, and step-decomposition caught the metric bug. The biggest single jump was **context and motivation** (V2) — until the model knew my real columns and goal it was just guessing. And the cross-model run taught me the real lesson: two models can both "work" and still differ on the one detail that matters (silently filling avg_position with 0), so I check the output, not the vibe.
