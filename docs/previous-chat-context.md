# 之前 ChatGPT 对话上下文摘要

来源：用户提供的 ChatGPT share 链接，标题为“长寿研究与内容创作”。共享页中的工具输出多数已被 redacted，但用户目标、最终方案和脚手架说明可读。

## 起点

用户最初参考的是 Reddit / Biohackers 帖子：

`Analyzed 75 longevity papers - most of your stack...`

以及作者 GitHub 目录：

`github.com/toadlyBroodle/science/tree/main/biology/longevity`

核心问题不是简单复刻原帖，而是理解其方法：把长寿/抗衰相关论文做成可维护的知识库，再转换成中文互联网可读、可审计、可持续更新的内容系统。

## 对参考项目的判断

参考项目的优点：

- 用 Markdown、sources、wiki pages、scripts、recommendations 形成知识图谱。
- 重视硬终点、死亡率、体能、肌肉、睡眠、腰围、烟酒等基础证据。
- 把 NMN/NR、盲补维 D、年轻血浆、端粒酶产品、多数补剂栈降级处理。
- 可被 AI agent 维护，偏向“AI-assisted research map”而不是传统综述。

参考项目的局限：

- 作者公开身份更像软件、AI agent、自动化/数据工具背景，不应被当作临床权威。
- 可见维护窗口较短，不能证明长期定期维护。
- README、log、source 数量之间曾出现不同步。
- 部分内容可能来自 abstract/search results，需要逐条核查。
- 不能把作者结论直接当事实，应逐条降调、核对、分级。

## 适合借鉴的方法

推荐工作流：

```text
文献源清单
→ 单篇论文卡片
→ 主题页
→ 综合分析页
→ 推荐结论
→ 更新日志
→ 自动检查脚本
→ 人工 review
→ 发布层同步
```

底层不应只是文章合集，而应是：

```text
Markdown / CSV / JSON / Python scripts / Git version control
```

## 平台选择结论

之前对话已经形成的核心结论：

- GitHub 是 source of truth，最适合 Codex 维护。
- 飞书是中文结构化展示和知识库展示首选。
- Gitee 可作为国内镜像。
- 腾讯文档可做强备选。
- 语雀可做补充展示，但不适合作为第一主平台。
- 公众号、知乎、B站、小红书只做传播层，不做事实源头。

推荐架构：

```text
GitHub 主仓库
  ↓
Codex 维护：文献抓取、论文卡片、证据矩阵、双语主题页、lint、索引
  ↓
人工 review / merge
  ↓
自动同步
  ├── 飞书多维表格：结构化证据数据库
  ├── 飞书知识库：中文公开知识库
  ├── Gitee：国内代码仓库镜像
  ├── 静态网站：双语长期公开站点，可选
  └── 腾讯文档 / 语雀：补充展示，可选
```

## 项目应比参考 GitHub 强的地方

需要补足：

- 双语结构：中文用于公众理解，英文用于元数据和国际核查。
- 结构化证据矩阵：可按研究类型、终点、风险、证据等级排序。
- 纳入/排除标准：避免主观收录。
- 文献检索日志：记录 query、结果数、纳入数、排除原因。
- 风险偏倚评估：RCT、队列、动物实验、机制研究分层。
- 硬终点 vs 替代终点：死亡率、MACE、功能终点不能和 NAD+、生物年龄 clock 等同。
- 中文发布层：GitHub 给技术/审计用户，飞书给中文读者。

## 证据和医学边界

长期保持这些规则：

- 不把动物实验写成人类延寿。
- 不把 biomarker 改善写成“逆龄”或“已经延寿”。
- 不给药物、补剂、处方、剂量建议。
- 药物、疾病、检测、异常指标和治疗方案必须标注医生监督。
- Codex 可以生成 PR，但不应绕过人工 review 自动发布医学结论。

## 之前已经生成过的 starter 包

之前对话最终生成了：

`longevity-antiaging-evidence-starter.zip`

包含：

- `AGENTS.md`
- `README.md`
- `README.zh-CN.md`
- `DISCLAIMER.md`
- `CHANGELOG.md`
- `data/sources.json`
- `data/evidence_matrix.csv`
- `data/candidate_sources.csv`
- `content/papers/_template.md`
- `content/topics/_template.md`
- `methodology/`
- `prompts/`
- `scripts/fetch_pubmed.py`
- `scripts/sync_feishu_bitable.py`
- `scripts/build_index.py`
- `scripts/lint.py`
- `docs/connect-codex-github.md`
- `docs/connect-feishu.md`
- GitHub Actions

当前本地项目就是基于这个 starter 包继续调整。

## 当前会话已经更新的正式决策

- GitHub repository: `longevity-antiaging-evidence-atlas-EnCn`
- GitHub visibility: private
- 中文公开名：`长寿抗衰与健康寿命证据图谱`
- English public name: `Longevity Anti-Aging Evidence Atlas EnCn`
- 第一阶段抓取范围：标准版，PubMed + ClinicalTrials.gov + Crossref
- 飞书 Base：建议四张表，`文献总表`、`候选文献`、`主题库`、`发布日志`

## 后续执行原则

1. 先建 GitHub 私有仓库。
2. 再建飞书多维表格和自建应用。
3. 先跑通 `文献总表` 同步。
4. 再扩展 `候选文献`、`主题库`、`发布日志`。
5. 抓取结果先进入候选队列，不直接进入正式证据矩阵。
6. 用户批准候选文献后，再生成论文卡片、主题页和证据矩阵。
