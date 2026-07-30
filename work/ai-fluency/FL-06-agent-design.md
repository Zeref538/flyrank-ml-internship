# FL-06 — Design Your Personal Agent

**John Andrei Martinez · General AI Fluency · Week 5**

> **Note on the attached hackathon brief:** `FlyRank_Hackathon_Brief.docx` wasn't
> downloaded when I wrote this, so this spec is designed against the FL-06 brief
> only. If the hackathon brief constrains the capstone agent differently, the
> scope section is the part that changes — the evals and guardrails hold either way.

---

## The job to be done

**One job: check every factual claim in a draft against the thing it came from.**

I write a deliverable, I paste it in, and the agent gives me back one line per
claim: verified, wrong, or can't-be-checked — with the source it looked at.

I'm not guessing that I need this. Three times this internship a number I had
already typed into a document turned out to be wrong:

| What I wrote | What was true | How it was caught |
|---|---|---|
| "the rule flags ~17× a 50-page capacity" | it flags **17 pages total** | ran the code |
| "142 core questions" in the internship materials | **~231** bullet questions | counted them |
| "70 million rows" (in a transcript I quoted) | **78,835,655** | checked the warehouse |

Each one took me 10–20 minutes to catch by hand and I only caught them because I
happened to re-run something. That's the job. Not writing, not researching —
**one narrow verification pass that I currently do badly and inconsistently.**

## The user and how often

Me, alone. Once per deliverable, right before I submit — so realistically
**2–4 runs a week** while the internship runs, and after that any time I put a
number in a CV, a README, or a project card. It's a "before you hit send" tool,
which is why speed matters more than depth: if it takes longer than reading the
draft myself, I won't use it.

## Tools and data it needs, and how I actually get access

| # | Tool | What it's for | Access plan |
|---|---|---|---|
| 1 | **Read file** | open the draft, and open the file a claim points at | Claude Code already has this on my local repo. No setup. |
| 2 | **Grep / search** | find whether a number literally appears anywhere in the repo | Already available. This alone catches most typos. |
| 3 | **Run a Python snippet** | recompute a claim from the actual data (`content_refresh_anonymized.csv`, 30k rows, already on disk) | Bash tool + pandas, both installed. The CSV is local and anonymized. |
| 4 | **Read the saved metrics** | `work/outputs/w05_model_metrics.json` and `w04_baseline_metrics.json` are the committed record of what my models scored | Plain JSON in the repo. This is the cheapest tool of the four and answers the most claims, so the instructions tell it to try this **first**. |
| 5 | *(optional, later)* **Warehouse query** | claims about the 79M-row warehouse that the local CSV can't answer | DuckDB over `hf://datasets/FlyRank/internship-warehouse`, needs a Hugging Face token. **Read from an environment variable only.** My old token got pasted into a chat, so step one is rotating it. Until that's done, tool 5 stays off and those claims come back as `UNVERIFIABLE`. |

No new accounts, no paid API, nothing to install. That's deliberate — the FL-04
"free only" constraint got broken last time by Azure token costs, and I'd rather
scope around it than discover it mid-build.

## Draft instructions

> You check claims. You do not improve writing, and you do not add claims.
>
> Given a draft file:
> 1. Extract every checkable claim — any number, count, percentage, metric,
>    date, filename, or "X beats Y" comparison. Skip opinions and plans.
> 2. For each one, find the cheapest source that could settle it, in this order:
>    the saved metrics JSON → a grep of the repo → recomputing from the CSV.
> 3. Return exactly one row per claim: `claim | verdict | source | what the source says`.
>    Verdict is `VERIFIED`, `WRONG`, or `UNVERIFIABLE`.
> 4. If you cannot find a source, the verdict is `UNVERIFIABLE`. Never estimate,
>    never reason from what sounds plausible, never say "approximately correct."
>    A claim you can't check is a finding, not a failure.
> 5. Quote the source value exactly. If it disagrees with the draft by any amount,
>    that is `WRONG` — including rounding.
> 6. End with a count: how many verified, wrong, unverifiable.
>
> You never edit the draft. You report; I decide.

Rule 4 is the one I care about most. The whole reason a wrong number survives is
that something confident agreed with it.

## Five eval cases, written before building (FL-03 style)

I built these from real errors, so I already know the right answer. Cases 4 and 5
are the ones that matter — they test the failure modes, not the happy path.

**Case 1 — the multiplier error (must catch)**
Input: a draft line saying *"the transparent rule flags ~17× a 50-page capacity."*
Expected: `WRONG`, source = the ML-02 notebook / the CSV, source value = 17 pages.
Pass if: verdict is `WRONG` **and** it reports 17 as a total, not a multiplier.

**Case 2 — the metric that exists in a file (must verify)**
Input: *"gradient boosting reached P@50 of 0.88 against the rule's 0.86."*
Expected: `VERIFIED` both halves, source = `w05_model_metrics.json`.
Pass if: both numbers verified and it names that JSON file — not the notebook,
not "my analysis." Naming a vague source is a fail even when the verdict is right.

**Case 3 — a rounding lie (must catch)**
Input: *"base rate on the test split was 0.55."* The stored value is `0.551`.
Expected: `VERIFIED` (0.55 is 0.551 rounded and I stated it as such).
Now the variant: *"base rate was 0.6."*
Expected: `WRONG`.
Pass if: it splits these two correctly. This is the case I expect it to fail
first, and if it can't do it, the agent isn't useful — most of my errors are
small, not wild.

**Case 4 — a correct claim it must NOT flag (false-positive test)**
Input: *"13,562 pages passed the eligibility gate across 29 clients."*
Expected: `VERIFIED`, both numbers.
Pass if: nothing is flagged. An agent that flags real numbers is worse than no
agent, because then I stop reading its output.

**Case 5 — something it genuinely cannot check (must admit it)**
Input: *"the March partition holds 9,841,378 rows"* — true, but it needs the
warehouse, and tool 5 is off.
Expected: `UNVERIFIABLE`, with the reason: needs warehouse access, token not set.
Pass if: it says unverifiable. **If it returns `VERIFIED` here, the agent is
dangerous and I stop the build**, because it just agreed with a number it never
looked at, which is exactly the thing I'm trying to prevent.

**Case 6 — a claim about a file that doesn't exist (must catch)**
Input: *"see `work/notebooks/w06_final.ipynb`."*
Expected: `WRONG` — no such file.
Pass if: it checks the path instead of assuming it.

## Risks and guardrails

**It must never:**
- **Edit the draft.** Read-only on my documents, always. If it can rewrite, then
  a wrong "fix" silently becomes the record, and I lose the one thing this agent
  exists to protect.
- **Print raw client data, real client names, or query text** from the warehouse
  — repo rule, and it applies to the agent's output too.
- **Print or log a token.** Env var only, never echoed.
- **Guess.** Covered by instruction 4 and eval case 5. This is the failure that
  ends the project, not a bug to patch.
- **Commit or push anything.**

**It must confirm before:**
- **Running any code I didn't hand it.** Recomputing from the CSV means it writes
  a snippet and executes it, and a generated snippet is the one irreversible-ish
  thing in the design. I see the snippet, I approve it, then it runs.
- **Reading anything outside the repo.** My drafts live next to personal files.

**What I'm accepting as a known limit:** it verifies claims against my own saved
outputs, so if the output itself was computed wrong, the agent will happily
confirm a wrong number. It catches transcription and staleness, not bad
methodology. That's a real ceiling and I'd rather name it than pretend the agent
makes my numbers true.

## Platform choice

**Chosen: a scripted agent on the scripting path — a Claude Code skill in the
repo** (`.claude/skills/claim-check/`), invoked as `/claim-check <file>`.

Why this one:
- The four tools it needs (read, grep, run Python, read JSON) are already how I
  work in that repo every day. There is no integration to build — the build hours
  go into the instructions and the evals, which is where the actual difficulty is.
- The data never leaves my machine. Anonymized or not, that's the right default
  for client data.
- Free on the plan I already have.
- It lives in the repo, so it's versioned with the thing it checks. A stale index
  in my portfolio chatbot already taught me what happens when a tool's knowledge
  drifts from the source.

**Against the alternative — a Claude Project with connectors:** I already built
one in FL-01, so this was the obvious candidate. I'm not using it because a
Project can read files I upload but can't **run** anything. Eval cases 1 and 4
need a real computation over 30,000 CSV rows, and case 6 needs a filesystem check.
A Project would have to be told the answers, which turns the agent into a
document I have to keep up to date by hand — the exact chore I'm trying to remove.
It's also the wrong direction on the leak risk: uploading the CSV to a hosted
Project is a copy of client data I don't need to make.

**Against n8n:** genuinely good at scheduled multi-step pipelines, and wrong here.
My trigger is "I'm about to submit," not a cron. A webhook plus a Python node
plus a credential store is a lot of moving parts to replace one command I type in
the terminal I'm already sitting in.

**Is this even an agent?** By the line I drew in FL-05 — *who chooses what happens
next* — yes, narrowly. I don't know in advance how many claims a draft has, which
tool settles each one, or whether a grep result is enough or it has to go
recompute. The route only exists after it runs. That's the difference between
this and my FL-04 study-notes pipeline, which is three prompts in an order I
fixed.

## Roughly 10 build hours

| | Hours |
|---|---|
| Write the 6 eval cases as fixture files with expected verdicts | 2 |
| Write the skill instructions + the source-priority order | 2 |
| Wire the recompute tool (a small helper so it isn't writing pandas from scratch each time) | 2 |
| Run the evals, fix what fails — I'm budgeting most of this for case 3, the rounding one | 3 |
| Write up what it caught on a real draft | 1 |

Evals get written first, on purpose. If I build first I'll grade it on whether it
looks smart, and I already know from ML-08 that the thing that looks like a win
usually isn't.
