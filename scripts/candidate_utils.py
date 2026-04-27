"""Shared helpers for candidate literature collection."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Set

CANDIDATE_FIELDS = [
    "id",
    "title_en",
    "title_zh",
    "year",
    "doi",
    "pmid",
    "pmcid",
    "url",
    "source",
    "query",
    "include_status",
    "notes",
    "last_checked",
]


def ensure_csv_header(path: Path, fieldnames: List[str]) -> None:
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


def load_candidate_keys(path: Path) -> Dict[str, Set[str]]:
    keys: Dict[str, Set[str]] = {"id": set(), "doi": set(), "pmid": set(), "url": set()}
    ensure_csv_header(path, CANDIDATE_FIELDS)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            for key in keys:
                value = (row.get(key) or "").strip().lower()
                if value:
                    keys[key].add(value)
    return keys


def is_duplicate(row: Dict[str, str], keys: Dict[str, Set[str]]) -> bool:
    for key in ("id", "doi", "pmid", "url"):
        value = (row.get(key) or "").strip().lower()
        if value and value in keys[key]:
            return True
    return False


def remember(row: Dict[str, str], keys: Dict[str, Set[str]]) -> None:
    for key in keys:
        value = (row.get(key) or "").strip().lower()
        if value:
            keys[key].add(value)


def append_rows(path: Path, rows: Iterable[Dict[str, str]]) -> int:
    ensure_csv_header(path, CANDIDATE_FIELDS)
    count = 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANDIDATE_FIELDS)
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in CANDIDATE_FIELDS})
            count += 1
    return count
