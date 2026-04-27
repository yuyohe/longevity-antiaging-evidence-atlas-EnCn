# AGENTS.md — 长寿抗衰与健康寿命证据图谱维护规则

## Project identity

This repository is the source of truth for **长寿抗衰与健康寿命证据图谱 / Longevity Anti-Aging Evidence Atlas EnCn**.

The project maintains a bilingual, evidence-graded knowledge base for:

- longevity and healthspan interventions
- exercise, sleep, nutrition, cardiometabolic prevention
- biomarkers and biological age clocks
- supplements and overhyped anti-aging claims
- frontier geroscience technologies
- clinical trials and translational research

## Language policy

All major outputs must be bilingual when practical:

- English: titles, metadata, study design, endpoints, effect sizes, references.
- Simplified Chinese: public-facing interpretation, practical meaning, limitations.

Do not loosely translate key terms. Preserve terms such as:

- randomized controlled trial / RCT
- cohort
- all-cause mortality
- MACE
- VO2max
- apoB / LDL-C / Lp(a)
- senolytics
- partial reprogramming
- biological age clock

## Evidence hierarchy

Never present weaker evidence as stronger evidence.

Endpoint classes:

- H1: hard endpoint — all-cause mortality, cardiovascular mortality, MACE, stroke, cancer incidence, hospitalization.
- H2: functional endpoint — VO2max, muscle strength, frailty, cognition, sleep apnea severity, falls.
- H3: clinical risk marker — apoB, LDL-C, non-HDL-C, blood pressure, HbA1c, waist circumference.
- H4: biomarker — NAD+, inflammatory markers, mitochondrial markers, proteomic markers.
- H5: biological clock — DNA methylation clock, proteomic clock, transcriptomic clock.
- H6: mechanism/cell/pathway — gene expression, cell culture, pathway model, computational hypothesis.

Evidence levels:

- A: human RCT/meta-analysis with clinically meaningful endpoints.
- B: large prospective cohort or strong repeated human evidence.
- C: small human trial, short-duration RCT, or surrogate endpoint study.
- D: animal lifespan/healthspan study.
- E: cell/mechanism/computational evidence only.
- F: anecdote, uncontrolled claim, marketing material, or unsupported claim.

Recommendation classes:

- Strong Action: reasonable for general adults as lifestyle/risk-reduction action.
- Medical Action: discuss with clinician; requires diagnosis, monitoring, prescription, or individual risk assessment.
- Monitor: frontier research; not a public recommendation.
- Do Not Recommend: not supported, excessive risk, misleading marketing, or no meaningful evidence.
- Insufficient Evidence: evidence too weak or conflicting.

## Medical safety boundary

Do not provide dosing protocols, prescription instructions, diagnosis, or individualized medical advice.

For drugs and clinical interventions, use conservative wording:

- “医生监督下讨论”
- “不是普通人自行使用建议”
- “不能从动物实验直接外推到人类延寿”

Never claim:

- “proven anti-aging” unless supported by human hard outcomes.
- “reverse aging” for biomarker changes alone.
- “extends human lifespan” unless human lifespan or mortality is directly measured.

## Source policy

Use public APIs and open metadata when possible:

- PubMed / NCBI E-utilities
- ClinicalTrials.gov
- Crossref
- Europe PMC
- Semantic Scholar
- PubMed Central open access content

The first approved crawling scope is the standard set:

- PubMed
- ClinicalTrials.gov
- Crossref

All fetched records must enter `data/candidate_sources.csv` or an equivalent candidate table before being promoted to `data/evidence_matrix.csv`.

Do not commit copyrighted full-text PDFs or paywalled full text.

Allowed to store:

- metadata
- DOI / PMID / PMCID
- abstracts when allowed
- open access links
- original analysis and summaries

## Required workflow when adding a paper

1. Add or update `data/sources.json`.
2. Add a paper card under `content/papers/`.
3. Update `data/evidence_matrix.csv`.
4. Update relevant topic pages under `content/topics/`.
5. Update `CHANGELOG.md`.
6. Run `python scripts/lint.py`.
7. Run `python scripts/build_index.py`.

## Required paper card sections

Every paper card must include:

- 中文一句话结论
- English one-sentence conclusion
- Study design / 研究设计
- Population / 样本和人群
- Intervention or exposure / 干预或暴露
- Comparator / 对照
- Primary endpoint / 主要终点
- Key results / 核心结果
- Appropriate interpretation / 适合怎么解读
- Overinterpretation to avoid / 不适合怎么解读
- Practical relevance / 对普通人的意义
- Limitations / 局限性
- Evidence grade / 证据等级
- References / 参考文献

## Quality checks

Before finishing any task:

- Check every claim has a linked source or is clearly labeled as interpretation.
- Check every paper has `id`, `title_en`, `title_zh`, `year`, `study_type`, `species`, `endpoint_class`, `evidence_level`, and `last_checked`.
- Check Chinese conclusions do not overstate evidence.
- Check English summaries are faithful to the source.
- Check links are not broken when possible.
- Do not delete old evidence unless it is duplicate, retracted, or superseded; mark it instead.

## Review guidelines

When reviewing a PR, flag:

- animal-to-human extrapolation
- biomarker-to-lifespan extrapolation
- missing limitations
- missing medical-supervision warnings
- unverified claims
- citation gaps
- inconsistent evidence grading
- potential copyright issues
