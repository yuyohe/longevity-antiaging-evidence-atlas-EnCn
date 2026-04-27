# 如何让 Codex 连接 GitHub 并开始维护仓库

## 方案 A：本地 Codex CLI，最快开工

1. 安装 Codex CLI。

```bash
npm install -g @openai/codex
# 或 macOS
brew install --cask codex
```

2. 登录。

```bash
codex
```

按提示选择 ChatGPT 登录，或配置 API key。

3. 克隆仓库。

```bash
git clone git@github.com:YOUR_NAME/longevity-antiaging-evidence-atlas-EnCn.git
cd longevity-antiaging-evidence-atlas-EnCn
```

4. 初始化环境。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/lint.py
```

5. 让 Codex 开始第一轮维护。

```bash
codex exec --sandbox workspace-write \
  "Read AGENTS.md. Review this repository. Create an implementation plan for the first 40-paper MVP. Then process data/candidate_sources.csv into sources.json, evidence_matrix.csv, and paper cards. Do not overstate evidence."
```

## 方案 B：GitHub PR 中使用 Codex review

在 Codex settings 中启用仓库的 code review 后，可以在 PR 评论里写：

```text
@codex review for evidence overstatement, missing citations, and medical safety issues
```

## 方案 C：GitHub Actions 中运行 Codex

本模板提供：

- `.github/workflows/codex-maintenance.yml`
- `.github/codex/weekly-maintenance.md`

你需要在 GitHub Secrets 添加：

```text
OPENAI_API_KEY
```

然后在 Actions 页面手动运行 `Codex maintenance`。
