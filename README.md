# Longevity Anti-Aging Evidence Atlas EnCn

A bilingual evidence atlas for longevity, anti-aging claims, healthspan, clinical prevention, supplements, biomarkers, and frontier geroscience.

Chinese public name: **长寿抗衰与健康寿命证据图谱**.

Repository name: **longevity-antiaging-evidence-atlas-EnCn**.

## Mission

This repository maintains a transparent, evidence-graded knowledge base for longevity and anti-aging claims. It separates hard human outcomes from functional endpoints, clinical risk markers, biomarkers, animal lifespan studies, and mechanistic hypotheses.

## Core Rules

- Do not present animal lifespan studies as proven human lifespan extension.
- Do not present biomarker improvement as clinical rejuvenation.
- Do not provide medical prescriptions or dosing protocols.
- Use bilingual outputs: English metadata and Chinese public interpretation.
- GitHub is the source of truth; Feishu is the structured Chinese display and review layer.
- Candidate records from PubMed, ClinicalTrials.gov, and Crossref require human approval before inclusion.

## Current Phase

Phase 1 builds a candidate pool at least 10x larger than the reference manifest we studied. The current target is at least 750 candidate records, followed by manual screening and contribution scoring before formal inclusion.

## Structure

```text
AGENTS.md                 AI maintenance instructions
README.zh-CN.md           Chinese project intro
methodology/              Inclusion criteria, grading, scoring, search strategy
data/                     CSV/JSON source of truth
content/papers/           Bilingual paper cards
content/topics/           Topic pages
content/analysis/         Evidence rankings and reviews
content/recommendations/  Public recommendation boundaries
scripts/                  Fetch, scoring, lint, index, Feishu sync
prompts/                  Codex task prompts
docs/                     Setup and operations guides
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/lint.py
python scripts/build_index.py
```
