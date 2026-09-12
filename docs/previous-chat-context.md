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

## 当前正式状态（更新至 2026-09-13）

- GitHub repository: `longevity-antiaging-evidence-atlas-EnCn`
- GitHub visibility: public
- 中文公开名：`长寿抗衰与健康寿命证据图谱`
- English public name: `Longevity Anti-Aging Evidence Atlas EnCn`
- 品牌：`宇多Yul细胞/yulcell`
- GitHub 是公开、可版本追踪的事实源；飞书是中文结构化展示和复核层。
- 当前飞书使用 9 张稳定在线表，覆盖文献库、候选、短名单、findings、矩阵、热力图、成分卡、卡片墙和阅读导航。
- 新抓取结果先进入候选层；自动流程只创建候选 PR，不绕过人工复核直接发布医学结论。
- 活跃库设容量上限并允许清退，不以不断增加总条数为目标。
- 例行维护不以移动硬盘备份为发布前提；需要离线副本时另行执行并验证。

上文记录的“私有仓库”和“四张表”是项目初建阶段的历史方案，已经被当前公开架构替代。

## 当前执行原则

1. 检索结果先进入候选队列，不直接进入正式证据矩阵。
2. 每轮先去重、排除非结果论文和主题关联过弱记录，再按主题容量保留最值得复核的内容。
3. 人类结局、功能终点、风险指标、动物寿命和机制线索必须分层表达。
4. GitHub 公开版本通过校验后，再同步飞书稳定表并进行在线审计。
5. 用户批准候选文献后，再把结论升级为已人工复核内容；自动摘要始终保留草稿标识。
6. 每次发布保留可核对的月度快照、清退日志、校验报告和更新说明。
