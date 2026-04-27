# Codex Prompt — Literature Ingest

You are maintaining the bilingual repository **长寿抗衰与健康寿命证据图谱 / Longevity Anti-Aging Evidence Atlas EnCn**.

Task:

1. Read `AGENTS.md` and `methodology/inclusion-criteria.md`.
2. Read `data/candidate_sources.csv`.
3. Deduplicate candidates by DOI, PMID, PMCID, title similarity, and URL.
4. Classify each candidate as:
   - include
   - exclude
   - needs_review
5. Prioritize human RCTs, large cohorts, systematic reviews, clinical prevention papers, and high-quality animal lifespan studies.
6. Exclude marketing materials, anecdotes, weak cell-only studies, and tangential papers.
7. Update `data/sources.json` and `data/evidence_matrix.csv`.
8. Do not create public recommendations yet.
9. Run `python scripts/lint.py` before finishing.

Output a concise summary in Chinese and English.
