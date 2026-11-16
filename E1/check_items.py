import json, re, sys
from collections import Counter

def toks(s):
    return re.findall(r"[a-z0-9\-']+", s.lower())

def jac(a, b):
    A, B = set(toks(a)), set(toks(b))
    return len(A & B) / len(A | B) if A | B else 0

def keep(a, b):
    A = toks(a)
    B = set(toks(b))
    return sum(w in B for w in A) / len(A)

items = [json.loads(l) for l in open(sys.argv[1])]
bad, types, wlonger = [], Counter(), 0
for it in items:
    errs = []
    if jac(it["A"], it["B"]) > 0.3:
        errs.append("Jaccard(A,B)>0.3")
    if keep(it["A"], it["B_min"]) < 0.75:
        errs.append("B_min keeps <75%")
    if jac(it["A"], it["C_tilde"]) > 0.3:
        errs.append("Jaccard(A,C~)>0.3")
    if len(toks(it["broader"])) > len(toks(it["narrower"])):
        wlonger += 1
    types[it["C_type"]] += 1
    if errs:
        bad.append((it["id"], errs))

print("items:", len(items), "| C types:", dict(types), "| W longer than N:", wlonger)
print("failures:", bad if bad else "none")
print("need: >=60 items, >=10 per type, >=10 with W longer than N")
