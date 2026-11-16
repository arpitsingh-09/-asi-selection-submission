import json, re, subprocess, hashlib, os
from collections import Counter

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)
def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()
def read(path):
    return open(path).read() if os.path.exists(path) else ""

out = []
def chk(name, ok, detail="", warn=False):
    out.append(("PASS" if ok else ("WARN" if warn else "FAIL"), name, detail))

# 1. deliverables
for f in ["E1/contrast.jsonl", "E1/eval_contrast.py", "E1/eval_contrast_v2.py",
          "E1/results_v2/report.md", "E1/results_v2/embedding_summary.json"]:
    chk(f"exists: {f}", os.path.exists(f))

# 2. dataset validator
v = sh("python E1/validate_all.py").stdout
chk("validator says READY", "READY FOR EVALUATION: YES" in v, v.strip().splitlines()[-1] if v.strip() else "no output")

# 3. freeze hash and no edits since the freeze commit
prereg = read("PREREG.md")
m = re.findall(r"contrast\.jsonl frozen[^\n]*SHA-256:\s*([0-9a-f]{64})", prereg)
cur = sha("E1/contrast.jsonl")
chk("contrast.jsonl hash equals the frozen hash in PREREG", bool(m) and m[-1] == cur,
    f"file {cur[:12]}..., PREREG {m[-1][:12] + '...' if m else 'none found'}")
fc = sh('git log --format=%h -1 --grep="dataset frozen"').stdout.strip()
if fc:
    chk(f"no changes to contrast.jsonl since freeze commit {fc}",
        sh(f"git diff --quiet {fc} -- E1/contrast.jsonl").returncode == 0)

# 4. held-out test file untouched
if os.path.exists("E1/test_item.jsonl"):
    chk("test_item.jsonl hash is recorded in PREREG", sha("E1/test_item.jsonl") in prereg)

# 5. results were produced on all 61 items
try:
    s = json.load(open("E1/results_v2/embedding_summary.json"))
    ns = {k: r.get("n") for k, r in s.items()}
    chk("all models evaluated on every item", all(n == 61 for n in ns.values()), str(ns))
except Exception as e:
    chk("embedding_summary.json readable", False, str(e))

# 6. report content that Tasks 2 to 4 require
rep = read("E1/results_v2/report.md").lower()
for label, kw in [("Task 3 (prediction comparison)", "task 3"), ("Task 4 (deduplication)", "task 4"),
                  ("length-only baseline", "length-only"), ("confidence intervals", "ci95"),
                  ("scope 'not measurable' for unit-norm models", "not measurable"),
                  ("threshold-free AUROC", "auroc"),
                  ("cross-encoder limitation documented", "instruction-following")]:
    chk(f"report mentions: {label}", kw in rep, warn=True)

# 7. placeholders and blanks in files I can still fix
for f in ["AI_LOG.md", "NOTEBOOK.md", "README.md"]:
    bad = [i + 1 for i, l in enumerate(read(f).splitlines()) if re.search(r"______|TODO|<date>|<describe>|NN%|XX%", l)]
    chk(f"no placeholders in {f}", not bad, f"lines {bad[:8]}" if bad else "", warn=True)
# Historical placeholders may remain in an append-only record, but their
# meaning must be explicitly explained in a later entry.
prereg_lines = prereg.splitlines()
hist = [
    i + 1 for i, line in enumerate(prereg_lines)
    if re.search(r"NN%|XX%|<date>|<describe>|<[^>]*from[^>]*>", line)
]
entry0_declared = (
    "Entry 0 remains an incomplete historical template" in prereg
    and prereg.find("Entry 0 remains an incomplete historical template")
        > prereg.find("## Entry 0 - <date>")
)
prediction_declared = (
    "No numeric E1 prediction was recorded before the evaluation ran" in prereg
    and prereg.find("No numeric E1 prediction was recorded before the evaluation ran")
        > prereg.find("My number: XX%")
)
v2_declared = (
    "## Entry 6 - 2026-10-22 (fills the placeholder in Entry 5)" in prereg
    and "v2 changes from v1: the v1 scope metric" in prereg
    and prereg.find("v2 changes from v1: the v1 scope metric")
        > prereg.find("v2 changes from v1: <describe>")
)
hist_declared = entry0_declared and prediction_declared and v2_declared
chk(
    "PREREG historical placeholders explicitly declared in later entries",
    not hist or hist_declared,
    f"historical matches at lines {hist}; declarations verified: {hist_declared}",
    warn=True,
)

# 8. author tags
rows = [json.loads(l) for l in open("E1/contrast.jsonl")]
a = Counter(r["author"] for r in rows)
ai_log = read("AI_LOG.md")
xx_disclosed = (
    "Items tagged XX (9 items" in ai_log
    and "author confirmation is required" in ai_log
)
chk(
    "unresolved author tags disclosed in AI_LOG.md",
    "XX" not in a or xx_disclosed,
    f"author counts: {dict(a)}; unresolved XX tags disclosed: {xx_disclosed}",
    warn=True,
)

# 9. 24-hour re-read recorded
nb = read("NOTEBOOK.md").lower()
chk("NOTEBOOK records a re-read after the items were written", "re-read" in nb and ("2026-10-22" in nb or "2026-10-23" in nb),
    "the last item (h062) was committed 2026-10-21 21:11, so the re-read must be after 2026-10-22 21:11", warn=True)

# 10. AI log has the required AI-error line
al = read("AI_LOG.md").lower()
chk("AI_LOG mentions at least one AI error caught", "error" in al or "wrong" in al or "mistake" in al, warn=True)

# 11. repo hygiene
chk("git working tree clean", sh("git status --short").stdout.strip() == "", sh("git status --short").stdout.strip()[:200])
sec = sh(r'git grep -nEi "(api[_-]?key|token|secret)\s*[=:]\s*[\"'"'"'][A-Za-z0-9_\-]{16,}"').stdout.strip()
chk("no secrets in tracked files", sec == "", sec[:200])

for status, name, detail in out:
    print(f"[{status}] {name}" + (f"   ({detail})" if detail else ""))
print("\nFAIL:", sum(s == "FAIL" for s, *_ in out), " WARN:", sum(s == "WARN" for s, *_ in out),
      " PASS:", sum(s == "PASS" for s, *_ in out))
