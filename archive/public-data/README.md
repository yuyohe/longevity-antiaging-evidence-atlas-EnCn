# Historical Public Data Archives / 历史公开数据归档

To keep the repository usable, the current and previous monthly CSV snapshots remain unpacked under `public-data/`. Older five-table snapshots are stored here as one ZIP per month.

为控制仓库体量，当前月和上一月的五张 CSV 保持展开；更早快照按月份压缩到这里。

Each ZIP contains:

- the five original CSV files without data conversion;
- `MANIFEST.csv` with row count, byte count, and SHA-256 for every CSV;
- deterministic filenames and timestamps for reproducible builds.

`SHA256SUMS.txt` verifies the ZIP files themselves. Run the following command to rebuild or verify the archive:

```powershell
python scripts/archive_public_snapshots.py 2026-05 2026-06 --delete-source
```

Retention policy / 保留规则: [`docs/data-retention-and-curation-policy.md`](../../docs/data-retention-and-curation-policy.md)
