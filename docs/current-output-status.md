# 宇多Yul细胞/yulcell 当前验收状态 / Current Output Status

Evidence snapshot / 资料快照: 2026-10-10 · Organization / 分类整理: 2026-10-16

## Reader Layout / 本次阅读整理

本轮只做分类、说明和历史版本整理，没有新增文献、更改评级或重画图片。当前入口按“项目介绍 → 热力图与成分卡 → 查证据 → 找原文”排列；首页直接展示真实图片，维护记录折叠到后面。

飞书保留全部48张数据表，其中9张为当前表、39张旧月份与早期表集中放入“90 历史资料（旧月份）”。当前表改为短名称，原表ID和链接不变；仪表盘、工作流及既有页面收进维护工具，不改其内容。14条导航重排，并保留“先看什么”“避免误读”说明。旧表中的独有记录没有删除，也没有重新塞回当前有容量控制的资料层。

2026-10-16完成九表只读回查：9/9通过，记录数、主键、来源字段、品牌和GitHub链接一致，57个图片附件完整，核验字段无乱码。文献目录界面显示11,167/20,000条，额度含限免部分；当前不需要续表。以后按实际额度90%预警，达到上限并去重后才建同名续表，不按月份建重复表。

GitHub的68份旧阅读说明与HTML移入[统一历史目录](../archive/reader-history/README.md)，保留逐文件校验及冻结来源提交。归档副本修正相对链接并统一UTF-8/LF；原始字节可从来源提交恢复。旧GitHub文件路径已改变，需从历史目录访问；飞书原表链接不变。

本地71项单元测试、lint、人体与皮肤草稿校验、完整发布校验及索引构建通过；15份读者导出和2,512份完整导出已重建。Git差异确认当前五层公开CSV、科学源表和57张PNG均未改变。飞书浏览器重新加载后，入口排序和目录分组仍保持。

本轮没有修改分享权限，也不做移动硬盘备份。未登录访客能否直接进入飞书当前表仍是单独的权限核对项，不能把已登录回查通过当作匿名访问验证。

English: this pass reorganizes reader entry points without changing evidence or images. All 48 Feishu data tables remain; 39 historical tables are grouped separately. Nine current table IDs remain stable. Sixty-eight old reader documents move to a checksummed archive with frozen original references. Sharing permissions and removable-drive backups are unchanged.

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
