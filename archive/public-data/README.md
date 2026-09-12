# Historical Public Data Archives / 历史公开数据归档

To keep the repository usable, the current and previous monthly CSV snapshots remain unpacked under `public-data/`. Older or superseded same-month five-table snapshots are stored here as verified ZIP archives.

为控制仓库体量，当前月和上一月的五张 CSV 保持展开；更早快照或同月被替代的完整快照压缩到这里。当前归档包括 5 月、6 月、7 月、8 月中期和 8 月底五表快照。

Each ZIP contains:

- the five original CSV files without data conversion;
- `MANIFEST.csv` with row count, byte count, and SHA-256 for every CSV;
- deterministic filenames and timestamps for reproducible builds.

`SHA256SUMS.txt` verifies the ZIP files themselves. Run the following command to rebuild or verify the archive:

```powershell
python -X utf8 scripts/archive_public_snapshots.py 2026-07 --archive-label 2026-07 --delete-source
```

When preserving a superseded release from the same month, use an explicit label:

```powershell
python -X utf8 scripts/archive_public_snapshots.py 2026-08 --archive-label 2026-08-end
```

Retention policy / 保留规则: [`docs/data-retention-and-curation-policy.md`](../../docs/data-retention-and-curation-policy.md)
