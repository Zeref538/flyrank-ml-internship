# PF-04 — DNS Walkthrough

**John Andrei Martinez · General AI Fluency · Week 5**

**Live site:** https://johnandrei.vercel.app — Vercel free hobby tier, HTTPS automatic.

I checked it rather than assumed it:

```
$ curl -o /dev/null -w "status=%{http_code} scheme=%{scheme} tls=%{ssl_verify_result}\n" https://johnandrei.vercel.app
status=200 scheme=https tls=0
```

`tls=0` means the certificate verified with no errors. That's the padlock, from
the command line.

---

## What a CNAME record is

A **CNAME** is a signpost. It says *"this name is really that other name — go ask
about that one instead."*

An **A record** is different: it holds an actual IP address, the numeric street
address of a machine. A CNAME holds a *name*, and whoever looks it up has to do
one more lookup to finish the job.

Why that matters here: I don't own the machines my site sits on. Vercel does, and
their IP addresses can change whenever they want — they move servers, add
capacity, route you to whichever data centre is closest. Right now my site
answers on two of them:

```
$ nslookup johnandrei.vercel.app
Addresses:  64.29.17.67
            216.198.79.67
```

If I wrote `64.29.17.67` into an A record and Vercel retired that machine, my
site would go dark and I'd have no way to know why. A CNAME hands that problem
back to the people who can actually solve it. They change the IP behind the name;
my record never has to change.

**One limit worth knowing:** a CNAME can't sit on a bare domain like
`flyrank.ai` itself — the rules don't allow a CNAME to coexist with the other
records a root domain needs, like its mail records. It's fine on a subdomain, and
`johnandrei.flyrank.ai` is a subdomain, so this doesn't affect me.

## What my record will hold

| Field | Value |
|---|---|
| Type | `CNAME` |
| Name | `johnandrei` (inside the `flyrank.ai` zone) |
| Value | the hostname Vercel shows me when I add the domain — **currently `cname.vercel-dns.com`** |
| TTL | Auto / 300 seconds |

I'm writing the value as *"whatever Vercel's dashboard tells me"* rather than
hardcoding it in my head, because it's their hostname and they've changed it
before. The dashboard is the source of truth; this document is the checklist.

## What happens when someone types my address

Say a hiring manager types `johnandrei.flyrank.ai`. Nobody has visited it before,
so nothing is cached anywhere. Here's the whole chain.

**1. The browser checks itself.** It keeps a small cache of names it looked up
recently. Empty. Then the operating system's cache. Also empty.

**2. The OS asks the resolver.** A **resolver** is the service that does the
legwork of finding an answer. Mine is my own router:

```
Server:  globebroadband.net
Address: 192.168.254.254
```

which forwards to my ISP. The browser asks one question — *"what's the address
for johnandrei.flyrank.ai?"* — and waits. Everything below happens on the
resolver's side.

**3. The resolver asks the root.** It doesn't know `flyrank.ai`, so it starts at
the top. The **root servers** don't know either, but they know who handles `.ai`.
They answer: *"ask the `.ai` servers."*

**4. The resolver asks the `.ai` servers.** They don't know my site either. They
know who's authoritative for `flyrank.ai` and say so.

**5. The resolver asks FlyRank's nameservers.** A **nameserver** is the machine
that holds the real records for a domain. FlyRank's are on Cloudflare:

```
$ nslookup -type=NS flyrank.ai
flyrank.ai  nameserver = ram.ns.cloudflare.com
flyrank.ai  nameserver = sasha.ns.cloudflare.com
```

These are the ones that will actually contain my record once Ops creates it. Two
of them, so one can fail without taking the domain down.

**6. The record comes back — and it's a signpost, not an answer.** Cloudflare
replies with my CNAME: *"`johnandrei.flyrank.ai` is really
`cname.vercel-dns.com`."* No IP address yet.

**7. So the resolver goes again.** Same process for the new name — this time
ending at Vercel's nameservers (`ns1.vercel-dns-3.com` and friends), which return
real A records: `64.29.17.67`, `216.198.79.67`. **Now** there's an address.

**8. The browser connects, and asks for me by name.** It opens an HTTPS
connection to that IP and, as part of the handshake, states which hostname it
wants — `johnandrei.flyrank.ai`. This matters: thousands of sites share those IPs,
and that name is how Vercel knows which certificate and which site to serve.

**9. Certificate, then page.** Vercel presents the certificate it issued for my
domain. The browser checks it covers the name it asked for and hasn't expired,
shows the padlock, and only then requests the page. My site loads.

**10. Everyone remembers.** Each step gets cached for its TTL. With TTL at 300
seconds, the next visitor for the next five minutes skips steps 3–7 entirely.

That's also the honest answer to *"why isn't my domain working yet?"* — usually
nothing is broken. Some resolver somewhere is still holding an old answer until
its timer runs out. A short TTL when you're making changes means shorter waiting.

## Capstone-day checklist

Ops creates the DNS record. My half is the other end. In order:

1. **Vercel → project → Settings → Domains → add `johnandrei.flyrank.ai`.** Vercel
   then shows the exact CNAME value it wants. Send that to Ops — don't assume it
   matches what's written above.
2. **Wait for Ops to confirm the record exists** in the Cloudflare zone.
3. **Check it resolves from my machine, not from a website:**
   ```
   nslookup -type=CNAME johnandrei.flyrank.ai
   ```
   I want to see the Vercel hostname come back. If it doesn't, nothing downstream
   will work and there's no point looking at Vercel yet.
4. **One Cloudflare-specific thing to ask about:** Cloudflare can either just
   answer with my record (grey cloud, "DNS only") or sit in front of my site and
   proxy the traffic (orange cloud). If it's proxied, the lookup returns
   *Cloudflare's* IPs rather than Vercel's, and Vercel can have trouble issuing
   the certificate because it can't see the domain pointing at itself. So if the
   padlock won't appear, this is the first thing I ask Ops to check — and I'd know
   to ask because step 3 would show Cloudflare IPs instead of `64.29.*`.
5. **Wait for Vercel to say "Valid Configuration"** and issue the certificate.
   Automatic, usually minutes.
6. **Confirm the padlock the same way I did above:**
   ```
   curl -o /dev/null -w "status=%{http_code} tls=%{ssl_verify_result}\n" https://johnandrei.flyrank.ai
   ```
   `status=200 tls=0` and it's done.
7. **Open it logged out, in a private window, on my phone** — different network,
   different resolver, no cached anything.

The old URL keeps working. Both addresses point at the same deployment, because a
custom domain is a pointer, not a move. Nothing about my build changes — I don't
rebuild, redeploy, or edit a single file.

---

## Every file in the deployed site

The brief says I have to be able to explain what I deployed, so:

- **`index.html`** — the shell. One `<div id="root">` and one script tag. Vite
  injects the hashed asset filenames at build time.
- **`src/main.jsx`** — mounts `<App/>` into that div.
- **`src/App.jsx`** — the whole page. Reads the arrays out of `data.js` and maps
  over them, so every section is a loop over data rather than hand-written markup.
- **`src/data.js`** — all content, as plain arrays: `profile`, `experience`,
  `projects`, `skills`, `certifications`, `education`. Adding a project is adding
  an object here; nothing else changes.
- **`src/index.css`** — the design tokens from my identity kit
  (`--bg: #07090d`, `--accent: #8b5cf6`, Sora for headings, Inter for body) and
  every layout rule.
- **`src/components/`** — one file each: `Reveal` (fade in on scroll, via
  IntersectionObserver), `BorderGlow` (the glow that tracks the cursor along a
  card edge), `RotatingText` and `ScrollFloat` (GSAP), `ParticleField`, `Noise`
  (grain overlay), `Cursor`, `ChatWidget`, `ContactForm`, `StatusBar`.
- **`src/skillIcons.jsx`** — maps a skill or issuer name to its icon.
- **`api/`** — Vercel serverless functions. The chat endpoint embeds the visitor's
  question, scores it against `api/_index.json` by cosine similarity, and sends
  the closest chunks to the model as context. Retrieval, not a chatbot wrapper.
- **`scripts/build-index.mjs`** — builds that index from `data.js`,
  `knowledge/*.md`, and project READMEs. Run by hand, which is a known problem:
  a stale index answers confidently from old content.
- **`public/`** — `cv.pdf`, `favicon.svg`, project screenshots, cert badges.
  Served as-is at the site root.
- **`vite.config.js`** — the React plugin, plus a manual chunk split so React,
  GSAP, and Motion end up in separate long-cached files and editing my own code
  doesn't invalidate them.
- **`dist/`** — the build output Vercel actually serves. Generated, never edited.
