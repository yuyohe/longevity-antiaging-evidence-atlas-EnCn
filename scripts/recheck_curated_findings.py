"""Reapply scope checks after inspection without repeating or resetting a search."""

from collections import Counter
import json

import curate_mid_august_2026 as curation


def main() -> None:
    root = curation.ROOT
    config = json.loads((root / "data/current_release.json").read_text(encoding="utf-8"))
    metrics_path = root / config["EVIDENCE_ATLAS_CURATION_METRICS"]
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if metrics["date"] != config["EVIDENCE_ATLAS_UPDATE_DATE"]:
        raise RuntimeError("Release dates differ")
    path = root / "data/evidence_findings.csv"
    rows = curation.read_csv(path)
    keep, rejected = [], []
    for row in rows:
        reason = curation.finding_rejection_reason(row)
        if reason:
            rejected.append(curation.finding_retirement(row, reason, metrics["date"]))
        else:
            keep.append(row)
    if not rejected:
        print("Scope recheck passed; no further retirements")
        return
    log_path = root / config["EVIDENCE_ATLAS_FINDING_RETIREMENT"]
    log = curation.read_csv(log_path) + rejected
    curation.write_csv(log_path, log, curation.csv_fields(log_path))
    curation.write_csv(path, keep, curation.csv_fields(path))
    metrics["after"]["finding_records"] = len(keep)
    recent_tag = config["EVIDENCE_ATLAS_RECENT_TAG"]
    recent_ids = {
        row["id"] for row in curation.read_csv(root / "data/candidate_sources.csv")
        if recent_tag in f"{row.get('query', '')} {row.get('notes', '')}"
    }
    metrics["after"]["recent_findings_retained"] = sum(row["candidate_id"] in recent_ids for row in keep)
    metrics["finding_topic_counts"] = dict(sorted(Counter(row["topic_id"] for row in keep).items()))
    metrics["retired"]["finding_decisions"] = len(log)
    metrics["retired"]["finding_reasons"] = curation.retirement_reason_counts(log)
    active = {row["candidate_id"] for row in keep}
    metrics["recent_selected_examples"] = [row for row in metrics["recent_selected_examples"] if row["candidate_id"] in active]
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Additional scope retirements: {len(rejected)}; active findings: {len(keep)}")


if __name__ == "__main__":
    main()
