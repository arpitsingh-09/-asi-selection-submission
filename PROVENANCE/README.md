# Original Main Problem preregistration history proof

`original-git-history.json` records the curated source history. `original-git-objects.jsonl` preserves the raw Git commit-object payloads from the original repository, plus the root/M tree payloads needed to bind the Main Problem preregistration to its original commit. These are the original objects: this package does not create commits, alter timestamps, include the oversized historical data blob, or change the source repository.

From the repository root, verify commit object IDs, author/committer dates, the complete parent chain, the original `M/PREREG.md` blob ID, and the current byte-identical snapshot with:

```sh
python3 -B PROVENANCE/verify_original_git_history.py
```

This makes the Git object contents and their self-reported dates independently hash-checkable. Git commit dates are not a trusted external timestamp; an independently timestamped remote/archive would be needed to establish when the objects were first published.
