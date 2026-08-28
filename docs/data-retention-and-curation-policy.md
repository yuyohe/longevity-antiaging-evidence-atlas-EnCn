# 宇多Yul细胞证据图谱：精编与归档规则 / Curation and Retention Policy

**最近复核 / Last reviewed:** 2026-08-28<br>
**品牌 / Brand:** 宇多Yul细胞/yulcell

## 先说结论 / The Short Version

这个项目不追求“越多越好”。候选文献只是等待检查的材料，不等于已经证实的结论。每次更新都同时做两件事：找新资料，也清理旧资料。

This project does not treat a larger database as a better database. A candidate paper is material awaiting review, not a proven conclusion. Every release adds useful records and removes noise from the active layers.

## 当前容量 / Active Limits

| 层级 / Layer | 上限 / Limit | 为什么 / Why |
| --- | ---: | --- |
| 每个主题的候选文献 / Candidates per topic | 600 | 保留可检查的检索池，避免单一热门主题淹没其他主题。 |
| 每个主题的证据发现 / Findings per topic | 200 | 只保留与主题直接相关、值得继续复核的记录。 |
| 证据矩阵 / Evidence matrix | 1,500 total; 100 per topic | 让公开矩阵保持可读、可筛选。 |
| 核心人工复核队列 / Core review queue | 3 per topic | 把有限人工时间放在最重要的记录上。 |

上限不是配额。一个主题只有 29 条合格记录，就保留 29 条，不为了把表格填满而加入弱相关论文。

Limits are not quotas. A topic with only 29 suitable records keeps 29; weak matches are not added just to fill space.

## 什么会退出当前层 / What Leaves the Active Layer

- 重复 PMID、DOI 或重复题名 / duplicate PMID, DOI, or normalized title;
- 方案论文、注册计划、评论、社论、勘误等非结果论文 / protocols, plans, commentaries, editorials, or corrections;
- 题名没有直接出现该主题概念 / title does not directly signal the assigned topic;
- 人体结局主题中的明确动物实验 / direct animal experiments inside human-outcome topics;
- 同主题中优先级更低，并且已超过容量上限 / lower-priority records beyond the topic limit;
- 无法映射到当前 20 个主题 / records not mapped to one of the 20 current topics.

退出当前层不等于论文“错误”或“被否定”。它只表示这条记录不适合占用当前公开主库的位置。

Removal from an active layer does not mean a paper is false. It means the record should not occupy a place in the current public working set.

## 可追溯与恢复 / Traceability and Recovery

- 8 月底候选退出原因：`data/archive/candidate_retirement_2026-08-end.csv`
- 8 月底发现层退出原因：`data/archive/finding_retirement_2026-08-end.csv`
- 8 月中期退出日志：`data/archive/candidate_retirement_2026-08-mid.csv` 与 `data/archive/finding_retirement_2026-08-mid.csv`
- 当前 8 月底与 7 月 CSV 保持展开，方便直接下载比较。
- 完整 8 月中期五表快照：`archive/public-data/public-data-2026-08-mid.zip`
- 更早的完整 CSV 按月份压缩到 `archive/public-data/`，ZIP 内含每个文件的行数、字节数和 SHA-256。
- Git 历史仍保留发布时的完整版本，可以恢复任何旧记录。

The current and previous monthly snapshots stay unpacked. Superseded same-month and older snapshots are compressed with internal row counts and SHA-256 hashes. Git history remains the final recovery path.

## 自动检索的边界 / Automation Boundary

每周自动检索只生成一个有数量上限的“待检查入口表”，并提交 Pull Request。自动任务不能把候选直接写进当前证据库，也不能直接修改 `main`。

The weekly search produces a capped intake file and a pull request. Automation cannot write directly into the active evidence layers or push candidate records straight to `main`.

## 读者怎么理解 / How Readers Should Use It

1. 先看普通读者说明，不要从上万条候选开始。
2. 把候选库当目录，把 findings 当待复核摘要，把矩阵当筛选工具。
3. A、B、C、D、E 是证据层级草稿，不是个人治疗建议。
4. 论文数量多、热力图颜色深，不等于干预有效。

1. Start with the plain-language guide.
2. Treat candidates as an index, findings as review drafts, and the matrix as a filter.
3. Evidence grades are drafts, not personal medical advice.
4. More papers or darker heatmap cells do not prove that an intervention works.
