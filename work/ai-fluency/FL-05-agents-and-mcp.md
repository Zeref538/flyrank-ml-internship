# FL-05 — Agent Concepts and MCP Basics

**John Andrei Martinez · General AI Fluency · Week 4**

> **Scope note:** I haven't submitted FL-04 yet, so rather than classify a pipeline I never built, I classify the real one I *did* build: my FlyRank refresh-scoring pipeline (`work/notebooks/w04_baseline_score.ipynb`, `capstone.ipynb`).

---

## Workflow vs agent, in my own words

A **workflow** is a path I decided in advance. I write the steps and the order, and the model — if it appears at all — is one station on an assembly line I already laid out. Run it twice and you get the same route both times.

An **agent** decides its own route. I give it a goal, tools, and a way to know it's finished, and it chooses what to do next based on what it just learned. Run it twice and it might take a different path — call one tool three times, skip another, backtrack when a result surprises it.

The line isn't "how smart is the model" or "does it call tools." It's **who chooses what happens next.** If I can draw the whole route as a flowchart before it runs, it's a workflow. If the route only exists after the run, it's an agent.

This matters because agents cost more, run slower, and fail in harder-to-trace ways. A workflow that solves your problem beats an agent that solves it with more moving parts — and "we built an agent" is often a marketing claim about a workflow with a loop in it.

## What MCP is

The Model Context Protocol is a standard for how an AI application talks to outside systems. Its docs call it "a USB-C port for AI," and the analogy earns its place: before MCP, every AI app needed custom glue for every tool it touched — N apps × M tools meant N×M integrations. MCP makes it N+M: a tool exposes itself once as a server, and any MCP client can use it.

It has three primitives, and the difference between them is really **who's in control**:

- **Tools** — things the model can *do*, chosen by the model. Read a file, run a query, create a document. Model-controlled, so they need real care: a tool call has effects.
- **Resources** — data the model can *read*, attached as context. A file's contents, a schema, a doc page. Application-controlled — the client decides what to hand over.
- **Prompts** — reusable templates a *user* invokes deliberately, like a slash command. User-controlled.

Worth being precise about one thing: MCP does not make anything an agent. It's plumbing. A workflow can call MCP tools at a step I hardcoded, and it's still a workflow. MCP is what makes agents *possible* by giving them hands — but hands aren't autonomy.

## Classifying my pipeline: it's a workflow, clearly

My refresh-scoring pipeline is a workflow, and not a borderline one. It runs: load the starter slice → fixed eligibility gate → fixed feature list → score a hand-written baseline rule → train the same three models every time → evaluate both on a client-holdout split → write a ranked queue with reason codes. I wrote that sequence and it cannot deviate from it. No step decides "actually, let me check something else first."

Two details make it unambiguous. First, **there's no model in the control flow at all** — the sklearn models are predictors, not decision-makers about what the pipeline does next. Second, **the judgment is mine and stays mine**: I chose the 250-impression gate, Precision@50, and keeping staleness as a weak additive term after my signal check came back MIXED.

The workflow is also the *right* choice here, not a limitation. My lane exists so a human editor reviews the top of the queue and decides the action — and a reproducible, auditable ranking is worth more to them than a clever one that takes a different path each run.

## What it would take to make it an agent

The concrete upgrade: **a signal-auditing agent that decides for itself which assumptions to test before building the rule.**

Right now that step is me: I picked two signals, wrote two bucket queries, read the tables, and assigned verdicts by hand — and one came back MIXED, which changed my rule design. An agent version would get the goal ("find which observable signals predict decline here, and which don't") plus tools: query the warehouse, compute a bucket table, check a sample size, read the data dictionary. Then it would pick its own next query from each result — see the 181–365 day bucket has only n=17, judge that too thin, widen the window or pivot to another signal, and stop when it has enough verdicts to justify a rule.

That's genuinely agentic because the query sequence depends on what earlier queries returned; I couldn't draw it in advance. Three things it would need that I don't have today: **tool access to the warehouse** (an MCP server wrapping my DuckDB/Hugging Face queries), **a stopping condition** (verdicts collected, or a query budget spent — otherwise it loops forever on 79 million rows), and **a verification step**, because an agent choosing its own analysis can also talk itself into a confident wrong verdict on a tiny sample. Honestly, I'd want it to *propose* verdicts and make me confirm them — the lesson this track keeps re-teaching is that the number you didn't check is the number that's lying.

---

## Evidence: a working MCP connector, three tasks chat alone couldn't do

**Client:** Claude Code · **Server:** `claude.ai Figma` (remote MCP, `https://mcp.figma.com/mcp`) · **Status:** Connected

`claude mcp list` output:
```
claude.ai AngelList: https://mcp.angellist.com/mcp - ! Needs authentication
claude.ai Figma:     https://mcp.figma.com/mcp     - ✓ Connected
```

### Task 1 — read live account state (`whoami`)

A **tool** call returning data that exists only in Figma's systems:

```json
{
  "handle": "John Andrei",
  "plans": [{ "name": "John Andrei Martinez's team",
              "seat": "View", "tier": "starter",
              "key": "team::1514186208323291905" }]
}
```

Chat alone can't do this — it has no way to know my Figma handle, seat type, or team key. Note it also returned a **resource** link (`rate-limits-access.md`), which is the resources primitive in action: data attached as context rather than an action taken.

### Task 2 — create a real artifact in an external service (`generate_diagram`)

I had it build the pipeline diagram for this very explainer — my ML workflow rendered in FigJam from Mermaid syntax:

```
diagramId: 958b7302-1f3a-4d3e-b0af-b7e23d084abd
file:      https://www.figma.com/board/L466dXyI0bJMjMeTS32yuI
```

This is the clearest "not chat" case: a persistent object now exists in my Figma account that didn't before. Chat could have written me the Mermaid code, but it could not have put a board in my account.

### Task 3 — read that external state back (`get_figjam`)

Round-tripping proves it's real and not a fabricated confirmation. Reading node `0:1` of the file returned the actual canvas contents, including exact coordinates the server assigned during layout — numbers I never supplied:

```html
<canvas id="0:1" name="Page 1">
  <shape-with-text id="1:3"  x="-208" y="476">Starter CSV: 30,000 pages</shape-with-text>
  <shape-with-text id="1:6"  x="144"  y="476">Prepare features (fixed list)</shape-with-text>
  <shape-with-text id="1:24" x="1904" y="476">Human editor decides action</shape-with-text>
  <connector id="1:27" connectorStart="1:3" connectorEnd="1:6" .../>
  ...
</canvas>
```

**One honest failure worth recording.** My first attempt at task 3 was `get_libraries`, which returned: *"This tool is not supported for Figjam files. Supported file type: Design."* That's a useful thing to have hit — it shows MCP servers enforce their own constraints and return real errors rather than a model's guess at an answer. Plain chat, asked the same question, would more likely have invented a plausible library list than told me the file type was wrong.
