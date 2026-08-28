# 宇多Yul细胞/yulcell 长寿抗衰与健康寿命证据图谱

**当前公开快照：** 2026-08-28<br>
**英文项目名：** Longevity Anti-Aging Evidence Atlas EnCn<br>
**品牌：** 宇多Yul细胞/yulcell

这是一套中英文双语、可以追溯来源的公开证据图谱。它不告诉读者应该买什么或吃多少，而是帮助大家判断：一项“抗衰”说法来自人体结局、指标变化、动物实验、机制线索，还是商业宣传。

> [8 月底精编说明](content/public-reader/end-august-2026-update.md)<br>
> [8 月底自包含图文报告](docs/end-august-public-update-2026-08.html)<br>
> [8 月底发帖资产面板](docs/yulcell-posting-asset-dashboard-2026-08-28.html)<br>
> [飞书 9 张长期表索引](docs/feishu-public-assets-2026-08.md)<br>
> [8 月公开 CSV 数据包](public-data/README.md)<br>
> [中英文 GitHub 首页](README.md)

## 这次最重要的变化

这次不是继续往数据库里塞东西，而是“补检 + 清理”同时做。

- PubMed 检索窗口为 2026-08-10 至 2026-08-28。
- 找到 923 个唯一匹配，其中 911 条是新候选，12 条已经在库中。
- 最终保留近期候选 248 条，其中 162 条进入 findings。
- 当前候选库从 11,079 条调整为 11,104 条。
- findings 从 2,966 条调整为 3,039 条。
- 证据矩阵继续固定为 1,500 条；已满额主题以替换为主。

数字变小不是资料丢失。重复项、方案论文、评论勘误、动物/人体边界错误、题名与主题不符和超过容量的低优先级记录退出当前层；每条原因都记录在 `data/archive/`，旧快照和 Git 历史仍可恢复。

## 当前公开体量

| 项目 | 当前数量 | 初中生怎么理解 |
| --- | ---: | --- |
| 候选文献 | 11,104 条 | 等待检查的资料目录，不是已证实结论 |
| 入选短名单 | 3,039 条 | 与主题直接相关、优先继续复核的记录 |
| 证据发现 | 3,039 条 | 自动整理草稿，还不是全部全文人工复核 |
| 证据矩阵 | 1,500 条 | 方便按主题和等级比较的有限集合 |
| 五层公开 CSV | 29,786 行 | 同一论文可跨层出现，不是独立论文总数 |
| 论文卡片 | 3,039 页 | 当前每条 finding 一页 |
| 健康寿命主题 | 20 个 | 本版固定主题，不随热度随意增加 |
| 图片资产 | 57 张 | 7 张主图和 50 张单成分卡 |
| 飞书在线表 | 9 张 | 复用长期表，不再每月新建一套 |

## 做减法的规则

- 候选层每个主题最多 600 条。
- findings 每个主题最多 200 条；不足 200 条就按实际数量，不凑数。
- 证据矩阵总计最多 1,500 条，每个主题最多 100 条。
- 核心人工复核队列每个主题最多 3 条，本版共 54 条。
- 自动检索只能生成有数量上限的待检查 Pull Request，不能直接写入 GitHub `main`。
- 当前月和上一月 CSV 保持展开；更早快照压缩归档并保存 SHA-256。

完整说明：[精编与归档规则](docs/data-retention-and-curation-policy.md)。

## 本轮质量修正

PubMed XML 解析继续限制在论文本身的标识列表。本轮用 NCBI 官方 E-utilities 核对全部 3,039 个 findings PMID：

- 官方摘要缺失：0；
- 实质题名冲突：0；
- 接受轻微题名格式差异：3 个；
- 修正 findings PMCID：27 个；
- 修正候选 PMCID：84 个。

研究类型判断也增加了动物实验、叙述性综述、方案论文、评论和勘误的防误升规则。

## 普通人从哪里开始

1. 先读[8 月底精编说明](content/public-reader/end-august-2026-update.md)，理解如何同时补检、替换和清退。
2. 打开[普通读者入口](content/public-reader/start-here.md)，按自己的问题选择主题。
3. 用[15 条结论](content/public-reader/ten-takeaways.md)建立判断框架。
4. 用[证据权重怎么看](content/public-reader/evidence-weight.md)分清人体、动物、指标和机制研究。
5. 查补剂时先看[最常见 30 个补剂](content/public-reader/supplements-top-30.md)。
6. 查防晒、皱纹或医美时看[护肤与外观抗老速读](content/public-reader/skin.md)。
7. 遇到药物、慢病、高剂量补剂或医美操作时看[哪些内容必须先问医生](content/public-reader/doctor-first.md)。

## 图片怎么读

- 热力图颜色深表示记录多或研究活跃，不表示疗效最好。
- 证据等级是优先复核工具，不表示每个人都应该行动。
- 撤稿密度是风险提醒，不能单独判断一个领域有效或无效。
- 成分卡是阅读入口，不是购买清单或剂量方案。

图片入口：

- [8 月底自包含图文报告](docs/end-august-public-update-2026-08.html)
- [8 月底发帖资产面板](docs/yulcell-posting-asset-dashboard-2026-08-28.html)
- [8 月研究热力图](docs/research-heatmap-2026-08.html)
- [8 月全部 57 张 PNG](docs/assets/visual-assets/2026-08/)

## 飞书怎么读

飞书用于中文结构化展示和复核，GitHub 保留版本化源文件。普通读者先看阅读导航，不要一上来就打开 11,104 条候选表。

- [飞书公开资产总索引](docs/feishu-public-assets-2026-08.md)
- [飞书普通读者导航](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbljh1Xmkn6RYWPD)
- [飞书研究图](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblASMHdK01yuvjL)
- [飞书 50 成分卡](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbliLsUC2T8lXHla)
- [飞书证据矩阵](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblLnS2g439w9pir)

飞书能否被搜索引擎收录，取决于公开分享和搜索引擎抓取权限。仓库和飞书表统一使用“宇多Yul细胞/yulcell”品牌字段和关键词。

## 证据规则

- 不把动物延寿实验说成人类延寿已经证实。
- 不把生物标志物改善说成临床返老还童。
- 不把论文多、热力图颜色深说成疗效更强。
- 不把皮肤外观改善说成健康寿命延长。
- 不把候选文献直接当成已经复核的结论。
- 不提供个人处方、剂量、诊断、停药、医美操作或购买建议。

## 仓库结构

```text
data/                       当前结构化数据
data/archive/               退出决定日志
public-data/                当前月和上一月公开 CSV
archive/public-data/        压缩历史快照
content/public-reader/      普通读者页面
content/papers/             当前论文卡片
content/topics/             20 个健康寿命主题
scripts/                    构建、校验和飞书同步脚本
docs/                       报告、图片和公开资产索引
```

## English Summary

The 2026-08-28 **宇多Yul细胞/yulcell** release keeps the active atlas bounded at 11,104 candidates, 3,039 findings, and a 1,500-row matrix. A bounded PubMed refresh found 911 new candidates; 248 recent candidates remain active and 162 entered findings. Retirement reasons are versioned, older snapshots remain recoverable, and nine stable Feishu tables are reused rather than recreated monthly.

## 使用边界

本项目用于证据复核、公众科普和内容生产，不提供个人医疗建议、诊断、处方、剂量方案、停药建议、医美操作或购买推荐。
