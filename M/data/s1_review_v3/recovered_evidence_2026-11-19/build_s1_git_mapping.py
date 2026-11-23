"""Reproduce the blocked S1 mapping from retained records and local Git objects."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path.home() / "asi-selection"
CONDITIONS = ("original", "empty", "cross_instance_shuffled", "same_topic_unsupported_decoy")


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def rows(name):
    with (HERE / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def mapping():
    versions = rows("E1_FIRST_COMMITTED_QUESTION_VERSIONS.csv")
    history = {r["question_id"]: r for r in rows("E1_QUESTION_HISTORY.csv")}
    controls = rows("E1_S1_CONTROLS.csv")
    slots = {(r["question_id"], r["condition"]): r for r in controls}
    expected = {(q, c) for q in history for c in CONDITIONS}
    if len(controls) != 244 or set(slots) != expected:
        raise ValueError("Condition inventory coverage mismatch")
    notes = (HERE / "E1_item_phase_notebook.md").read_bytes()
    if notes != git("show", "3f246af51a3620e94c8ec62c32cfe603542801d5:NOTEBOOK.md"):
        raise ValueError("Notebook differs from committed snapshot")
    output = []
    for v in sorted(versions, key=lambda row: row["question_id"]):
        q = v["question_id"]
        commit = v["first_observed_commit_sha"]
        path = v["git_file_path"]
        raw = git("show", f"{commit}:{path}").splitlines(keepends=True)[int(v["record_line_at_commit"]) - 1]
        item = json.loads(raw)
        dates = git("show", "-s", "--format=%aI%n%cI", commit).decode().splitlines()
        wording = json.loads(history[q]["exact_question_text"])
        if (item["id"] != q or hashlib.sha256(raw).hexdigest() != v["record_sha256"]
                or any(item[k] != value for k, value in wording.items())
                or dates != [v["commit_author_timestamp_metadata"], v["commit_committer_timestamp_metadata"]]):
            raise ValueError(f"{q}: version evidence mismatch")
        conditions = {}
        for condition in CONDITIONS:
            slot = slots[q, condition]
            if slot["evidence_status"] != "MISSING" or any(slot[k] for k in slot if k not in {"condition","question_id","evidence_status"}):
                raise ValueError(f"{q}: new condition evidence requires review before revising blocked snapshot")
            conditions[condition] = {"status": "BLOCKED", "source_binding": None}
        conditions["empty"]["registered_input_definition"] = []
        conditions["same_topic_unsupported_decoy"]["input_rule"] = "reuse original inputs with distinct independently verified same-topic question"
        output.append(dict(question_id=q, commit=commit, git_path=path, record_line=int(v["record_line_at_commit"]),
                           git_author_time=dates[0], git_committer_time=dates[1], record_sha256=v["record_sha256"],
                           wording=wording, associated_arxiv=item["source_arxiv"], author_code=item["author"],
                           notebook_lines=[i for i,line in enumerate(notes.decode().splitlines(),1) if re.search(r"\b"+q+r"\b",line)],
                           conditions=conditions))
    if len(output) != 61 or {r["question_id"] for r in output} != set(history):
        raise ValueError("Question coverage mismatch")
    return output


if __name__ == "__main__":
    print("\n".join(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in mapping()))
