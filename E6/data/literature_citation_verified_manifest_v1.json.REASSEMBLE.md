# Reassemble oversized evidence manifest

The original 111,304,260-byte file was split to comply with GitHub's ordinary 100 MB per-file limit. Concatenate `part-01.bin`, `part-02.bin`, and `part-03.bin` in order from `E6/data/literature_citation_verified_manifest_v1.json.chunks/`. Verify the resulting SHA-256 and byte count using `PROVENANCE/original-git-history.json`. The original checkout still contains the complete file.
