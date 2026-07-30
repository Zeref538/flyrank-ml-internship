---
name: claim-check
description: Check every number in a draft against the source it came from. Use before submitting any deliverable, README, project card, or presentation slide that states a metric, count, percentage, date, or filename. Returns VERIFIED / WRONG / LOOSE / UNVERIFIABLE per claim with the source. Triggers - "claim check", "check my numbers", "verify this draft", "is this number right".
---

# Claim check

You check claims. You do not improve writing, and you do not add claims.

## The job

Given a draft file, return one row per checkable claim:

| claim | verdict | source | what the source says |
|---|---|---|---|

Verdicts, and there are four, not three:

- **VERIFIED** — an exact match in a source, or a match that rounds correctly at two or more decimal places.
- **WRONG** — a source exists and disagrees.
- **LOOSE** — a source exists and the claim rounds to it at only one decimal place. `0.551` rounds to `0.55`, which is fine, but it *also* rounds to `0.6`, which hides the difference between `0.551` and `0.649`. Not a lie, not usable. Say which source value it should be.
- **UNVERIFIABLE** — no source found. **This is a finding, not a failure.** Never estimate, never reason from what sounds plausible, never write "approximately correct."

End with a count: verified / wrong / loose / unverifiable.

## What counts as a checkable claim

Any number, count, percentage, metric, date, filename, or comparison of the form "X beats Y". Skip opinions, plans, and descriptions of method.

## Source order — cheapest first, always

1. **`python .claude/skills/claim-check/lookup.py <the number as written>`**
   Normalizes commas and trailing zeros, searches the committed metrics JSON, the
   notebooks (source *and* outputs), and the markdown. Reports EXACT,
   ROUNDS-TO, ROUNDS-TO LOOSE, or NOT FOUND. Most claims die here.
2. **Grep** for text claims — filenames, column names, quoted phrases. For a
   claim about a file path, check the path exists. Do not assume it does.
3. **Recompute from `data/raw/content_refresh_anonymized.csv`** — only when 1 and
   2 can't settle it. Write the snippet, show it to the user, wait for approval,
   then run it. Never run a generated snippet unasked.

If a number appears in a *draft* but its only "source" is another draft, that is
not a source. Say UNVERIFIABLE.

## Hard rules

- **Never edit the draft.** Read-only. You report; the user decides.
- **Never print row-level data, content/client pseudonyms, or raw query text.**
  `lookup.py` deliberately does not search the CSVs in `work/outputs/` for this
  reason. Don't work around it.
- **Never print or echo a token.** Warehouse access is env-var only.
- **Never commit or push.**
- **Confirm before** running any generated code, or reading anything outside this
  repo.

## Claims about the Flewd hackathon data

Three shapes are wrong by construction. Flag these on sight, before looking for a source:

- **A query count without a stated denominator** → UNVERIFIABLE. ~8% of
  site-level and ~36% of URL-level GSC queries are anonymized (blank query).
  "N queries" means nothing until the draft says whether blanks are in or out.
- **Anything tying a search query to a conversion or revenue figure** → WRONG.
  GSC and GA4 join on landing-page URL only; GA4 has no query dimension for
  organic. The claim isn't unverified, it's unjoinable.
- **A per-page revenue average computed over all events** → WRONG. Revenue only
  populates on purchase events, so the denominator is wrong and the result still
  looks reasonable.

## Known ceiling — state it in the output

This checks that stated numbers match computed numbers. If the computation itself
was wrong, this will happily confirm a wrong number. It catches transcription and
staleness, not bad methodology.
