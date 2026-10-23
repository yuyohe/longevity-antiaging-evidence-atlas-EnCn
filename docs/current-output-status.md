# 宇多Yul细胞/yulcell：当前核验状态 / Current Verification

资料快照 / Evidence snapshot：2026-10-23。发布验收 / Publication checks：2026-10-24。

[项目首页](../README.md) · [本次更新](../content/public-reader/october-23-2026-update.md) · [当前目录](asset-catalog.md)

## 当前资料 / Current Assets

| 资料 | 当前数量 | 怎样理解 |
| --- | ---: | --- |
| 候选与文献目录 | 各11,176条 | 找到并保留的来源，不表示结论已确认 |
| 研究笔记与优先复核名单 | 各2,487条 | 包含待全文复核的草稿 |
| 证据对照表 | 1,500条 | 有容量上限的比较集合 |
| 图像 | 57张 | 7张主图与50张成分卡 |
| 当前飞书表 | 9张 | 复用原表；全库48张含历史表 |

五个资料层共28,826行，同一论文可跨层出现。相对10月10日，候选新进入108、退出99；研究笔记新进入57、退出20。

## 已核对 / Checked

- 20组检索覆盖10月11日至23日：526个唯一PubMed匹配，其中513条为新候选。筛选后保留120条近期候选、63条近期笔记，包含既有记录。
- 全部2,487个笔记PMID经官方数据核对，缺失和实质题名冲突为0；六篇重点解读基于官方摘要，全文待复核。
- 飞书9/9表通过只读核对：数量、唯一编号、抽取层字段、中文解读、导航目的地、品牌和图片附件一致，检查字段内未发现乱码。[机器核对记录](../data/feishu_online_audit_2026_10_23.json)。
- 文献目录、研究笔记、证据对照表增加三个简洁阅读视图，原始完整视图保留。目录链接直接选中阅读视图。
- 76项单元测试、lint、健康寿命与皮肤草稿检查、完整发布校验通过。历史CSV、视觉原件及76份历史阅读文件保留校验记录。
- 两个HTML各内嵌57张当前图片；图片SHA-256与PNG原件一致，内嵌JavaScript语法检查通过，无外部样式或脚本依赖。

## 验证范围 / Verification Limits

飞书在已登录账号下检查，未重新验证匿名访问，未修改分享权限。多数原始论文仍保留英文题名，六篇本期重点研究另有双语解释。

本次浏览器工具拒绝打开本地`file:`地址，因此离线页面的生成图片和下载按钮未重新进行点击测试；静态文件检查已完成。

Ingredient cards retain their original evidence-review dates. New graphics do not mean every grade has been re-reviewed. The atlas contains draft interpretations and does not give individual medical instructions.

## GitHub 发布 / GitHub Publication

内容提交[`89204bb1`](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/commit/89204bb13a446a52417b1c28bd1b6aca372ddcd4)已发布到公开主分支。2026-10-24通过匿名请求逐字核对README，并在未登录的GitHub页面检查双语文字、商标和三张首页图片，均正常显示。

[GitHub Lint运行39998442268](https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/actions/runs/39998442268)通过，包含单元测试及公开资料校验。仓库的可选飞书工作流跳过了同步步骤；本次九表同步和只读核对已在本地使用现有连接完成，以上九表记录才是同步完成的依据。

Publication is confirmed on public GitHub. The follow-up acceptance record does not change the research data or image files.

本轮没有向移动硬盘备份。历史版本在项目归档和Git版本记录中保留。
