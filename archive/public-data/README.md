# Historical Public Data Archives / 历史公开数据归档

To keep the repository usable, the current and previous monthly CSV snapshots remain unpacked under `public-data/`. Older or superseded same-month five-table snapshots are stored here as verified ZIP archives.

为控制仓库体量，当前月和上一月的五张 CSV 保持展开；更早快照或同月被替代的完整快照压缩到这里。`public-data-2026-08-mid.zip` 保存 8 月中期发布的五张原始 CSV。

Each ZIP contains:

- the five original CSV files without data conversion;
- `MANIFEST.csv` with row count, byte count, and SHA-256 for every CSV;
- deterministic filenames and timestamps for reproducible builds.

`SHA256SUMS.txt` verifies the ZIP files themselves. Run the following command to rebuild or verify the archive:

```powershell
python scripts/archive_public_snapshots.py 2026-05 2026-06 --delete-source
```

When preserving a superseded release from the same month, use an explicit label:

```powershell
python scripts/archive_public_snapshots.py 2026-08 --archive-label 2026-08-mid
```

Retention policy / 保留规则: [`docs/data-retention-and-curation-policy.md`](../../docs/data-retention-and-curation-policy.md)
