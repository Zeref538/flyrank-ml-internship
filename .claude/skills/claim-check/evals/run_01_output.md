# Run 1 — end-to-end on `draft_01.md`

`/claim-check .claude/skills/claim-check/evals/draft_01.md`
No hand-editing mid-run. Every verdict below came from a tool call, and the tool
calls are listed underneath so each row can be re-run.

| # | Claim | Verdict | Source | What the source says |
|---|---|---|---|---|
| 1 | rule flags "~17x a 50-page review capacity" | **WRONG** | `work/notebooks/w01_research_question.ipynb:93` | "flags only **17 pages**. It can't even fill one 50-page review cycle." 17 is a total, not a multiplier — the claim inverts it. |
| 2a | gradient boosting P@50 = 0.88 | **VERIFIED** | `work/outputs/w05_model_metrics.json:36` | `"P@50": 0.88` |
| 2b | the rule's P@50 = 0.86 | **VERIFIED** | `work/outputs/w05_model_metrics.json:8` | `"P@50": 0.86` |
| 3a | test base rate = 0.55 | **VERIFIED** | `work/outputs/w05_model_metrics.json` | `test_base_rate = 0.551`; correct to two places |
| 3b | test base rate = 0.6 | **LOOSE** | same | 0.551 does round to 0.6 at one decimal place, so this isn't false — but one place can't separate 0.551 from 0.649. Use 0.55. |
| 4 | 13,562 pages | **VERIFIED** | `work/outputs/w05_model_metrics.json:2` | `"eligible_pages": 13562` |
| 4b | 29 clients | **VERIFIED** | `work/notebooks/w05_model.ipynb:56` | "Clients in the eligible pool: 29" |
| 5 | March partition = 9,841,378 rows | **VERIFIED** | `work/notebooks/w03_data_contract.ipynb:74` | "Rows in month=2026-03: 9,841,378" |
| 5b | April partition = 4,102,887 rows | **UNVERIFIABLE** | — | `NOT FOUND: 4,102,887 appears in no searched source.` Nothing in this repo has ever queried April. Warehouse tool is off (token not rotated). |
| 6 | "see `work/notebooks/w06_final.ipynb`" | **WRONG** | filesystem | `ls: cannot access … No such file or directory` |

**Count: 6 verified · 2 wrong · 1 loose · 1 unverifiable.**

**Ceiling, restated as the skill requires:** this only confirms that the stated
numbers match the computed ones. If a computation was wrong, this run would have
confirmed it happily.

## The tool calls behind it

```
$ python .claude/skills/claim-check/lookup.py 17
15 source(s) for 17:
  [EXACT] work/notebooks/w01_research_question.ipynb:93
      2) The simple rule (not updated in 180+ days AND 500+ impressions) flags
      only 17 pages. It can't even fill one 50-page review cycle, while ~16,000 dec…

$ python .claude/skills/claim-check/lookup.py 0.88
12 source(s) for 0.88:
  [EXACT] work/outputs/w05_model_metrics.json:36
      "P@50": 0.88,
  [EXACT] work/notebooks/w05_model.ipynb:173
      gradient_boosting   0.9  0.90  0.88    0.618   0.667

$ python .claude/skills/claim-check/lookup.py 0.86
8 source(s) for 0.86:
  [EXACT] work/outputs/w05_model_metrics.json:8
      "P@50": 0.86,
  [EXACT] work/notebooks/w05_model.ipynb:169
      baseline rule (ML-07)   0.9  0.95  0.86    0.582   0.651

$ python -c "import json;print(json.load(open('work/outputs/w05_model_metrics.json'))['test_base_rate'])"
0.551

$ python .claude/skills/claim-check/lookup.py 13,562
10 source(s) for 13,562:
  [EXACT] work/outputs/w04_baseline_metrics.json:2
      "eligible_pages": 13562,
  [EXACT] work/outputs/w05_model_metrics.json:2
      "eligible_pages": 13562,

$ python .claude/skills/claim-check/lookup.py 29
4 source(s) for 29:
  [EXACT] work/notebooks/w05_model.ipynb:56
      Clients in the eligible pool: 29

$ python .claude/skills/claim-check/lookup.py 9841378
3 source(s) for 9841378:
  [EXACT] work/notebooks/w03_data_contract.ipynb:74
      Rows in month=2026-03: 9,841,378

$ python .claude/skills/claim-check/lookup.py 4102887
NOT FOUND: 4102887 appears in no searched source.
  -> verdict UNVERIFIABLE unless you can recompute it from data/raw/.

$ ls work/notebooks/w06_final.ipynb
ls: cannot access 'work/notebooks/w06_final.ipynb': No such file or directory
```

## Against `expected.md`

8 of 10 rows matched what I predicted before building. The two that didn't:

- **Case 5** — I predicted UNVERIFIABLE. It's VERIFIED, and the agent was right:
  the ML-04 notebook already ran that query and the output is committed. My
  expectation was wrong, not the tool's answer. Replaced with case 5b (April),
  which nothing has ever queried, so it still tests the thing case 5 was for.
- **Case 3b** — I predicted WRONG. It's LOOSE, a verdict that didn't exist when I
  wrote the spec. See build log entry 1.

The stop-the-build condition did not fire: nothing came back VERIFIED without a
named source.
