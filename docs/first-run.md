# 第一次开工 checklist

## 1. GitHub

```bash
git init
git add .
git commit -m "init: 长寿抗衰与健康寿命证据图谱 starter"
git branch -M main
git remote add origin git@github.com:YOUR_NAME/longevity-antiaging-evidence-atlas-EnCn.git
git push -u origin main
```

## 2. 本地环境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/lint.py
python scripts/build_index.py
```

## 3. Codex

```bash
codex exec --sandbox workspace-write \
  "Read AGENTS.md and docs/first-run.md. Create a concrete 4-week project plan in docs/roadmap.md. Then improve any missing templates without adding unsupported medical claims."
```

## 4. PubMed 候选文献

```bash
python scripts/fetch_pubmed.py
```

## 5. 第一轮论文卡片

```bash
codex exec --sandbox workspace-write \
  "Read AGENTS.md and prompts/literature-ingest.md. Process candidate_sources.csv. Select 10 high-priority papers and create paper cards."
```

## 6. 飞书同步

```bash
python scripts/sync_feishu_bitable.py
```
