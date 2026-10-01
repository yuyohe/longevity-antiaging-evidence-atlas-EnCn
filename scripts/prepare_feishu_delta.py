"""Compare structured public CSV snapshots and emit resumable primary-key lists."""

import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTH = os.environ["EVIDENCE_ATLAS_ASSET_MONTH"]
BASELINE = os.environ["EVIDENCE_ATLAS_BASELINE_MONTH"]


def indexed(path, key):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {row[key]: row for row in rows}
    if len(result) != len(rows) or "" in result:
        raise RuntimeError(f"Blank or duplicate primary keys in {path.name}")
    return result


def main():
    output = ROOT / "output" / f"feishu-delta-{MONTH}"
    output.mkdir(parents=True, exist_ok=True)
    summary = {}
    for asset, key in [("literature_library", "library_id"), ("candidate_sources", "id"),
                       ("shortlist_sources", "candidate_id"), ("evidence_findings", "finding_id"),
                       ("evidence_matrix", "paper_id")]:
        prefix = asset.replace("_", "-")
        before = indexed(ROOT / "public-data" / f"{prefix}-{BASELINE}.csv", key)
        after = indexed(ROOT / "public-data" / f"{prefix}-{MONTH}.csv", key)
        changed = sorted(k for k, row in after.items() if before.get(k) != row)
        (output / f"{asset}.txt").write_text("".join(k + "\n" for k in changed), encoding="utf-8")
        summary[asset] = {"before": len(before), "after": len(after), "changed_or_new": len(changed),
                          "old_removed": len(before.keys() - after.keys()), "new_active": len(after.keys() - before.keys())}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
