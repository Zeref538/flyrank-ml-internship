# FL-07 — Build the Agent · Build Log

**John Andrei Martinez · General AI Fluency · Week 5 · Checkpoint 1 (MVP)**

Agent: **claim-check** — checks every number in a draft against the source it came
from. Spec: [FL-06-agent-design.md](FL-06-agent-design.md).

Platform: a Claude Code skill in the ML repo, as chosen in FL-06.

**What's in the repo**

| File | What it is |
|---|---|
| `.claude/skills/claim-check/SKILL.md` | the agent's instructions |
| `.claude/skills/claim-check/lookup.py` | the one custom tool — 140 lines |
| `.claude/skills/claim-check/evals/expected.md` | the verdicts I predicted **before** building |
| `.claude/skills/claim-check/evals/draft_01.md` | the fixture draft, with deliberate errors |
| `.claude/skills/claim-check/evals/run_01_output.md` | the run, with every tool call |

**Live connections in use:** the repo filesystem (read + path checks), the
committed metrics JSON in `work/outputs/`, and the notebook outputs in
`work/notebooks/`. Nothing is mocked and nothing is pasted in by hand — the run
reads the same files the notebooks wrote.

---

## What actually happened, in order

### 1. The first thing I ran failed, and it changed the spec

The self-check on `lookup.py` failed on its second line:

```
assert round(0.551, 1) != 0.6
AssertionError
```

`round(0.551, 1)` **is** 0.6. Which means FL-06 eval case 3 was wrong: I'd written
that a draft saying "base rate was 0.6" should come back `WRONG`, and it isn't
wrong, it's just useless — one decimal place can't tell 0.551 from 0.649.

So I added a fourth verdict the spec didn't have: **LOOSE**. A one-decimal match
is reported, not blessed. Three verdicts turned out to be too few, and I only
found that out because I wrote the assertion before I trusted my own reasoning.

### 2. My own tool broke my own guardrail on run one

FL-06 says: never print client pseudonyms. First real lookup, searching for 0.88:

```
51 source(s) for 0.88:
  [EXACT] work/outputs/baseline_action_score.csv:7217
      7216,content_9cd88c77492f,client_6208ef0f77,0.0855,no_clear_gap,monitor,…
```

Two failures in one line. It printed `content_` and `client_` ids, and 48 of the
51 "sources" were per-row CSV values that settle nothing.

Fix: stop searching CSVs entirely. Row-level data goes through recompute, which
needs my approval, and never through search. Down to 12 hits, all meaningful.

### 3. Same guardrail, second leak — from a place I hadn't thought of

Fixed the CSVs, then searched for `29`:

```
  [EXACT] work/notebooks/capstone.ipynb:205
      4167   content_a8864e189b2e  client_d029fa3a95    0.925944
```

Notebook *outputs* contain pseudonyms too. And the match was fake: `29` matched
the `029` inside `client_d029fa3a95`. Earlier, `9999` matched
`content_9b6603da9999`.

Two fixes, because one wasn't enough:
- **Word boundaries** on the number regex, so a number has to stand alone.
- **Masking** — any `content_…` / `client_…` token gets replaced with
  `<redacted>` before printing, whatever file it came from.

I kept both. Boundaries fix the noise; masking is the actual guarantee. Result:
`29` went from 9 hits to 4, top hit *"Clients in the eligible pool: 29"*.

### 4. A bug that was in my terminal, not my data

Quoted notebook lines came back as `~16,000 dec�`. My first thought was the
notebook encoding was corrupted again — that happened during ML-08.

Checked all ten notebooks before touching anything: every one decoded as clean
UTF-8, zero replacement characters. The mangling was my cp1252 console. Fixed by
reconfiguring stdout in the tool, because a tool that quotes a source must not
corrupt what it quotes.

Worth writing down: if I'd "fixed" this by re-encoding the notebooks, I'd have
damaged ten clean files to solve a problem that was one line of Python away.

### 5. Eval case 5 failed — and the agent was right, I was wrong

The one case I said would stop the build. Draft claim: *"the March partition holds
9,841,378 rows."* I predicted `UNVERIFIABLE` because it needs the warehouse, and
the warehouse tool is off until I rotate my leaked HF token.

```
3 source(s) for 9841378:
  [EXACT] work/notebooks/w03_data_contract.ipynb:74
      Rows in month=2026-03: 9,841,378
```

The ML-04 notebook already ran that query in March and its output is committed. A
notebook output **is** a source. So the answer is `VERIFIED`, and the
stop-the-build condition correctly didn't fire — the agent didn't guess, it found
a real source I'd forgotten existed.

But the case stopped testing what I built it for, so I added **5b**: the *April*
partition, which nothing in the repo has ever queried. That returns
`NOT FOUND → UNVERIFIABLE`, which is the behaviour I actually wanted to prove.

### 6. Then a second assertion failed, and this time the tool was right

After adding word boundaries:

```
assert NUM.findall("P@50: 0.88,") == ["0.88"]
AssertionError    # actual: ["50", "0.88"]
```

The `50` in "P@50" *is* a standalone number. My assertion was wrong. Fixed the
assertion, not the regex.

Twice now — case 5 and this — the thing I'd written down was wrong and the code
was right. That's the whole reason this agent exists, and it's a bit funny that
it kept proving it during its own build.

---

## Results, first full run

**6 verified · 2 wrong · 1 loose · 1 unverifiable.** 8 of 10 rows matched my
pre-build predictions. Full transcript with every tool call:
`evals/run_01_output.md`.

Both errors it was built to catch, it caught:
- the "17× capacity" claim, correctly reported as **17 pages total**
- a reference to `w06_final.ipynb`, which doesn't exist

And the false-positive case passed — it flagged nothing on 13,562 / 29 clients.
That mattered more to me than the catches. An agent that cries wolf on correct
numbers is one I'd stop reading inside a week.

## Deviations from the FL-06 spec

| Spec said | Built | Why |
|---|---|---|
| Three verdicts | **Four** — added LOOSE | `round(0.551, 1) == 0.6`. The spec's three-way split couldn't express "true but useless precision." |
| Search the repo for a number | **Same, minus the CSVs** | It leaked pseudonyms and buried real sources in row noise. |
| "Never print row-level data" as an instruction | **Enforced in code** | An instruction I can forget; a regex I can't. The mask runs whatever the model does. |
| One helper tool | **One helper tool** | Unchanged. Read, grep, and path checks are Claude Code built-ins — nothing to build. |
| Eval case 5 = UNVERIFIABLE | **VERIFIED**, plus a new case 5b | My expectation was wrong; a committed notebook output is a source. |
| Warehouse tool (tool 5) | **Cut from the MVP** | Token still not rotated. Claims needing it return UNVERIFIABLE, which is the honest answer and required no code. |

## Cut from scope, deliberately

- **The warehouse connector.** Blocked on rotating the token. Not a code problem.
- **Flewd hackathon rules.** They're written into `SKILL.md` (the three
  wrong-by-construction claim shapes), but untested — I don't have the Flewd
  extracts on disk yet, so there's no fixture and I'm not claiming they work.
- **Auto-fixing a wrong number.** Never building this. Read-only is the point.

## What's next

1. Rotate the HF token, turn tool 5 on, add a warehouse eval case.
2. A fixture for the three Flewd rules once the extracts land.
3. Run it against a real deliverable I haven't pre-seeded with errors — the
   fixture proves it works on known bugs, not that it finds unknown ones.

## Screen capture

**TODO — John.** Record ~2 minutes, unedited: open the repo, run
`/claim-check .claude/skills/claim-check/evals/draft_01.md`, let it finish, show
the verdict table. Don't cut the tool calls out — the brief asks for the full loop
from request to result, and the tool calls *are* the evidence. Then attach it to
the submission as a file (the assignment accepts uploads).
