import json, re
from collections import Counter

def toks(s): return re.findall(r"[a-z0-9\-']+", s.lower())
def jac(a, b):
    A, B = set(toks(a)), set(toks(b)); return len(A & B) / len(A | B) if A | B else 0
def keep(a, b):
    A = toks(a); B = set(toks(b)); return sum(w in B for w in A) / len(A) if A else 0

TYPES = ["inquiry_change", "role_swap", "direction_flip", "constraint_flip", "goal_swap"]
FIELDS = ["id", "source_arxiv", "A", "B", "B_min", "C", "C_type", "C_tilde",
          "narrower", "broader", "length_flipped", "author", "second_reader_agrees"]
rows, problems = [], []
for n, line in enumerate(open("E1/contrast.jsonl"), 1):
    try:
        rows.append(json.loads(line))
    except Exception as e:
        problems.append(f"line {n}: not valid JSON ({e})")

ids = [r.get("id") for r in rows]
for r in rows:
    i = r.get("id", "?")
    for f in FIELDS:
        if f not in r: problems.append(f"{i}: missing field {f}")
    if any(f not in r for f in FIELDS): continue
    if not re.fullmatch(r"\d{4}\.\d{4,5}", r["source_arxiv"]):
        problems.append(f"{i}: source_arxiv is not a bare ID: {r['source_arxiv']!r}")
    elif r["source_arxiv"][:2] not in ("25", "26"):
        problems.append(f"{i}: paper is before 2025: {r['source_arxiv']}")
    if r["C_type"] not in TYPES: problems.append(f"{i}: bad C_type {r['C_type']!r}")
    if jac(r["A"], r["B"]) > 0.3: problems.append(f"{i}: Jaccard(A,B)={jac(r['A'], r['B']):.2f} > 0.3")
    if keep(r["A"], r["B_min"]) < 0.75: problems.append(f"{i}: B_min keeps {keep(r['A'], r['B_min']):.0%} < 75%")
    if jac(r["A"], r["C_tilde"]) > 0.3: problems.append(f"{i}: Jaccard(A,C~)={jac(r['A'], r['C_tilde']):.2f} > 0.3")
    if r["B_min"].strip() == r["A"].strip(): problems.append(f"{i}: B_min is identical to A")
    for x, y in [("C", "A"), ("B", "A"), ("C_tilde", "C"), ("narrower", "A"), ("broader", "A")]:
        if r[x].strip() == r[y].strip(): problems.append(f"{i}: {x} is identical to {y}")
    flip = len(toks(r["broader"])) > len(toks(r["narrower"]))
    if bool(r["length_flipped"]) != flip:
        problems.append(f"{i}: length_flipped={r['length_flipped']} but should be {flip}")
    for f in ["A", "B", "B_min", "C", "C_tilde", "narrower", "broader"]:
        t = r[f].strip()
        if not t.endswith("?"): problems.append(f"{i}: {f} does not end with '?'")
        if re.search(r"TODO|XXX|\[|\]|HOT\b|\"", t): problems.append(f"{i}: {f} has a placeholder, bracket or stray quote")

c = Counter(r["C_type"] for r in rows if "C_type" in r)
flipped = sum(bool(r.get("length_flipped")) for r in rows)
print("items:", len(rows), "/ 60")
print("missing ids:", [x for x in ["h%03d" % i for i in range(1, len(rows) + 1)] if x not in ids] or "none")
print("duplicate ids:", {x for x in ids if ids.count(x) > 1} or "none")
dupA = [a for a, k in Counter(r["A"] for r in rows if "A" in r).items() if k > 1]
print("duplicate A questions:", dupA or "none")
for t in TYPES: print(f"  {t:16s} {c[t]:2d} / 10", "" if c[t] >= 10 else f"  <-- need {10 - c[t]} more")
print("broader longer than narrower:", flipped, "(need >=10)")
print("broader NOT longer:", len(rows) - flipped, "(aim for 20+)")
srcs = Counter(r["source_arxiv"] for r in rows if "source_arxiv" in r)
print("papers used more than once:", {k: v for k, v in srcs.items() if v > 1} or "none")
print("\nPROBLEMS:", len(problems))
for p in problems: print(" -", p)
ok = len(rows) >= 60 and all(c[t] >= 10 for t in TYPES) and flipped >= 10 and not problems
print("\nREADY FOR EVALUATION:", "YES" if ok else "NO")
