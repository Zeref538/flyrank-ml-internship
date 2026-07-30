# Three Roads — Choosing My Stack — John Andrei Martinez

## The four constraints I gave the AI

1. **Free only.** Student budget. No paid hosting, no paid database.
2. **My honest skill level.** Comfortable in React, JS, Python, and deploying to Vercel — I've shipped several full-stack projects. Not experienced with SSR frameworks or CMS plumbing, and I don't want to learn one just for a portfolio.
3. **What the portfolio needs to do** (from my content map): four pages — Home with the one-line claim, Work with three case studies (FlyRank capstone, ACRA, Aegix), a short About, and Contact. Every CTA funnels to one action: a hiring manager emails me.
4. **How my work must be displayed.** This is the constraint that actually decided it. My work is *not* pretty pictures — it's models with numbers behind them. So I need: image galleries of real screenshots per project, **live demo links** (ACRA, Aegix, and CafèSync all have working deployments), a visible route to the **code repos**, and room for **long-form reading**, because my capstone deliverable is a research paper with charts and a methodology section.

**Does anything have to be dynamic?** Yes — and this is where my answer differs from what I'd guess most people conclude. See the backend section below.

---

## The three options, simplest to most powerful

### Road 1 — Plain static HTML/CSS, hosted on GitHub Pages

**How I'd build:** hand-write the pages, one HTML file each, one stylesheet. No build step, no dependencies.
**Host:** GitHub Pages, free, straight off `main`.
**Backend:** none.
**The real trade-off:** unbeatable for reliability and speed — nothing to update, nothing to break, and it will still work in five years untouched. But every case study is copy-pasted markup, so adding a fourth project means editing four files and keeping them consistent by hand. It also can't do anything interactive, which for me is a hard limit rather than an inconvenience.

### Road 2 — React + Vite, static build, on Vercel or Netlify

**How I'd build:** components for the repeating pieces, all content in one `data.js` file so adding a project is one object, not a page.
**Host:** Vercel or Netlify free tier, auto-deploy on push.
**Backend:** none — it's a static bundle after `vite build`.
**The real trade-off:** the sweet spot for maintainability. One content file means the site can't drift out of sync with itself, and I already know this stack so there's no learning tax. What it gives up: anything requiring a secret. No API key can live in a static bundle, so any AI feature is off the table.

### Road 3 — React + Vite **plus serverless functions**, on Vercel

**How I'd build:** Road 2, plus an `api/` folder of serverless functions for anything needing a key or server-side work.
**Host:** Vercel free tier — the Hobby plan includes serverless function invocations.
**Backend:** yes, but only just: stateless functions, no database, no server to run.
**The real trade-off:** it unlocks real interactivity, and it's the only road where a recruiter can *ask my portfolio questions*. The cost is that I now own a moving part — a function that can break, get abused, or run up a bill on whatever API it calls.

---

## Pressure-testing the front-runner

**What breaks if I pick the simplest (Road 1)?** The thing that makes my portfolio worth visiting. My differentiator isn't layout, it's that I build working AI systems — and a static page can only *claim* that. It also can't host zeref-bot, the RAG chatbot that answers recruiter questions about me, which is itself a live demo of the exact skill I'm selling. Road 1 would make me describe my work instead of showing it.

**What do I maintain if I pick the most powerful (Road 3)?** Honestly: one file, `api/chat.js` — 182 lines. Plus a static vector index I have to regenerate (`npm run index`) whenever I change site content, or the bot answers from stale information. That's a real maintenance obligation and the most likely thing to quietly rot. It's also where the abuse risk lives, which is why I put per-IP rate limiting in the function and made it fail gracefully with a "just email me directly" message instead of an error.

**Can I finish in two weeks?** Yes — because I'm not starting from zero. The site is already live at johnandrei.vercel.app; the remaining work is content, not architecture.

**Does it show my work the way it needs to be shown?** Yes, and this is the deciding answer. Screenshot galleries per project ✓. Live demo links ✓. Repo links ✓. Long-form reading for the research paper ✓ — and for that last one I deliberately chose a *different* road (see below).

---

## My decision, and the honest complications

**I chose Road 3 for the portfolio** — React + Vite + Vercel serverless functions.

**Why not Road 1:** it can't show interactive work, and interactive AI work is the thing I'm proving. Rejecting it wasn't about ambition; it's that the simplest road fails constraint #4.

**Why not Road 2:** it's genuinely the option I'd recommend to most people, and I nearly took it. It loses on one specific thing: no secrets means no zeref-bot. A chatbot grounded in my own site, that a recruiter can interrogate at 2am, is worth the one file of maintenance it costs me.

**Can I maintain this?** Yes, with one caveat I want on the record: the `api/_index.json` vector index is a manual step, and a stale index is a silent failure — the bot keeps answering, just from old content. If I find myself forgetting to rebuild it, the right fix is to move that step into the build script so it can't be skipped, not to try harder to remember.

### The backend question, answered honestly

The expected answer here is "not yet," and for most portfolios it's correct. **Mine is "yes"** — but the smallest possible yes: stateless functions, no database, no persistent server, no auth. I'm not running infrastructure; I'm running one function that holds a key.

### The constraint I'm technically breaking

"Free only" doesn't fully survive contact with my choice. Vercel Hobby is free and GitHub Pages is free, but **zeref-bot calls Azure OpenAI, and tokens cost money.** It's small, and the per-IP rate limit and short replies keep it small, but I'd be lying if I called this stack strictly free. Two things make me accept it: the spend is capped by my own rate limiting rather than open-ended, and the feature it buys is the single strongest piece of evidence on the site. If the cost ever became a problem, the honest fallback is Road 2 — drop the bot, keep everything else, lose nothing structural.

### One decision I made *differently* on purpose

My capstone research paper is **not** on Road 3. It's plain static HTML on GitHub Pages (Road 1), live at zeref538.github.io/flyrank-ml-internship. That was deliberate: a research paper is long-form reading with charts and zero interactivity, it needs to still resolve years from now, and it belongs in the same repo as the notebooks it cites so the paper and its evidence can't drift apart. Road 1's weaknesses — no interactivity, no components — simply aren't costs for that job.

The real lesson from this exercise: "choose your stack" isn't one decision. I ended up with two stacks for two surfaces, each matched to what that surface actually has to do.
