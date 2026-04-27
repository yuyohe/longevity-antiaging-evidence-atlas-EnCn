# Codex Prompt — Feishu Publishing

Prepare a Feishu publishing package from the repository.

Task:

1. Read `docs/connect-feishu.md` and `config/feishu_field_mapping.json`.
2. Validate `data/evidence_matrix.csv`.
3. Generate/update Feishu Base records using `scripts/sync_feishu_bitable.py`.
4. Prepare Markdown pages under `build/feishu-docs/`:
   - Homepage
   - Evidence ranking
   - Topic pages
   - Monthly update
5. Do not publish drug recommendations without medical-supervision warnings.
6. Report missing environment variables instead of guessing.
