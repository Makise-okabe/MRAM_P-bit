# Verified raw scientific result archives

Executable freeze: `d217ab54fc41a3a84d6a500f3ab0f3aa433059dd`.

This directory contains 12 generated-graph archives (two families, fixed
12-index ranges) and one archive for all six official anchors. Each graph
bundle contains exactly `records.jsonl.gz`, `fidelity.jsonl.gz`,
`representation_metrics.json` and `manifest.json`. Files retain their exact
original bytes and their paths relative to `results/fyp_ideal_20261120`.
Scientific arrays are not regenerated during packaging. Timings, operational
logs, analysis outputs and original graph source files are excluded.

`archive_registry.json` records every archive SHA256/size, each member path,
SHA256/size, and all registered campaign counts. Its 88,320 trajectory records
include 768 immutable first-block records, so 87,552 trajectories are new.
There are 150 graph bundles, 239,616 common-state fidelity rows and 600 archived
files. Per-bundle payload hashes are checked against each COMPLETE bundle
manifest; the registry separately hashes the exact manifest bytes.

The packaging gate requires all 150 registered bundles, exact manifest counts,
one executable freeze and no IN_PROGRESS/FAILED markers. The campaign's full
`--verify-all` gate remains the prerequisite for packaging. Packaging verifies
bytes and metadata, not scientific quality or the statistical conclusions.

## Safe verification and extraction

Use the registry from the trusted result commit. Verify the 13 archive hashes,
all 600 member hashes, sorted exact member names and regular-file types before
extracting. The script's verification-only mode does not require the original
unpacked graph bundles:

```bash
python results/fyp_ideal_20261120/operational/archive.py \
  --freeze-commit d217ab54fc41a3a84d6a500f3ab0f3aa433059dd --verify-only
```

After successful verification, extract into a fresh directory. The keep-old
option prevents silently replacing existing files:

```bash
mkdir -p recovered_fyp_ideal
for archive in results/fyp_ideal_20261120/raw_archives/*.tar.gz; do
  tar --extract --gzip --file "$archive" --directory recovered_fyp_ideal \
    --keep-old-files --no-same-owner --no-same-permissions
done
```

The verifier rejects unexpected member paths, directory traversal, links,
duplicate members and extra archives. Archived members have mode 0644,
UID/GID/mtime 0 and empty owner names. USTAR ordering is fixed and gzip omits
an original filename and has mtime 0. Original official `_6666` graph files
and their acquisition provenance are committed separately, not hidden inside
these scientific-result archives.
