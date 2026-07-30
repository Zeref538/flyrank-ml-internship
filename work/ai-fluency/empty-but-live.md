# Empty but Live — John Andrei Martinez

## The live URLs

**New this week — my capstone research paper page:**
> **https://zeref538.github.io/flyrank-ml-internship/**

Near-blank on purpose: it has the title, my name, and the eight section headings the finished paper will fill, and nothing else. Next week I'm filling a page that already exists instead of starting from zero.

**Already live — my portfolio (the stack from the earlier assignment):**
> **https://johnandrei.vercel.app**

## The stack, and why two URLs

My chosen stack from the sitemap assignment was React + Vite on Vercel, and that portfolio is already live — so "get from nothing to a URL" was a milestone I'd already passed there. Rather than ship a throwaway blank page just to tick the box, I applied this assignment to the thing that genuinely didn't have a URL yet: **my ML capstone research paper**, which the internship requires to be deployed and recorded in `submission/paper_url.txt`.

So this week's empty-but-live page is plain static HTML on **GitHub Pages**, served from the `docs/` folder of my existing internship repo. Reasons that beat spinning up another host:

- No new accounts, no new deploy pipeline — Pages builds straight off `main`.
- It lives in the same repo as the notebooks the paper cites, so the paper and its evidence can never drift apart.
- The capstone needs exactly one public URL in `submission/paper_url.txt`, and that file now holds this one.

## Proof it's really live

Confirmed reachable on a second device (opened on my phone over mobile data, not just my laptop) — screenshot attached alongside this document.

## Identity kit applied, not invented

The page already uses the identity kit I documented in Week 3, so the build week has nothing to re-decide:

- **Fonts:** Sora (headings) / Inter (body)
- **Background** `#07090d`, **text** `#e6edf3`, **accent** `#8b5cf6` used only on the tag, list numerals, and links
- Same quiet dark-mode engineering mood as the portfolio, so the two pages read as one person's work

## Loaded into my Claude Project for build week

- **Identity kit** — `work/ai-fluency/identity-kit.md` (fonts, hex codes, style note)
- **Framed case studies** — `work/ai-fluency/framed-cases.md` (FlyRank, ACRA, Aegix in three beats)
- **Content map** — `work/ai-fluency/through-line.md` (one-line claim, pages → sections → CTAs, gather-list)

All three are in the repo the page is served from, so they're one link away rather than pasted copies that go stale.

## Still to do next week

Fill the eight sections with the real capstone content. The ML results that go in them already exist (baseline rule vs. models under client-holdout, from `work/notebooks/`), so this is a writing-and-charting job, not a research job.
