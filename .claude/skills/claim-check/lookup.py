"""Find where a number actually comes from.

Grep can't do this job: a draft says "13,562" or "0.88" and the source says
13562 or 0.880 or 0.8800000000000001. This normalizes both sides, then reports
every place the value appears -- and, separately, every place a value ROUNDS to
it, which is how a real claim usually relates to its source.

    python lookup.py 0.88
    python lookup.py 13562 --root .

Exit code is 0 whether or not anything is found. "Not found" is a finding, not
an error -- the agent needs to see it, not crash on it.
"""
import argparse, json, re, sys
from pathlib import Path

# A tool that quotes a source must not corrupt what it quotes. On a cp1252
# console every em-dash in a notebook came back as U+FFFD, which made clean
# files look mojibake'd -- the mangling was here, not in them.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Files worth searching. No CSVs, and this is not a performance decision: the
# first run searched work/outputs/*.csv and printed rows containing content_ and
# client_ pseudonyms, which is exactly what the repo rule forbids. It also matched
# "9999" inside the id content_9b6603da9999. Row-level data goes through
# recompute, never through search.
GLOBS = ("work/outputs/*.json", "work/notebooks/*.ipynb",
         "work/ai-fluency/*.md", "*.md", "work/*.md")
# The number must stand alone. Without the lookarounds, searching for 29 matched
# the "029" inside the pseudonym client_d029fa3a95, and 9999 matched
# content_9b6603da9999 -- noise, and it dragged ids into the output.
NUM = re.compile(r"(?<![A-Za-z0-9_.])-?\d[\d,]*\.?\d*(?![A-Za-z0-9_])")

# Belt and braces on the same problem: notebook outputs legitimately contain
# pseudonyms, so anything quoted from them gets masked before printing. The rule
# is that ids never reach the screen, not that they never appear in a file.
IDS = re.compile(r"\b(content|client)_[0-9a-fA-F]{6,}\b")


def norm(tok: str):
    try:
        return float(tok.replace(",", ""))
    except ValueError:
        return None


def decimals(tok: str) -> int:
    tok = tok.replace(",", "")
    return len(tok.split(".")[1]) if "." in tok else 0


def scan(path: Path, target: float, places: int):
    """Yield (relation, source_value, line_no, snippet) for one file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    # .ipynb: search only outputs and source, not the base64 image blobs
    if path.suffix == ".ipynb":
        try:
            nb = json.loads(text)
        except json.JSONDecodeError:
            return
        parts = []
        for cell in nb.get("cells", []):
            parts.append("".join(cell.get("source", [])))
            for out in cell.get("outputs", []):
                parts.append("".join(out.get("text", [])))
                parts.append("".join(out.get("data", {}).get("text/plain", [])))
        text = "\n".join(parts)

    for i, line in enumerate(text.splitlines(), 1):
        for tok in NUM.findall(line):
            val = norm(tok)
            if val is None:
                continue
            if val == target:
                rel = "EXACT"
            elif places and round(val, places) == target:
                # 0.551 rounds to 0.55 -- fine. It ALSO rounds to 0.6, which is
                # technically true and useless: one decimal place on a metric
                # hides the difference between 0.551 and 0.649. Flag it instead
                # of blessing it; the skill treats LOOSE as not-verified.
                rel = f"ROUNDS-TO{' LOOSE' if places < 2 else ''} (source is {tok})"
            else:
                continue
            snip = IDS.sub(r"\1_<redacted>", line.strip())
            yield rel, tok, i, (snip[:150] + "…" if len(snip) > 150 else snip)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("value", help="the number as it appears in the draft, e.g. 0.88 or 13,562")
    ap.add_argument("--root", default=".", help="repo root to search from")
    args = ap.parse_args()

    target = norm(args.value)
    if target is None:
        print(f"NOT-A-NUMBER: {args.value!r} — use grep for text claims")
        return 0
    places = decimals(args.value)
    root = Path(args.root).resolve()

    hits = []
    for g in GLOBS:
        for path in sorted(root.glob(g)):
            for rel, tok, ln, snip in scan(path, target, places):
                hits.append((rel, path.relative_to(root).as_posix(), ln, tok, snip))

    if not hits:
        print(f"NOT FOUND: {args.value} appears in no searched source.")
        print("  -> verdict UNVERIFIABLE unless you can recompute it from data/raw/.")
        return 0

    # one row per (file, line, relation) -- a line with two matching tokens was
    # printing three identical rows and made a single source look like three
    seen, uniq = set(), []
    for h in hits:
        key = (h[1], h[2], h[0])
        if key not in seen:
            seen.add(key)
            uniq.append(h)
    hits = uniq
    # exact matches first; they settle the claim without a rounding argument
    hits.sort(key=lambda h: (h[0] != "EXACT",))
    print(f"{len(hits)} source(s) for {args.value}:")
    for rel, f, ln, tok, snip in hits[:25]:
        print(f"  [{rel}] {f}:{ln}\n      {snip}")
    if len(hits) > 25:
        print(f"  … {len(hits) - 25} more")
    return 0


def _self_check():
    """The normalization is the whole point of this file, so it gets a check."""
    assert norm("13,562") == 13562.0
    assert norm("0.880") == 0.88
    assert norm("nope") is None
    assert decimals("0.55") == 2 and decimals("13,562") == 0
    # a bare number must not match inside an identifier
    assert NUM.findall("client_d029fa3a95") == []
    assert NUM.findall("P@50: 0.88,") == ["50", "0.88"]   # the 50 in P@50 is standalone
    assert NUM.findall("pos 10.6 vs") == ["10.6"]         # not ["10.6", "6"]
    assert IDS.sub(r"\1_<redacted>", "content_9cd88c77492f x") == "content_<redacted> x"
    # 0.551 rounds to 0.55 at 2 places -- and ALSO to 0.6 at 1 place, which is
    # why one-decimal matches are labelled LOOSE rather than accepted.
    assert round(0.551, 2) == 0.55
    assert round(0.551, 1) == 0.6
    print("lookup self-check ok")


if __name__ == "__main__":
    if "--self-check" in sys.argv:
        _self_check()
    else:
        try:
            sys.exit(main())
        except BrokenPipeError:
            sys.exit(0)   # piping into `head` is normal, not a failure
