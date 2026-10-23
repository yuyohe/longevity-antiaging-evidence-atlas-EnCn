# 宇多Yul细胞/yulcell：2026-10-10 资产维护记录
## Asset Maintenance Record

**基线 / Baseline:** 2026-10-01，Git `9dc9f4f7eb5616b856cbcd732c0f4dc09c04a26c`。<br>
**检索窗口 / Search:** 2026-10-02 至 2026-10-10。<br>
**范围 / Scope:** 同一公开 GitHub 仓库、同一组飞书长期表、资料层、读者入口、图表和归档。没有移动硬盘副本。

## 实际增减 / Actual Turnover

| 层级 / Layer | 上期 / Before | 旧记录退出 / Retired | 新进入 / Added | 当前 / After | 净变化 / Net |
| --- | ---: | ---: | ---: | ---: | ---: |
| 候选 / Candidates | 11,161 | 66 | 72 | 11,167 | +6 |
| 发现 / Findings | 2,424 | 9 | 35 | 2,450 | +26 |
| 矩阵 / Matrix | 1,500 | 按评分重排 / Reselected | 固定容量 / Bounded | 1,500 | 0 |

20 个主题得到 298 个唯一 PubMed 匹配，其中 289 个此前不在候选库、9 个已在库。最终保留近期候选 81 条、近期 findings 39 条，包含原有记录。候选 283 条、findings 268 条排除/退出决定包含新抓取后就未通过筛选的材料，不能当成移除了这么多旧论文。

Turnover compares stable record IDs. New findings may come from older candidates. Retirement decisions include rejected intake. Publication-date matching can include articles published online earlier and recently assigned to an issue.

候选每主题最多 600，findings 每主题最多 200，矩阵每主题最多 100、总计 1,500。上限不是配额。五个公开处理层合计 28,734 行，同一论文可以跨层出现。

## 旧资产整理 / Historical Organization

- 10 月 1 日五张 CSV：28,670 行完整保存在 [数据包](../../public-data/public-data-2026-10-01.zip)。
- 10 月 1 日视觉原件：57 张 PNG、两个自包含 HTML，共 59 个文件，保存在 [视觉包](../../visual-releases/visual-release-2026-10-01.zip)。
- 全部视觉历史包：5 个 ZIP、241 个原件。每个原件校验字节数与 SHA-256；ZIP 校验 CRC 和完整成员列表。
- 原来的 10 月 1 日 HTML 路径保留归档提示；当前 10 月图片目录代表 10 月 10 日，不能混用日期。
- 9 月与最新 10 月各五张 CSV 保持展开。当前入口统一在[资产目录](../../../docs/asset-catalog.md)，首页不堆放历次报告。
- 不覆盖历史 ZIP，不重写 Git 历史，不删除旧本地工作目录；归档不保证完整克隆变小。

Same-month releases are frozen before updates. ZIP contents remain immutable and recoverable. This tidies the active tree, not the full Git history.

## 资料质量 / Evidence Quality

官方核对 2,450 个 finding PMID，缺失 0、未解决题名冲突 0。IMPACT 试验题名中的 `vs.` 更新为 `compared with`，经 EFetch、ESummary 与 DOI 核对，是同一论文，独立留痕。修正 findings PMCID 12 个、候选 PMCID 17 个，DOI 改动 0。

Six featured studies have Chinese titles, short interpretations and explicit limits in both the report and source tables. They were read at official-abstract level, not full-text level.

本轮重点修正：部分训练组随机、对照组非随机的研究不能标成完全随机比较；准实验/混合分配独立分类，最高 C。认知和 BDNF 未显著改善的结果明确写出。队列识别保留结论中的研究设计线索；呼吸暂停次数作为功能终点识别。评分、来源表、论文卡和公开表同步重建。

50 张成分卡沿用既有暂定评级，评级资料日期、撤稿查询日期和图片日期分开。更新图片不代表 50 个成分完成了新一轮全文评审。

117 个撤稿目标全部重新查询，错误 0；596 条主题匹配行对应 540 个唯一 PMID。采用自 2006 年起的发表日期窗口，属于历史累计，不能说本期新增了这么多撤稿。

## 同步与验收 / Synchronization and Acceptance

本地 55 项单元测试、lint、人体/皮肤草稿校验、源发布校验及全部归档核验通过。两个 HTML 各 57/57 张图解码，桌面/手机无页面横向溢出；生成海报 1400×1900，原图下载与源 PNG 的 SHA-256 相同。

飞书复用 9 张长期表与 14 条导航，不另建月份副本。按主键计算新增、变更和退出，只整理登记表的当前记录；图片使用本轮新上传令牌缓存。

2026-10-10 00:50 UTC 只读验收通过 9/9：数量与主键集合准确，中文题名/结果/结论、研究类型、DOI、评级和日期等被核验源字段一致；品牌/GitHub 链接覆盖完整，57/57 个图片附件齐全，14 条导航日期正确，核验字段乱码记录为 0。全量本地发布校验也已通过。缓存审计报告留在忽略目录 `build/feishu_online_audit_2026_10.json`，不公开附件令牌。

Read-only acceptance passed all nine tables after synchronization. Current source fields match; all image attachments are present. No credentials or attachment tokens are public assets.

GitHub 内容提交 [`abf6a61d`](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/commit/abf6a61d9f281d88ce50bdfe368110ad2cf1875a) 于 2026-10-10 01:23 UTC 匿名确认出现在公开 `main`，README 字节、日期、品牌和双语文字通过核验。[Lint 自动测试](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/actions/runs/38012975341)通过。首次上传遇到 HTTP 408，确认远端未变化后重试成功；只对本次命令使用 HTTP/1.1、OpenSSL 和 64 MiB 请求缓冲，没有改全局 Git 设置，没有强制推送。

The public content commit and its CI were verified. An initial HTTP timeout was retried without changing global Git settings or forcing the branch. The optional REST fallback was not used.

同步缓存、差异目录、PubMed 核对缓存均按具体发布日期隔离。基线比较从校验后的 10 月 1 日 ZIP 读取，避免同月覆盖后与自己比较。配置统一由 `data/current_release.json` 指定。

```powershell
python -X utf8 scripts/build_release.py identifiers
python -X utf8 scripts/build_release.py core
python -X utf8 scripts/build_release.py visuals
python -X utf8 scripts/build_release.py exports
python -X utf8 scripts/build_release.py delta
python -X utf8 scripts/build_release.py sync
python -X utf8 scripts/build_release.py audit
python -X utf8 scripts/build_release.py validate
```

检索和撤稿刷新需在构建前另行执行；同步需要本地凭据，凭据不是公开资产。当前验收状态见[状态记录](../../../docs/current-output-status.md)，读者入口见[本次说明](../content/public-reader/october-10-2026-update.md)。
