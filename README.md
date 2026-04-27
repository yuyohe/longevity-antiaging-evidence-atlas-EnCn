# Longevity Anti-Aging Evidence Atlas EnCn

A bilingual, open, evidence-graded knowledge base for longevity, healthspan, clinical prevention, supplements, biomarkers, and frontier geroscience.

Chinese public name: **长寿抗衰与健康寿命证据图谱**.

Repository name: **longevity-antiaging-evidence-atlas-EnCn**.

## Mission

This repository maintains a transparent evidence atlas for longevity and anti-aging claims. It separates hard human outcomes from biomarkers, animal studies, and mechanistic hypotheses.

## Core rules

- Do not present animal lifespan studies as proven human lifespan extension.
- Do not present biomarker improvement as clinical rejuvenation.
- Do not provide medical prescriptions or dosing protocols.
- Use bilingual outputs: English metadata, Chinese public interpretation.
- GitHub is the source of truth; Feishu and other Chinese platforms are publishing layers.
- Candidate records from PubMed, ClinicalTrials.gov, and Crossref require human approval before inclusion.

## Structure

```text
AGENTS.md                 AI maintenance instructions
README.zh-CN.md           Chinese project intro
methodology/              Inclusion criteria, grading, search strategy
data/                     CSV/JSON source of truth
content/papers/           Bilingual paper cards
content/topics/           Topic pages
content/analysis/         Evidence rankings and reviews
content/recommendations/  Public recommendation boundaries
scripts/                  Fetch, lint, index, Feishu sync
prompts/                  Codex task prompts
docs/                     Setup guides
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/lint.py
python scripts/build_index.py
```

Run Codex:

```bash
codex exec --sandbox workspace-write \
  "Read AGENTS.md and perform the first maintenance pass."
```
