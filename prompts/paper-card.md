# Codex Prompt — Paper Card

Create a bilingual paper card for source ID: {{paper_id}}.

Requirements:

1. Use `content/papers/_template.md`.
2. Include Chinese and English one-sentence conclusions.
3. Identify study type, species, sample size, population, intervention/exposure, comparator, endpoint, effect size, limitations, funding/conflicts if available.
4. Assign evidence level A-F and endpoint class H1-H6.
5. Include:
   - Appropriate interpretation
   - Overinterpretation to avoid
   - Practical relevance for Chinese readers
6. Do not claim human lifespan extension unless directly measured.
7. Do not provide drug dosing advice.
8. Update relevant topic pages.
9. Update `CHANGELOG.md`.
10. Run `python scripts/lint.py` and `python scripts/build_index.py`.
