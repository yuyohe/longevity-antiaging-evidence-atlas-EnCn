# 宇多Yul细胞/yulcell 当前验收状态 / Current Output Status

Date / 日期: 2026-10-10

## Production Draft Assets / 可发布草稿资产

- Candidate pool: 11,167 active records, bounded by topic capacity.
- Finding extraction layer: 2450 healthspan/longevity finding records.
- Topic drafts: 20 public draft topic pages.
- Paper-card drafts: 2450 public draft paper pages.
- Evidence matrix: 1500 cautious draft inclusion records.
- Five public processing layers: 28,734 rows, not unique papers.
- Current catalog: [资产总目录 / Asset catalog](asset-catalog.md).

## Verification / 核验

官方标识核对覆盖 2,450 条 findings，缺失与未解决题名冲突均为 0。55 项本地单元测试、lint、人体/皮肤草稿校验、源发布校验和所有归档校验通过。

Playwright 检查两个自包含 HTML：各 57/57 张图解码，桌面 1440×1000、手机 390×844 无页面横向溢出。海报生成并下载为 1400×1900 非空 PNG；原图下载 SHA-256 与源图相同。

飞书 9/9 张长期表只读回查通过（2026-10-10 00:50 UTC）：记录数和主键集合准确，中文题名/结果/结论及核验字段与当前源表一致；57/57 个图片附件齐全，14 条阅读导航已更新，品牌和 GitHub 链接覆盖完整，核验字段乱码记录为 0。原表链接未变。

Feishu read-back passed for all nine stable tables, including counts, keys, source fields, branding, links and all 57 image attachments. Navigation retains 14 entries. Full local release validation also passed.

GitHub 内容提交 [`abf6a61d9f281d88ce50bdfe368110ad2cf1875a`](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/commit/abf6a61d9f281d88ce50bdfe368110ad2cf1875a) 已匿名确认出现在公开 `main`（2026-10-10 01:23 UTC）。不可变版本的 README 与本地 SHA-256 一致，日期/品牌正确，无连续问号或替换字符；About 简介保留商标和双语说明。[GitHub Lint 验收](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/actions/runs/38012975341)通过，包含单元测试、草稿校验、源发布/归档校验与索引构建。

The content commit was anonymously verified on public main. Its immutable README matches the local bytes and preserves the date, exact brand and bilingual text without mojibake. GitHub Lint passed.

旧的可选云端飞书工作流不是本轮九表更新的证明；九表以完成写入后的只读审计为验收依据。后续验收记录提交只补状态和交接说明，不改变内容快照。

## Reader Annotation Pass / 普通读者标注检查

2026-10-10 另做一次读者视角检查，没有增加论文、改评级或重画 PNG。已补五层处理关系、A–E 草稿排序与 H1–H6 终点的区别、英文状态、成分两场景百分比、撤稿分母和三种日期说明。入门页旧撤稿数已修正为当前 596 条匹配行。

飞书 9 张当前表的 67 处字段说明已逐项写入并回读；14 条导航加上“先看什么”和“避免误读”，7 张主图的说明同步更新。新增一个三列“普通读者图例 / Reader notes”视图，保留原视图与全部数据。已登录浏览器确认该视图可打开；未登录时曾跳回旧“数据表”，公开访客可见性仍需管理员核对，本次未改分享权限。

62 项单元测试与源发布校验通过。两份自包含报告各 57 个嵌入 PNG 的 SHA-256 与原图完全一致，仅更新文字与链接。飞书简洁视图已在浏览器重新加载确认三列说明与多行布局保存成功。本次未重新运行本地 HTML 的浏览器下载测试，前面的 Playwright 结果属于标注前版本。

本次阅读说明内容提交 [`d4fe0518`](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/commit/d4fe05183bb402f0a4d37d36b4f0d3ae7bdef07c) 已发布到公开 main，GitHub 页面已显示新的双语读表说明；原文 SHA-256 与本地一致。[线上 Lint 检查](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/actions/runs/38038490715)通过。补充只读审计也确认 9/9 表的数据与附件完整，证据数据和 PNG 未改动。

The annotation pass distinguishes grades, outcome codes, review status, chart denominators and dates. It adds 67 field descriptions and two notes to each of the 14 navigation entries, without changing evidence or PNGs. The signed-in reader view works; anonymous visibility is a separate unresolved check. Sharing permissions were not changed.

## Public Boundaries / 使用边界

- 草稿状态：自动整理，尚未完成全文复核，不构成医疗建议。
- Draft status: automatically prepared; not fully reviewed; not medical advice.
