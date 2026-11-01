# 当前版本核验 / Current Release Verification

## 2026-11-01 访问核验 / Access Check

- GitHub仓库为公开状态。全新未登录请求取得五张完整CSV：文献目录11,181行、检索来源11,181行、优先复核名单2,497行、研究笔记2,497行、矩阵1,500行，均返回HTTP 200。文献目录含11,061个不同PMID、43条ClinicalTrials.gov来源和77条Crossref来源；来源之间仍可能涉及相同研究。
- [全部公开资料](full-library.md)集中列出五表、卡片、研究图、评分方法、撤稿记录与历史快照。新增112页文献目录和25页复核名单，每页最多100条；仅改变浏览方式，不改资料快照与科学评级。
- 飞书此前文件分享实际为`anyone_editable`，现已在底层多维表格与wiki节点读回确认`external_access=true`、`link_share_entity=anyone_readable`。
- 高级权限原“普通用户”自定义角色只配置5张旧表。现按现有资产清单配置48张表为`table_perm=1`，不允许新增、删除记录；没有修改角色成员、表格内容或历史记录。
- 两个独立未登录浏览器会话实测仍被导向`暂无组件`的旧仪表盘，当前九张资料表没有出现。**飞书匿名访问未修好，不能标为通过。** 新版角色接口返回缺少`base:role:read`应用授权；没有扩大应用授权或关闭高级权限。需由有管理权限的账号检查高级权限中的“阅读者/默认访客”是否能读取全部当前表与视图，且允许通过链接分享授权。
- 48张表的名称中未发现AI问答表；本次没有新建或恢复问答入口。内部报告、口播脚本、密钥不列入公开清单。

The GitHub full-data files were anonymously downloaded. Feishu file-link permissions are now read-only, but anonymous table access still fails because the current advanced reader configuration remains unresolved. This access-only update does not change the evidence snapshot or grades.

---

资料快照 / Evidence snapshot：2026-10-30。

## 阅读入口 / Open

- [本期六篇研究解读](../content/public-reader/october-end-2026-update.md)
- [全部当前资产](asset-catalog.md)
- [离线图文报告](october-end-public-update-2026-10.html)
- [助理发帖面板](yulcell-posting-asset-dashboard-2026-10-30.html)
- [飞书阅读导航](https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbljh1Xmkn6RYWPD&view=vewWNihLzD)

## 本期内容 / Contents

10月24日至30日补检20个主题，213个唯一PubMed匹配中有209条新抓取记录。筛选后保留54条近期候选、27条近期研究笔记，包含此前已有记录。

| 处理层 / Layer | 当前 / Current | 相对上期 / Turnover |
| --- | ---: | --- |
| 文献目录、候选 / Literature and candidates | 11,181 | 新进入50、旧退出45 |
| 研究笔记、短名单 / Notes and shortlist | 2,497 | 新进入24、旧退出14 |
| 证据矩阵 / Evidence matrix | 1,500 | 继续保留总量与单主题上限 |

五层合计28,856行，同一论文可能出现多次。20个主题、54条核心复核记录、7张主图和50张成分卡保持稳定规模。

## 已核验 / Verified

- 全部2,497个研究笔记PMID均取得官方题录，无缺失或实质题名冲突；修正9个笔记PMCID、14个候选PMCID。
- 六篇重点解读已读官方摘要，提供中英文说明；全文待复核。线虫实验、每搏输出量、前瞻性队列等分类修正有回归测试。
- 117个撤稿目标完成重新检索，602条历史累计主题匹配对应546个唯一PMID，不是本期新增撤稿数。50种成分的评级资料日期保留。
- 飞书只读审计通过9/9：记录数与主键匹配、核验来源字段一致、品牌标识完整、57个图片附件存在、14条导航指向当前入口。检查字段的乱码数为0。[审计记录](../data/feishu_online_audit_2026_10_30.json)
- 飞书仍为48张表，其中9张当前表、39张历史表。既有画廊和三张简洁阅读视图保留，项目名称补齐“宇多Yul细胞/yulcell”。页面实查确认六张研究图可显示，历史与维护目录已在本次浏览中收起；没有改变分享权限。
- 81项单元测试、lint、健康寿命与皮肤草稿校验、完整发布校验通过。两个自包含HTML各内嵌57张唯一PNG，逐图哈希与当前图片一致，内嵌脚本语法检查通过，无外部样式或脚本依赖。
- 10月23日五表快照与59个视觉原件已归档，7份旧阅读文件移入历史目录，累计83份。ZIP完整性和文件哈希已校验。

## 发布状态 / Publication

GitHub内容提交 [`eb9c9789`](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/commit/eb9c9789b1ee260207001ab846b4045146f5e052) 已发布至公开 `main`，[Lint检查](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/actions/runs/40917401317)通过。匿名读取的README与本地UTF-8文本一致；未登录浏览器实查确认双语标题、2026-10-30日期、研究热力图和两张成分示例卡均正常显示。

飞书由本地同步完成并通过9/9线上核验。GitHub的可选飞书工作流整体成功，但实际同步步骤因未启用相应配置而跳过，不能把它当成本次飞书更新的凭证。

Content commit `eb9c9789` is on public main and its Lint check passed. The anonymous README matched local UTF-8 text, and all three homepage images loaded. Feishu publication was verified through the local sync and online audit; the optional workflow skipped its sync step.

## 核验范围 / Limits

本轮没有重测离线HTML的浏览器生成海报、下载按钮或响应式布局；这里只确认嵌入资源、脚本语法和数据一致性。飞书未登录访问权限、本期实际单表额度未重新核实。没有备份至移动硬盘。

Offline interactions and anonymous Feishu access were not re-tested. No removable-drive backup was made. Draft grades and abstract notes do not imply a completed full-text review or personal medical advice.
