# 宇多Yul细胞/yulcell：2026-10-01 资产整理记录
## Asset Maintenance Record

**基线 / Baseline:** 2026-09-21 发布，Git `2cebd911c985a11e69cff975ea03799eae5805a7`。<br>
**本轮检索 / Search window:** 2026-09-22 至 2026-10-01。<br>
**执行原则 / Principle:** 补新资料、替换旧噪声、整理入口，不无上限积累。

## 资料增减 / Record Turnover

| 层级 / Layer | 上期 / Before | 旧记录退出 / Old retired | 新进入当前层 / Newly active | 当前 / After |
| --- | ---: | ---: | ---: | ---: |
| 候选 / Candidates | 11,141 | 200 | 220 | 11,161 |
| 发现 / Findings | 2,339 | 45 | 130 | 2,424 |
| 矩阵 / Matrix | 1,500 | 按当前评分重排 / Reselected | 固定容量 / Bounded | 1,500 |

这些增减按记录 ID 与上一期集合比较。finding 的“新进入”可以来自已有候选，不一定是新发表的论文。20 个主题共检索到 1,216 个唯一 PMID，1,129 个此前不在候选库；近期最终保留 307 条候选、161 条 findings，含已有记录。

Counts compare record identifiers with the previous release. Newly active findings may come from older candidates. Recent retained sets include previously indexed records.

候选 1,109 条、findings 1,100 条排除/退出决定包含新抓取后就被排除的记录，**不能**理解成删除了这么多旧文献。

Retirement-decision counts include newly screened-out records, not only removals from the prior library.

## 归档与保留 / Archived and Retained

- 旧视觉原件：182 个文件，132,611,118 字节，归入 4 个 ZIP；CRC、成员列表、每个文件字节数与 SHA-256 全部核验。
- 旧 PNG：6 至 8 月共 171 张移出展开目录，原件保留在 ZIP 和冻结 Git 版本。
- 旧大网页：11 个 HTML 改为归档提示；原始自包含网页保存在 ZIP。
- 旧 CSV：8 月最新 5 张表、29,786 行完整归档；已有同月早期档案不覆盖。
- 当前/上一期：10 月与 9 月五表、57 张图、主报告和发帖面板保持可用。
- 品牌索引改为指向统一资产目录，减少重复清单。
- 旧本地工作目录保持原样；没有删除用户工作，也没有复制到移动硬盘。

Archiving is recoverable and does not rewrite Git history. It reduces active-directory clutter, not necessarily full-clone size.

## 质量检查 / Quality Checks

- 检索触及数量上限时停止，防止静默截断；摘要查询按 200 个 PMID 分批，避免 URL 过长。
- 2,424 个 finding PMID 官方核对；缺失 0，未解决题名冲突 0。1 条题名更新经 EFetch、ESummary、DOI 和期刊核对，保留独立变更记录。
- 模型推算对照、观察性二次分析独立分类，不继承母试验随机比较的标签。
- 六篇精选文献均标记“已读官方摘要，全文待复核”；不伪装完成全文评审。
- 50 张成分卡保留原评级资料日期；撤稿检查与图片日期更新为本轮日期。

## 后续维护入口 / Reproducible Maintenance

本轮在线验收：飞书 9/9 张长期表通过，五张数据表共 28,670 行，核查题名、DOI、研究类型等字段与本地一致；57 张附件齐全，导航 14 条，核查字段无乱码。GitHub 内容提交 `99290b361dbb97fffd3d69f645ed1faa0d9e52bd` 已确认公开发布，仓库品牌简介也已更新。

Online acceptance passed for all nine Feishu tables, with exact counts, audited source fields, attachments and branding. The release-content commit is publicly available on GitHub. Fifty local unit tests and full release validation passed.

当前版本统一由 `data/current_release.json` 指定，复用已有构建脚本，不再每月复制一套运行器。

```powershell
python -X utf8 scripts/build_release.py identifiers
python -X utf8 scripts/build_release.py core
python -X utf8 scripts/build_release.py visuals
python -X utf8 scripts/build_release.py exports
python -X utf8 scripts/validate_public_release.py --source-only
```

联网同步前先核对[长期表注册清单](../data/feishu_table_registry.csv)，只更新同一组 9 张表；完成后运行 `build_release.py audit` 和 `build_release.py validate`。同步需要本地凭据，凭据不属于公开资产。

[当前资产总目录 / Asset catalog](asset-catalog.md) · [归档恢复说明 / Restore](../archive/visual-releases/README.md) · [本次文献解读 / Reader update](../content/public-reader/october-2026-update.md)
