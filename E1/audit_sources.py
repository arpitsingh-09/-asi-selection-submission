import csv
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

DATASET = Path("E1/contrast.jsonl")
OUTPUT = Path("E1/results_v2/source_metadata.csv")

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

rows = [
    json.loads(line)
    for line in DATASET.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

ids = [str(row.get("source_arxiv", "")).strip() for row in rows]
unique_ids = list(dict.fromkeys(x for x in ids if x))

metadata = {}

# Query the official arXiv API in small batches.
for start in range(0, len(unique_ids), 10):
    batch = unique_ids[start:start + 10]
    query = urllib.parse.urlencode({"id_list": ",".join(batch)})
    url = "https://export.arxiv.org/api/query?" + query
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ASI-Lab-Assignment-Source-Audit/1.0"},
    )

    print(f"Querying official arXiv metadata: {start + 1}-{start + len(batch)} of {len(unique_ids)}")

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            root = ET.fromstring(response.read())

        for entry in root.findall("atom:entry", NS):
            raw_id = entry.findtext("atom:id", default="", namespaces=NS)
            arxiv_id = raw_id.rstrip("/").split("/")[-1]
            arxiv_id = arxiv_id.split("v")[0]

            title = " ".join(
                entry.findtext("atom:title", default="", namespaces=NS).split()
            )
            abstract = " ".join(
                entry.findtext("atom:summary", default="", namespaces=NS).split()
            )
            published = entry.findtext(
                "atom:published", default="", namespaces=NS
            )
            updated = entry.findtext(
                "atom:updated", default="", namespaces=NS
            )
            authors = [
                a.findtext("atom:name", default="", namespaces=NS)
                for a in entry.findall("atom:author", NS)
            ]
            categories = [
                c.attrib.get("term", "")
                for c in entry.findall("atom:category", NS)
            ]

            metadata[arxiv_id] = {
                "paper_title": title,
                "authors": "; ".join(authors),
                "first_posted_date": published[:10],
                "last_updated_date": updated[:10],
                "abstract": abstract,
                "categories": "; ".join(categories),
                "official_url": f"https://arxiv.org/abs/{arxiv_id}",
                "metadata_status": "FOUND",
            }

    except Exception as exc:
        print(f"Batch request failed: {type(exc).__name__}: {exc}")
        for arxiv_id in batch:
            metadata.setdefault(arxiv_id, {
                "metadata_status": "API_ERROR",
                "metadata_error": str(exc),
            })

    if start + 10 < len(unique_ids):
        time.sleep(3)

fields = [
    "item_id",
    "source_arxiv",
    "dataset_author",
    "C_type",
    "paper_title",
    "authors",
    "first_posted_date",
    "last_updated_date",
    "categories",
    "official_url",
    "metadata_status",
    "date_eligible_2025_onward",
    "abstract",
    "metadata_error",
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for row in rows:
        arxiv_id = str(row.get("source_arxiv", "")).strip()
        item = metadata.get(arxiv_id, {"metadata_status": "NOT_FOUND_IN_API_RESPONSE"})
        date = item.get("first_posted_date", "")

        writer.writerow({
            "item_id": row.get("id", ""),
            "source_arxiv": arxiv_id,
            "dataset_author": row.get("author", ""),
            "C_type": row.get("C_type", ""),
            **item,
            "date_eligible_2025_onward": (
                "YES" if date and date >= "2025-01-01"
                else "NO" if date
                else "UNVERIFIED"
            ),
        })

found = sum(
    metadata.get(x, {}).get("metadata_status") == "FOUND"
    for x in unique_ids
)
missing = [x for x in unique_ids if x not in metadata]
errors = [
    x for x in unique_ids
    if metadata.get(x, {}).get("metadata_status") == "API_ERROR"
]

print("\n========== SOURCE METADATA SUMMARY ==========")
print("Dataset records:", len(rows))
print("Unique source IDs:", len(unique_ids))
print("Metadata found:", found)
print("IDs absent from API response:", len(missing))
print("IDs with API errors:", len(errors))
print("Output:", OUTPUT)

if missing:
    print("IDs requiring follow-up:", ", ".join(missing))
if errors:
    print("IDs requiring retry:", ", ".join(errors))

print("\nMetadata retrieval is not yet semantic verification.")
print("The question text still needs to be compared with each paper.")
