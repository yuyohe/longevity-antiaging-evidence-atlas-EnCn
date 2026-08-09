# 宇多Yul细胞/yulcell · 长寿抗衰与健康寿命证据图谱 / Longevity Anti-Aging & Healthspan Evidence Atlas EnCn

**Current snapshot / 当前公开快照:** 2026-08-09<br>
**Maintainer and public brand / 维护方与公开品牌:** 宇多Yul细胞/yulcell<br>
**Repository / 仓库:** `longevity-antiaging-evidence-atlas-EnCn`

> **Mid-August curated update / 8 月中期精编说明:** [plain-language guide / 普通读者说明](content/public-reader/mid-august-2026-update.md)<br>
> **Self-contained report / 自包含图文报告:** [open report / 打开报告](docs/mid-august-public-update-2026-08.html)<br>
> **Feishu assets / 飞书资产:** [nine stable tables / 9 张长期表](docs/feishu-public-assets-2026-08.md)<br>
> **Public data / 公开数据:** [August CSV package / 8 月 CSV 数据包](public-data/README.md)<br>
> **Chinese guide / 中文详细说明:** [README.zh-CN.md](README.zh-CN.md)

This bilingual, versioned atlas helps readers distinguish stronger human evidence from biomarkers, animal studies, mechanisms, and marketing claims. It is an evidence-navigation project, not a treatment or shopping guide.

这是一套中英文双语、可追溯版本的公开证据图谱，帮助读者分清较强人体证据、生物标志物、动物研究、机制线索和商业宣传。它是证据导航，不是治疗或购物指南。

**Search keywords / 搜索关键词:** 宇多Yul细胞/yulcell, yulcell, 宇多Yul细胞, 长寿抗衰证据图谱, 健康寿命证据图谱, Longevity Anti-Aging Evidence Atlas, Healthspan Evidence Atlas.

## August Snapshot / 8 月快照

| Asset / 资产 | Active size / 当前体量 | What it means / 怎么理解 |
| --- | ---: | --- |
| Candidate sources / 候选来源 | 11,079 | Search index awaiting review / 等待复核的资料目录 |
| Shortlist / 入选短名单 | 2,966 | Direct topic matches prioritized for review / 与主题直接相关的优先复核记录 |
| Evidence findings / 证据发现 | 2,966 | Automated drafts, not completed full-text reviews / 自动整理草稿，不等于全文复核完成 |
| Evidence matrix / 证据矩阵 | 1,500 | Bounded comparison layer / 有容量上限的比较层 |
| Public CSV processing rows / 五层 CSV 总行数 | 29,590 | A paper may occur in several layers / 同一论文可跨层出现 |
| Paper cards / 论文卡片 | 2,966 | One page per active finding / 每条当前 finding 一页 |
| Healthspan topics / 健康寿命主题 | 20 | Fixed topic set for this release / 本版固定主题集合 |
| Visual assets / 图片资产 | 57 | 7 main charts plus 50 ingredient cards / 7 张主图和 50 张成分卡 |
| Feishu Bitable / 飞书多维表格 | 9 | Stable tables reused across releases / 跨版本复用的长期表 |

The 29,590-row total is the sum of five processing layers. It is not a count of unique papers.

29,590 行是五张处理层表的行数相加，不是互不重复的论文数。

## Why Smaller Is Better / 为什么这次数字变小

The previous active candidate pool contained 16,547 records and the findings layer contained 6,000. This release searched PubMed from 2026-07-30 through 2026-08-09, found 1,042 unique matches, and identified 834 new candidates. It then removed noise instead of continually appending records.

上一活动候选池有 16,547 条，findings 有 6,000 条。本轮补检 2026-07-30 至 2026-08-09 的 PubMed 文献，得到 1,042 个唯一匹配，其中 834 条是新候选；随后同步做清理，而不是继续无上限累加。

- Duplicate records, protocols, plans, commentaries, corrections, and clear topic mismatches leave the active layers. / 重复项、方案论文、评论勘误和明确主题错配退出当前层。
- Direct animal or cell experiments leave human-outcome topics. / 明确动物或细胞实验退出人体结局主题。
- Candidates are capped at 600 per topic; findings at 200 per topic. Limits are not quotas. / 候选每主题最多 600 条，findings 最多 200 条；上限不是配额。
- The matrix is capped at 1,500 total and 100 per topic. / 矩阵总计最多 1,500 条，每主题最多 100 条。
- Every retirement reason is logged; older complete snapshots remain recoverable. / 每条退出原因有日志，旧完整快照仍可恢复。

Full policy / 完整规则: [curation and retention policy / 精编与归档规则](docs/data-retention-and-curation-policy.md).

## What Changed / 本次更新

- **English:** 303 recent candidates remain active; 211 entered the findings layer after topic and quality guards.
- **中文：** 近期候选最终保留 303 条，其中 211 条通过主题与质量防线进入 findings。
- **English:** Active findings now contain no protocols or non-primary commentary/correction records.
- **中文：** 当前 findings 不再包含方案论文，也不包含评论、社论或勘误记录。
- **English:** PubMed DOI/PMCID parsing was corrected and all 2,966 finding PMIDs were checked against official NCBI summaries; substantive title mismatches are zero.
- **中文：** 修正 PubMed DOI/PMCID 解析范围，并用 NCBI 官方摘要核对全部 2,966 个 finding PMID；实质题名冲突为 0。
- **English:** All seven main visuals and 50 ingredient cards were regenerated.
- **中文：** 7 张主图和 50 张单成分卡全部重建。
- **English:** Weekly automation now produces a capped intake pull request and cannot write candidates directly to `main`.
- **中文：** 每周自动检索现在只生成有上限的 intake Pull Request，不能直接把候选写入 `main`。

## Start Here / 从这里开始

1. [Mid-August update / 8 月中期精编说明](content/public-reader/mid-august-2026-update.md)
2. [Plain-language start page / 普通读者入口](content/public-reader/start-here.md)
3. [15 takeaways / 15 条结论](content/public-reader/ten-takeaways.md)
4. [Evidence weighting / 证据权重怎么看](content/public-reader/evidence-weight.md)
5. [Topic guide / 大众主题速读](content/public-reader/topics.md)
6. [Common supplements / 最常见 30 个补剂](content/public-reader/supplements-top-30.md)
7. [Skin and appearance / 护肤与外观抗老速读](content/public-reader/skin.md)
8. [Doctor-first topics / 哪些内容必须先问医生](content/public-reader/doctor-first.md)

## Visuals and Feishu / 图片与飞书

- [Self-contained August report / 8 月自包含报告](docs/mid-august-public-update-2026-08.html)
- [August research heatmap / 8 月研究热力图](docs/research-heatmap-2026-08.html)
- [All 57 August PNGs / 8 月全部图片](docs/assets/visual-assets/2026-08/)
- [Feishu public asset index / 飞书公开资产索引](docs/feishu-public-assets-2026-08.md)
- [Feishu reading navigation / 飞书普通读者导航](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbljh1Xmkn6RYWPD)

GitHub is the versioned source of truth. Feishu is the structured Chinese reading and review layer. Search-engine visibility for Feishu still depends on public sharing and crawler access.

GitHub 是版本化源头；飞书是结构化中文阅读和复核层。飞书能否被搜索引擎收录，仍取决于公开分享和搜索引擎抓取权限。

## Evidence Rules / 证据规则

- Do not present animal lifespan studies as proven human lifespan extension. / 不把动物延寿实验说成人类延寿已经证实。
- Do not present biomarker improvement as clinical rejuvenation. / 不把生物标志物改善说成临床返老还童。
- Research volume and dark heatmap colors do not prove efficacy. / 论文多、热力图颜色深，不代表疗效更强。
- Candidate records require review before being treated as evidence. / 候选记录必须经过复核，不能直接当成结论。
- Do not provide personal prescriptions, dosing, diagnosis, procedure advice, or purchase recommendations. / 不提供个人处方、剂量、诊断、医美操作或购买建议。

Scoring / 评分方法: [evidence scoring v0.5 / 证据评分 v0.5](content/overview/evidence-scoring-v0-5.md)<br>
Methods / 方法说明: [methods and scoring / 方法与分级](content/overview/methods-and-scoring.md)

## Repository Structure / 仓库结构

```text
data/                       active structured data / 当前结构化数据
data/archive/               retirement decision logs / 退出决定日志
public-data/                current and previous CSV snapshots / 当前与上一期 CSV
archive/public-data/        compressed older snapshots / 压缩历史快照
content/public-reader/      plain-language pages / 普通读者页面
content/papers/             active paper cards / 当前论文卡片
content/topics/             20 healthspan topics / 20 个健康寿命主题
scripts/                    build, validation, Feishu sync / 构建、校验、飞书同步
docs/                       reports, visuals, public indexes / 报告、图片、公开索引
```

## Historical Snapshots / 历史快照

The July CSV snapshot remains unpacked for direct comparison. May and June five-table snapshots are verified ZIP archives under [`archive/public-data/`](archive/public-data/). Git history remains the final recovery path.

7 月 CSV 保持展开，便于直接比较；5 月和 6 月五表快照已按月压缩并校验，位于 [`archive/public-data/`](archive/public-data/)。Git 历史仍是最终恢复路径。

## Boundary / 使用边界

This project supports evidence review, public education, and content production. It does not provide personal medical advice, diagnosis, prescriptions, dosing protocols, aesthetic procedure guidance, or purchase recommendations.

本项目用于证据复核、公众科普和内容生产，不提供个人医疗建议、诊断、处方、剂量方案、医美操作建议或购买推荐。
