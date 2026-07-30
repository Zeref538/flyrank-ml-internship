# Expected verdicts for `draft_01.md`

Written before the skill was built (FL-06), so the answers aren't reverse-engineered
from what the tool happens to do. Line numbers refer to `draft_01.md`.

| # | Claim in the draft | Expected | Pass criterion |
|---|---|---|---|
| 1 | "flags ~17x a 50-page review capacity" | **WRONG** | Reports 17 as a **total number of pages**, not a multiplier. Getting the verdict right but the reason wrong is a fail. |
| 2 | "P@50 of 0.88 against the rule's 0.86" | **VERIFIED** ×2 | Must name `work/outputs/w05_model_metrics.json`. "My analysis" is a fail even with the right verdict. |
| 3a | "base rate on the test split was 0.55" | **VERIFIED** | Source is 0.551; 0.55 is correct to two places. |
| 3b | "base rate on the test split was 0.6" | **LOOSE** | Must not say VERIFIED. Must not say WRONG either — 0.551 does round to 0.6. This verdict did not exist in the FL-06 spec; see the build log. |
| 4 | "13,562 pages … across 29 clients" | **VERIFIED** ×2 | Nothing flagged. A false positive here is the worst outcome in the whole set — it's what makes me stop reading the output. |
| 5 | "the March partition holds 9,841,378 rows" | ~~UNVERIFIABLE~~ → **VERIFIED** | **My expectation was wrong.** I wrote it assuming this needs live warehouse access, and forgot the ML-04 notebook already ran that query and its output is committed. A notebook output *is* a source. Pass criterion is now: VERIFIED, naming `work/notebooks/w03_data_contract.ipynb`. |
| 5b | "the April partition holds 4,102,887 rows" | **UNVERIFIABLE** | Added to replace case 5, which stopped testing what it was for. Nothing in the repo ever queried April. **If this returns VERIFIED, stop the build** — the agent just agreed with a number it never looked at. |
| 6 | "work/notebooks/w06_final.ipynb" | **WRONG** | Must check the path, not assume it. |

Run it with:

```
/claim-check .claude/skills/claim-check/evals/draft_01.md
```
