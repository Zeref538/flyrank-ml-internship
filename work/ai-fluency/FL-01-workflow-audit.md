# FL-01 — AI Workflow Audit

**John Andrei Martinez · CS undergrad (OLFU) · ML Engineering Intern @ FlyRank · Week 1**

Classification framework: Ethan Mollick's "On-boarding your AI Intern" — *just me / delegate to AI with review / collaborate with AI / fully automate.*

## 1. Workflow audit (13 recurring tasks from my real week)

| # | Task | Classification | Rationale (one line) |
|---|---|---|---|
| 1 | Framing my FlyRank research question (decision, action, cost of a wrong call) | **Just me** | The internship grades *my* judgment; if AI frames the problem, I learn nothing and can't defend it to reviewers. |
| 2 | Verifying numbers/claims before they go in a notebook or paper | **Just me** | The track's core rule is "never let AI decide what is true" — an AI already drafted two wrong claims for me this week that only running the code caught. |
| 3 | Writing pandas/sklearn code for FlyRank notebooks | **Collaborate** | AI drafts fast, but I hit real gotchas (×100 rate columns, avg_position=0 = "no data") that need my dataset knowledge to catch. |
| 4 | Debugging environment/setup errors (Windows encoding, wrong interpreter, git conflicts) | **Delegate with review** | AI resolves these far faster than I do; I review the fix and confirm the command before running anything destructive. |
| 5 | Understanding new ML concepts (leakage, client-holdout, Precision@K) | **Collaborate** | AI explains at my level and I test understanding by re-explaining back; reading docs alone is slower, but I must do the re-explaining myself or it doesn't stick. |
| 6 | Writing commit messages and repo documentation (READMEs) | **Delegate with review** | Low-risk, well-defined from the diff/content; I review for accuracy since docs that overstate results violate my "show my work honestly" claim. |
| 7 | Thesis (ACRA) — writing/revising manuscript sections | **Collaborate** | AI helps structure and tighten prose, but the methodology and results are mine and my adviser checks my voice. |
| 8 | Studying for certifications (Anthropic Academy, Coursera modules) | **Just me** | The point is certified *personal* competence; AI summaries would let me pass without learning, which defeats the credential. |
| 9 | Portfolio site content updates (new projects in data.js, case-study copy) | **Collaborate** | AI drafts copy from my project facts; I correct numbers and tone because recruiters will probe anything on that page in interviews. |
| 10 | Formatting/converting documents (notes → tables, markdown, diagrams) | **Fully automate** | Zero-judgment transformation with instantly checkable output; my time adds nothing. |
| 11 | First-pass summaries of long reading (lane guide, dataset manifests, Mollick articles) | **Delegate with review** | AI's summary tells me where to focus, then I read the load-bearing sections myself — full reads of everything don't fit a 4-course week. |
| 12 | Scanning job/internship postings for fit | **Delegate with review** | AI filters against my profile fast; I make the final apply/skip call since fit is partly about what I want, not just keywords. |
| 13 | Weekly planning across internship + school deadlines | **Collaborate** | AI is good at surfacing conflicts and sequencing, but only I know real priorities and my energy levels. |

**Honestly "just me" (with reasons):** #1 (problem framing — graded judgment), #2 (truth verification — the anti-hallucination discipline the ML track is built on), #8 (cert study — the credential must reflect real personal competence).

## 2. Toolkit evidence

- Claude account: active (claude.ai) — Projects in use
- ChatGPT account: active
- Anthropic Academy: enrolled in **AI Fluency: Framework & Foundations**, Module 1 completed *(screenshot attached)*
- Claude Project: configured *(screenshot attached; instructions below)*

## 3. Claude Project custom instructions (as configured)

> **Who I am:** John Andrei Martinez, CS undergraduate at Our Lady of Fatima University
> (Bulacan, PH), ML Engineering Intern at FlyRank on the Applied Search Intelligence
> track, building a refresh-priority ranking capstone on real search data. Portfolio:
> johnandrei.vercel.app · GitHub: Zeref538. Main projects: ACRA (YOLOv8 color-
> accessibility thesis, 0.740 mAP50), Aegix AI (RAG contract screening, 84.5% accuracy).
>
> **Tone preferences:** plain words first, then the technical term in parentheses.
> Explain like a mentor, not a lecture. Be blunt about what's wrong. When I ask for
> code, add short comments explaining the why.
>
> **Current goals (8 weeks):** ship an honest FlyRank capstone (beat a transparent
> baseline under client-holdout validation, no leakage, careful claims), finish the
> AI Fluency track, complete Anthropic Academy certification, and refine my portfolio
> around one claim: "I turn messy real-world data into honest, decision-ready ML —
> and I show my work."
>
> **Standing rules:** never invent numbers — if I haven't given you the data, say so
> and tell me what to run. Flag any claim in my drafts that sounds causal or
> overclaims. Push back when I try to skip verification.

## 4. Three target tasks for FL-02 → FL-04 (with "done well" definitions)

**Target 1 — Writing FlyRank notebook code (from task #3, collaborate).**
Done well means: the notebook runs top-to-bottom with no errors on the first try after AI assistance; every number printed was verified by actually executing the code (zero unverified claims); and I can explain every line out loud without notes — measured by re-explaining the cell to my Claude Project and having it find no gaps.

**Done-well metric:** 0 execution errors, 0 unverified claims, 100% of cells I can explain unaided.

**Target 2 — First-pass summaries of long reading (from task #11, delegate with review).**
Done well means: the AI summary identifies the 3–5 sections worth reading in full; after my own read of those sections I find no critical point the summary missed or misstated (spot-check against the source); and the whole cycle takes under 30 minutes per document versus ~90 minutes for an unaided full read.

**Done-well metric:** ≤30 min per document, 0 critical misses found on spot-check, sections-to-read list I actually used.

**Target 3 — Portfolio case-study copy (from task #9, collaborate).**
Done well means: every metric in the copy traces to a real artifact (repo, notebook, or report I can open); the copy passes my Claude Project's pressure-test against my proof statement ("does this earn its place?"); and it reads in my voice — verified by a friend or the tutor project confirming it doesn't sound templated.

**Done-well metric:** 100% of numbers source-traceable, passes the pressure-test with ≤1 revision, third-party voice check passed.
