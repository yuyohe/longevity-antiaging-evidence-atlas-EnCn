# Project Handoff Log / 项目交接记录

Last updated / 最后更新：2026-04-29

This file is the local continuity record for future Codex threads and human maintainers. It records what has been built, how work is run, how GitHub and Feishu are synchronized, and where credentials are stored. Do not put real secrets in this file.

本文档是本地交接记录，供后续 Codex 线程和人工维护者快速接手。这里记录已经完成的工作、执行流程、GitHub/飞书同步方式，以及凭据文件位置。不要把真实密钥写入本文档。

## Project Identity

- GitHub repo: `https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn.git`
- Local repo path: `D:\longevity\longevity-antiaging-evidence-atlas-EnCn`
- Public Chinese name: `长寿抗衰与健康寿命证据图谱`
- Repository name: `longevity-antiaging-evidence-atlas-EnCn`
- Language policy: bilingual Chinese + English. Public interpretation should be Chinese-first, with English metadata and English summaries retained.
- Publication policy: GitHub is the source of truth; Feishu is the structured display, review, and collaboration layer.

## Credential And Token Locations

Do not commit real secrets. Current known credential locations:

- Feishu app ID / app secret source file provided by user: `D:\longevity\feishu-byYul.txt`
- Repo runtime env file: `D:\longevity\longevity-antiaging-evidence-atlas-EnCn\.env`
- Safe template: `D:\longevity\longevity-antiaging-evidence-atlas-EnCn\.env.example`

Current `.env` is expected to contain these variable names:

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_BITABLE_APP_TOKEN`
- `FEISHU_BITABLE_WIKI_NODE_TOKEN` if resolving from wiki node is needed
- `FEISHU_SOURCE_TABLE_ID`
- `FEISHU_CANDIDATE_TABLE_ID`
- `FEISHU_TOPIC_TABLE_ID`
- `FEISHU_PUBLISH_LOG_TABLE_ID`

Security rule: never paste the actual app secret, tenant token, GitHub token, or Feishu token into Markdown, CSV, Git commit messages, issue comments, or public docs.

## Feishu Base And Table Map

Known Feishu wiki/base:

- Wiki/base node token: `WriBw4TXZiOsjQkJWk8ctL1xnVg`
- Bitable app token is stored in `.env` as `FEISHU_BITABLE_APP_TOKEN`. Do not copy the real value into committed files.

Known table IDs:

- `文献总表`: `tblYryTL08h4jE53`
- `候选文献`: `tblBYXg91Wiw1BJl`
- `主题库`: `tblAkCgeJ2U9UURD`
- `发布日志`: `tbl7a9f81YjvJpwk`
- `对外总览`: `tblFsXTD5yqnJTFH`
- `外观抗老总览`: `tbl9vcaOrwjPcWZt`
- `补剂证据矩阵`: `tblAfXqX6qHqpSKb`
- `方法学与评分说明`: `tbl96mwWn085quRA`

Useful Feishu links:

- 对外总览: `https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblFsXTD5yqnJTFH`
- 外观抗老总览: `https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbl9vcaOrwjPcWZt`
- 补剂证据矩阵: `https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblAfXqX6qHqpSKb`
- 方法学与评分说明: `https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbl96mwWn085quRA`

## What Has Been Built

Main longevity evidence atlas:

- `data/candidate_sources.csv`: candidate source pool.
- `data/evidence_findings.csv`: 1800 healthspan/longevity findings with bilingual draft fields and v0.4/v0.5 scoring fields.
- `data/evidence_matrix.csv`: 900 formally selected/public matrix rows.
- `data/topics.csv`: 20 healthspan/longevity topics.
- `content/topics/`: 20 public topic pages.
- `content/papers/`: paper-card style public draft pages.
- `content/overview/public-summary.md`: the main public summary window.
- `content/overview/evidence-quality-dashboard.md`: v0.4 quality dashboard.
- `content/overview/evidence-scoring-v0-4.md`: public method and scoring explanation.

Skin and appearance aging atlas:

- `data/skin_beauty_findings.csv`: 160 skin/appearance aging candidate findings.
- `data/skin_beauty_summary.csv`: 8 skin topic summary records.
- `data/skin_beauty_topics.csv`: 8 skin topic definitions.
- `content/overview/skin-beauty-summary.md`: public skin/appearance aging overview.
- `content/skin-beauty-topics/`: 8 topic pages.

Supplement matrix:

- `data/supplement_matrix.csv`: 100 supplement/nutrition entries.
- `content/overview/supplement-summary.md`: public supplement matrix explanation.

Methodology:

- `data/methodology_scoring.csv`: previous methodology table.
- `data/scoring_policy_v0_4.csv`: current v0.4 scoring policy table.
- `scripts/apply_evidence_scoring_v04.py`: applies v0.4 scoring across healthspan findings, skin findings, supplement matrix, summaries, and public method pages.
- `scripts/expand_healthspan_pubmed_v05.py`: expands healthspan PubMed candidates using high-weight journal and high-design search tiers.
- `scripts/build_healthspan_outputs_v05.py`: rebuilds 1800 paper cards, 20 topic pages, 900 evidence matrix rows, public summary, status, and analysis outputs.
- `scripts/cleanup_feishu_evidence_matrix.py`: removes stale/duplicate Feishu evidence matrix records after schema changes.

## Current Scoring Framework

Current version: `v0.5_expanded_selection_plus_v0.4_scoring`.

The framework combines:

- GRADE-style public certainty framing.
- Cochrane RoB 2 for RCT full-text review.
- ROBINS-I for non-randomized/observational full-text review.
- AMSTAR 2 for systematic review/meta-analysis full-text review.
- NIH iCite Relative Citation Ratio where available.
- OpenAlex citation count where cached/available.
- Risk adjustments for abstract-only records, metadata-only records, soft endpoints, possible industry funding, and commercial overclaim risk.
- Confidence caps so animal/mechanistic/metadata-only/high-commercial-risk soft endpoint claims cannot become A solely because of study type.
- v0.5 topic-level confidence caps: early or highly translational topics such as rapamycin/mTOR, senolytics, NAD/NMN/NR, Klotho/IL-11, partial reprogramming, ITP mouse lifespan, autophagy/mitophagy, and microbiome/inflammaging are capped below A where appropriate, even if PubMed contains review-level records.

Important policy decisions:

- JCR Impact Factor is not currently auto-imported.
- Do not fabricate IF values.
- If JCR IF, CiteScore, or SJR are later imported from authorized/exported sources, they should be influence signals only; they should not override endpoint value, risk of bias, source depth, or GRADE-style certainty.
- Oral collagen was specifically downgraded under v0.4. It should not be presented as A. Current public framing: possible candidate signals for skin hydration/elasticity, but soft endpoints, heterogeneity, conflict risk, and commercial overclaim risk require caution.

## How Work Was Conducted

1. Created/expanded the healthspan evidence atlas from candidate sources.
2. Generated bilingual draft findings and topic pages.
3. Synced healthspan data to Feishu candidate, topic, evidence matrix, and public summary tables.
4. Added a separate skin/appearance aging atlas instead of mixing cosmetic endpoints into lifespan/healthspan.
5. Added a supplement evidence matrix with separate healthspan and skin/beauty evidence levels.
6. Rebuilt the scoring methodology after user challenged over-optimistic grades, especially oral collagen.
7. Added v0.4 scoring fields to CSVs and Feishu tables.
8. Added public method and quality dashboard pages.
9. Expanded healthspan/longevity findings from 600 to 1800 records using PubMed high-weight-journal/high-design search tiers.
10. Expanded candidate pool from 938 to 5983 records.
11. Rebuilt paper cards, topic pages, public summary, evidence matrix, and Feishu tables for the v0.5 expansion.

## Standard Local Commands

Run from `D:\longevity\longevity-antiaging-evidence-atlas-EnCn`.

Validation:

```powershell
python scripts\lint.py
python scripts\build_index.py
python scripts\validate_public_drafts.py
python scripts\validate_skin_beauty_public_drafts.py
python scripts\prepare_feishu_docs.py
```

Apply v0.4 scoring with cached bibliometrics only:

```powershell
python scripts\apply_evidence_scoring_v04.py
```

Expand healthspan findings to 1800:

```powershell
python scripts\expand_healthspan_pubmed_v05.py --target 1800 --retmax-per-topic-tier 150
python scripts\apply_evidence_scoring_v04.py
python scripts\build_healthspan_outputs_v05.py --matrix-limit 900
python scripts\apply_evidence_scoring_v04.py
```

Optionally fetch new external iCite/OpenAlex signals:

```powershell
$env:SCORING_FETCH_EXTERNAL='1'
python scripts\apply_evidence_scoring_v04.py
```

The external fetch mode can be slow. It writes caches under:

- `build/cache/icite_rcr_cache.json`
- `build/cache/openalex_work_cache.json`

## Standard Feishu Sync Commands

Run from repo root after loading `.env`.

```powershell
$env:FEISHU_PUBLIC_SUMMARY_TABLE_ID='tblFsXTD5yqnJTFH'
python scripts\sync_feishu_public_summary.py --delete-stale

python scripts\sync_feishu_csv_table.py --csv data/skin_beauty_summary.csv --table-name 外观抗老总览 --table-id tbl9vcaOrwjPcWZt --primary-key topic_id --primary-field 文本 --delete-stale

python scripts\sync_feishu_csv_table.py --csv data/supplement_matrix.csv --table-name 补剂证据矩阵 --table-id tblAfXqX6qHqpSKb --primary-key supplement_id --primary-field 文本 --delete-stale

python scripts\sync_feishu_csv_table.py --csv data/scoring_policy_v0_4.csv --table-name 方法学与评分说明 --table-id tbl96mwWn085quRA --primary-key rule_id --primary-field 文本

python scripts\sync_feishu_csv_table.py --csv data/evidence_matrix.csv --table-name 文献总表 --table-id tblYryTL08h4jE53 --primary-key paper_id --primary-field 文本

python scripts\sync_feishu_findings_to_candidates.py

python scripts\cleanup_feishu_evidence_matrix.py
```

After committing to GitHub, append publish log:

```powershell
python scripts\sync_feishu_publish_log.py
```

## Latest Sync Status Before This Handoff

Completed in the v0.5 expansion round:

- Candidate pool: 5983 records.
- Healthspan findings: 1800 records, 90 per topic.
- Evidence matrix: 900 records.
- Paper cards: 1800 Markdown pages.
- Topic pages: 20 Markdown pages.
- Feishu `候选文献`: all 5983 candidate records present; 1800 finding/scoring records updated.
- Feishu `文献总表`: 900 current records retained after deleting 300 stale legacy records.
- Feishu `对外总览`: 20 rows updated.
- Feishu `主题库`: 20 rows updated.
- Feishu `外观抗老总览`: 8 rows updated.
- Feishu `补剂证据矩阵`: 100 rows updated.
- Feishu `方法学与评分说明`: 11 rows updated.
- Local validation passed:
  - `python scripts\lint.py`
  - `python scripts\build_index.py`
  - `python scripts\validate_public_drafts.py`
  - `python scripts\validate_skin_beauty_public_drafts.py`
  - `python scripts\prepare_feishu_docs.py`

## Public Summary Window

Primary GitHub public window:

- `content/overview/public-summary.md`

Supporting public windows:

- `content/overview/evidence-quality-dashboard.md`
- `content/overview/evidence-scoring-v0-4.md`
- `content/overview/skin-beauty-summary.md`
- `content/overview/supplement-summary.md`

Current dashboard summary after v0.5:

- Healthspan/longevity findings: 1800 records.
- Skin/appearance findings: 160 records.
- Supplement/nutrition matrix: 100 entries.
- Oral collagen: no longer A; public framing is cautious and downgraded.
- Healthspan public topic levels after caps: A=8 topics, B=5 topics, C=5 topics, D=2 topics.

## Operating Rules For Future Threads

- Always read this file first.
- Do not ask the user for repeated manual Feishu operations unless API permission is actually blocked.
- Keep GitHub as source of truth, then sync Feishu from GitHub CSVs.
- Public pages must include draft and medical-disclaimer language.
- Do not give dose, prescription, brand, or purchase recommendations.
- Do not convert animal, cell, biomarker, skin hydration, or epigenetic-clock findings into human longevity claims.
- Update this handoff log after each major batch of work, especially when changing table IDs, token locations, scoring rules, or sync commands.
