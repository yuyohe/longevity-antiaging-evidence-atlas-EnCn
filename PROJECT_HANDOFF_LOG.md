# Project Handoff Log / 项目交接记录

Last updated / 最后更新：2026-07-29

This file is the local continuity record for future Codex threads and human maintainers. It records what has been built, how work is run, how GitHub and Feishu are synchronized, and where credentials are stored. Do not put real secrets in this file.

本文档是本地交接记录，供后续 Codex 线程和人工维护者快速接手。这里记录已经完成的工作、执行流程、GitHub/飞书同步方式，以及凭据文件位置。不要把真实密钥写入本文档。

## Current Release Snapshot / 当前发布快照

The current public release supersedes the historical counts later in this log.

- Snapshot date: `2026-07-29`
- Publication repository: `D:\longevity\github-publish-2026-06-29`
- Development workspace: `D:\longevity\longevity-antiaging-evidence-atlas-EnCn` (may contain unrelated local work; do not use it as a clean release checkout)
- Candidate and literature records: `16,151`
- Shortlist and evidence findings: `6,000`
- Evidence matrix: `3,000`
- Public CSV processing rows: `47,302`
- Visual assets: `7` main PNGs plus `50` ingredient cards
- Feishu release layer: `9` active tables
- Plain-language release guide: `content/public-reader/end-july-2026-update.md`
- Self-contained visual report: `docs/end-july-public-update-2026-07.html`
- Self-contained posting dashboard: `docs/yulcell-posting-asset-dashboard-2026-07-29.html`
- Feishu table manifest: `data/feishu_live_tables_2026_07.csv`
- Feishu read-only audit report: `build/feishu_online_audit_2026_07.json`

The July 15-29 PubMed refresh added 427 deduplicated candidates. Of those, 161 entered the findings layer across 18 topics. Protocols are classified as `protocol_or_registered_plan` and capped at evidence level E. Editorials, corrections, and related non-primary records are classified as `non_primary_commentary_or_correction` and capped at E. Explicit animal subjects take precedence over randomized-design wording; uncertain designs remain `metadata_only_needs_classification`.

Current release validation:

```powershell
$env:EXPECTED_FINDINGS='6000'
$env:MIN_MATRIX_ROWS='3000'
$env:MAX_MATRIX_ROWS='3000'
python scripts\lint.py
python scripts\validate_public_drafts.py
python scripts\validate_skin_beauty_public_drafts.py
python scripts\validate_public_release_2026_07.py
```

Do not publish from the development workspace without first checking its worktree. For public releases, start from a clean clone or worktree that matches GitHub `main`, run the complete build chain, validate locally, then perform the read-only Feishu audit.

## Project Identity

- GitHub repo: `https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn.git`
- Publication repo path: `D:\longevity\github-publish-2026-06-29`
- Development repo path: `D:\longevity\longevity-antiaging-evidence-atlas-EnCn`
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

## Historical Build Baseline

The counts and commands below document earlier milestones and are retained for provenance. Use the current release snapshot and current scripts for new publication work.

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

## 2026-04-29 Skin Scoring Correction

- Corrected `sunscreen-photoaging-prevention` from an overly conservative automated public grade to `A`.
- Rationale: broad-spectrum sunscreen / photoprotection has strong causal plausibility, human RCT evidence for slowing photoaging, and broad dermatology consensus for preventing premature skin aging.
- Boundary kept explicit: `A` applies to prevention and slowing of UV-related photoaging, not reversal of all existing skin aging, not a claim that any single product is superior, and not a substitute for professional dermatology or aesthetic procedures.
- Updated GitHub files: `data/skin_beauty_summary.csv`, `data/skin_beauty_topics.csv`, `content/overview/skin-beauty-summary.md`, and scoring override logic in `scripts/apply_evidence_scoring_v04.py`.
- Feishu `外观抗老总览` should be re-synced after this correction.

## 2026-04-29 Methods A/B Implementation

User asked to execute both hardening options:

- Method A: publication-prep hardening for high-grade topics.
- Method B: methodology enhancement with PICO/PECO, claim-level grading, and appraisal plans.

Implemented:

- `data/literature_library.csv`: 5983 full-library records for Feishu visibility.
- `data/core_review_queue.csv`: 95 A/B-topic core paper review records.
- `data/public_topic_explanations.csv`: 28 topic-level explanations for why a level was assigned and why it is not personal medical advice.
- `data/topic_pico_peco.csv`: 28 PICO/PECO question frames.
- `data/claim_level_grading.csv`: 56 claim-level rows, separating supported public claims from unsupported/overstated claims.
- `data/methodology_appraisal_plan.csv`: 95 appraisal assignments using AMSTAR 2, Cochrane RoB 2, ROBINS-I, or domain screen.
- `content/overview/high-priority-review-brief.md`: public/internal bridge for high-grade topic review.
- `content/overview/claim-level-grading.md`: claim-level grading and PICO/PECO summary.
- `docs/methods-ab-implementation-report-2026-04-29.md`: implementation report.
- `scripts/implement_methods_ab.py`: reproducible generator for these files.

New Feishu tables created/synced:

- `文献库全量`: `tblphEOQSzMb3dFi`, 5983 rows.
- `核心复核队列`: `tblRyAJ5afGo6tGj`, 95 rows.
- `主题评级说明`: `tblMfLdNDc4zkrDk`, 28 rows.
- `PICO_PECO问题框架`: `tblPJ2AHChIV7gGo`, 28 rows.
- `Claim级证据评级`: `tblgsBeHJ7LI7uKf`, 56 rows.
- `方法学复核计划`: `tblwZVdgFQRYd1fA`, 95 rows.

Existing Feishu `候选文献` was also checked: 5983 records already present.

## 2026-04-29 Reader-Friendly Feishu Upgrade

User asked to make the project easier for non-specialist 40-50-year-old readers, especially inside Feishu. Implemented a plain-language layer aimed at readers who do not know biology, statistics, or medical research terminology.

New local files:

- `scripts/build_reader_friendly_layer.py`: builds beginner guides, topic reading guides, glossary, Feishu table guide, and overview Markdown pages.
- `scripts/enhance_feishu_plain_language_fields.py`: adds plain-language fields directly into the Feishu-facing CSVs.
- `data/reader_guides.csv`: 8 beginner guide records.
- `data/reader_topic_guide.csv`: 28 topic guide records covering healthspan and skin/appearance topics.
- `data/plain_language_glossary.csv`: 40 glossary records.
- `data/feishu_table_guide.csv`: 14 Feishu table guide records.
- `content/overview/start-here.md`: first-reader entry page.
- `content/overview/evidence-levels-plain-language.md`: A/B/C/D/E grade explanation in plain Chinese.
- `content/overview/feishu-reading-guide.md`: Feishu navigation and reading order.
- `content/overview/plain-language-glossary.md`: public glossary page.
- `content/overview/reader-topic-guide.md`: public topic reading guide.
- `docs/reader-friendly-upgrade-report-2026-04-29.md`: implementation report.

New Feishu tables created/synced:

- `新手阅读指南`: `tblaYnCNYIJnf0dG`, 8 rows.
- `普通读者主题指南`: `tblUAsYxAzCtNBQc`, 28 rows.
- `术语解释`: `tblTl9zuW2h4Aavp`, 40 rows.
- `飞书表格使用说明`: `tblM53UjZbx6VUJG`, 14 rows.

Existing Feishu tables also updated with plain-language fields:

- `对外总览` (`tblFsXTD5yqnJTFH`): added `plain_takeaway_zh`, `read_first_zh`, `do_not_misread_zh`, `doctor_boundary_plain_zh`, `plain_language_updated`; 20 rows updated.
- `外观抗老总览` (`tbl9vcaOrwjPcWZt`): added `plain_takeaway_zh`, `endpoint_plain_zh`, `do_not_misread_zh`, `professional_boundary_plain_zh`, `plain_language_updated`; 8 rows updated.
- `补剂证据矩阵` (`tblAfXqX6qHqpSKb`): added `plain_takeaway_zh`, `not_a_buying_guide_zh`, `overclaim_warning_plain_zh`, `safety_plain_zh`, `doctor_boundary_plain_zh`, `plain_language_updated`; 100 rows updated.

Feishu Markdown package was regenerated under `build/feishu-docs/`. `scripts/prepare_feishu_docs.py` now includes the beginner pages, claim-level grading page, and high-priority review brief.

Validation run after this upgrade:

```powershell
python scripts\prepare_feishu_docs.py
python scripts\lint.py
python scripts\validate_public_drafts.py
python scripts\validate_skin_beauty_public_drafts.py
```

All validation commands passed before commit.

## Operating Rules For Future Threads

- Always read this file first.
- Do not ask the user for repeated manual Feishu operations unless API permission is actually blocked.
- Keep GitHub as source of truth, then sync Feishu from GitHub CSVs.
- Public pages must include draft and medical-disclaimer language.
- Do not give dose, prescription, brand, or purchase recommendations.
- Do not convert animal, cell, biomarker, skin hydration, or epigenetic-clock findings into human longevity claims.
- Update this handoff log after each major batch of work, especially when changing table IDs, token locations, scoring rules, or sync commands.
