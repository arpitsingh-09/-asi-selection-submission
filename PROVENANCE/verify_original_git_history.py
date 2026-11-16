"""Verify preserved source Git commit objects and the original M prereg blob."""
from __future__ import annotations
import base64, datetime, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prov=json.loads((ROOT/'PROVENANCE/original-git-history.json').read_text())
rows=[json.loads(line) for line in (ROOT/'PROVENANCE/original-git-objects.jsonl').read_text().splitlines() if line]
objects={(r['type'],r['oid']):base64.b64decode(r['payload_base64']) for r in rows}
def oid(kind,payload): return hashlib.sha1(kind.encode()+b' '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
def parse_headers(payload):
    return payload.split(b'\n\n',1)[0].splitlines()
def date_iso(line):
    _,epoch,zone=line.rsplit(b' ',2)
    sign=1 if zone[:1]==b'+' else -1
    minutes=sign*(int(zone[1:3])*60+int(zone[3:5]))
    dt=datetime.datetime.fromtimestamp(int(epoch),datetime.timezone(datetime.timedelta(minutes=minutes)))
    return dt.isoformat(timespec='seconds')
commit_map={r['commit']:r for r in prov['commits_newest_first']}
assert len(commit_map)==prov['original_commit_count'] and prov['commits_newest_first'][0]['commit']==prov['original_head']
for row in prov['commits_newest_first']:
    payload=objects[('commit',row['commit'])]
    assert oid('commit',payload)==row['commit']
    headers=parse_headers(payload)
    tree=next(x.split(b' ',1)[1].decode() for x in headers if x.startswith(b'tree '))
    parents=[x.split(b' ',1)[1].decode() for x in headers if x.startswith(b'parent ')]
    author=next(x for x in headers if x.startswith(b'author '))
    committer=next(x for x in headers if x.startswith(b'committer '))
    assert (tree,parents)==(row['tree'],row['parents'])
    assert date_iso(author)==row['author_date'] and date_iso(committer)==row['committer_date']
    assert all(parent in commit_map for parent in parents)
# Require the preserved object set to be exactly the ancestry reachable from original HEAD.
seen=set(); pending=[prov['original_head']]
while pending:
    current=pending.pop()
    if current in seen: continue
    seen.add(current)
    payload=objects[('commit',current)]
    pending.extend(x.split(b' ',1)[1].decode() for x in parse_headers(payload) if x.startswith(b'parent '))
assert seen==set(commit_map)
# Validate that the original commit tree named the exact submitted preregistration blob.
def entries(payload):
    result=[]; i=0
    while i<len(payload):
        j=payload.index(b' ',i); k=payload.index(b'\0',j+1)
        result.append((payload[i:j].decode(),payload[j+1:k].decode(),payload[k+1:k+21].hex())); i=k+21
    return result
pr=prov['main_problem_preregistration_history_newest_first'][0]
commit=objects[('commit',pr['commit'])]
root_tree=next(x.split(b' ',1)[1].decode() for x in parse_headers(commit) if x.startswith(b'tree '))
root_payload=objects[('tree',root_tree)]
assert oid('tree',root_payload)==root_tree==pr['tree']
m_tree=next(x[2] for x in entries(root_payload) if x[1]=='M' and x[0]=='40000')
m_payload=objects[('tree',m_tree)]
assert oid('tree',m_payload)==m_tree
blob=next(x[2] for x in entries(m_payload) if x[1]=='PREREG.md')
snap=prov['main_problem_preregistration_snapshot']
assert blob==pr['M_PREREG_blob']==snap['original_head_blob']
content=(ROOT/'M/PREREG.md').read_bytes()
assert hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()==blob
assert hashlib.sha256(content).hexdigest()==snap['snapshot_sha256']
print(f"Verified {len(commit_map)} original commit objects and parent links.")
print(f"Verified original M/PREREG.md blob {blob} at commit {pr['commit']}.")
print("Git-authored/committer dates are preserved in the self-hashed objects; this is not an external trusted timestamp.")
