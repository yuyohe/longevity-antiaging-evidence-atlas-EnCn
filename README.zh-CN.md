# 长寿抗衰证据地图 / Longevity Anti-Aging Evidence Atlas EnCn

**品牌 / Brand：** 宇多Yul细胞/yulcell  
**品牌资产索引 / Brand asset index：** [docs/yulcell-brand-index.md](docs/yulcell-brand-index.md)

这个仓库是 **宇多Yul细胞/yulcell** 维护的长寿抗衰证据地图，把“抗衰、长寿、健康寿命、补剂、护肤和前沿技术”的资料整理成一套可追踪的证据库。它不是产品清单，也不是治疗方案；它的作用是帮读者分清楚：哪些说法比较可靠，哪些只是早期研究，哪些更像商业宣传。

This repository is a bilingual evidence atlas by **宇多Yul细胞/yulcell** for longevity, anti-aging claims, healthspan, supplements, skin-aging topics, biomarkers, and frontier geroscience. It is designed to separate stronger evidence from early signals and overclaimed marketing.

搜索关键词：宇多Yul细胞/yulcell、yulcell、宇多Yul细胞、长寿抗衰证据图谱、健康寿命证据图谱、抗衰证据库。

## 第一次打开，从这里开始

如果你不是研究人员，也不想一上来读论文，请从这些入口开始：

- [普通读者入口：从这里开始](content/public-reader/start-here.md)
- [2026 年 6 月底更新说明：普通读者版](content/public-reader/june-end-2026-update.md)
- [15 条结论](content/public-reader/ten-takeaways.md)
- [证据权重怎么看](content/public-reader/evidence-weight.md)
- [撤稿风险怎么看](content/public-reader/retractions.md)
- [大众版入口表](content/public-reader/index.md)
- [大众主题速读](content/public-reader/topics.md)
- [最常见 30 个补剂](content/public-reader/supplements-top-30.md)
- [大众补剂速查](content/public-reader/supplements.md)
- [护肤与外观抗老速读](content/public-reader/skin.md)
- [哪些内容必须先问医生](content/public-reader/doctor-first.md)

If you are a non-specialist reader, start here:

- [Plain-language start page](content/public-reader/start-here.md)
- [15 takeaways](content/public-reader/ten-takeaways.md)
- [Evidence weighting guide](content/public-reader/evidence-weight.md)
- [Retraction risk guide](content/public-reader/retractions.md)
- [Easy reader home](content/public-reader/index.md)
- [Easy topic guide](content/public-reader/topics.md)
- [30 common supplements](content/public-reader/supplements-top-30.md)
- [Easy supplement lookup](content/public-reader/supplements.md)

## 一句话说明

很多“抗衰”内容听起来很厉害，但证据强弱差别很大。这个项目把它们分成几类：

- 比较值得普通人先理解的基础方向：运动、力量、睡眠、饮食模式、血压、血脂、血糖、体重和防晒。
- 需要医生或专业人员参与的方向：处方药、慢病指标、医美项目、高剂量或长期补剂。
- 只能当作前沿研究看的方向：动物实验、细胞实验、衰老时钟、部分重编程、清除衰老细胞等。
- 容易被夸大的方向：把补剂说成“逆龄”，把皮肤改善说成“延寿”，把一个指标变好说成真正抗衰。
- 证据评分现在使用 v0.5 字段：除了研究设计、终点、人群和风险，也单独加入发表地/期刊层级 `venue_tier`、`venue_score`。
- 撤稿风险层：对已进入资产库的补剂、护肤和抗衰前沿主题，记录近 20 年发表、且被 PubMed 标记为 `Retracted Publication` 的撤稿观察。

In plain English: the project does not ask readers to buy or try things. It helps readers understand what the evidence can and cannot say.

## 现在有哪些资产

| 资产 | 数量 | 适合谁看 |
| --- | ---: | --- |
| 文献候选库 | 14273 条 | 维护者、研究者 |
| 当前高权重证据矩阵 | 2400 条 | 研究者、编辑 |
| 健康寿命证据发现 | 4800 条 | 研究者、编辑 |
| 健康寿命主题 | 20 个 | 普通读者、编辑、研究者 |
| 皮肤与外观抗老主题 | 9 个 | 普通读者、内容创作者 |
| 皮肤与外观证据发现 | 180 条 | 编辑、研究者 |
| 补剂/营养条目 | 100 个 | 普通读者、内容创作者 |
| 撤稿观察目标 | 117 个 | 普通读者、编辑、研究者 |
| 撤稿明细 | 538 条 | 研究者、深度读者 |
| 论文卡片 | 4800 个 Markdown 页面 | 研究者、深度读者 |
| 普通读者页面 | 16 个 | 第一次打开项目的人 |
| 飞书全量 Markdown 发布包 | 4862 个文件 | 维护者 |
| 飞书普通读者包 | 15 个文件 | 普通读者、内容团队 |
| 公开全量 CSV 数据包 | 40546 行 | 研究者、维护者 |
| 公开图片资产 | 57 张 PNG | 内容团队、发帖助手 |
| 自包含发帖面板 | 1 个 HTML | 内容团队、助理 |

评分方法见：[证据评分方法 v0.5](content/overview/evidence-scoring-v0-5.md)。v0.5 把发表地/期刊分成 S/A/B/C/D：S 是顶级综合或临床期刊，A 是领域头部期刊，B 是正规专业或综合期刊，C 是普通索引或注册记录，D 是未知或预印本。期刊只加权，不替代研究设计、终点硬度、人体相关性和偏倚风险判断。
撤稿观察见：[撤稿风险怎么看](content/public-reader/retractions.md) 和 [撤稿风险观察方法](content/overview/retraction-risk-methodology.md)。撤稿数是风险观察信号，不等于成分一定有效或无效。
撤稿层现在同时展示分母：同一口径下的总发表量、年均发表量、撤稿百分比和每 1000 篇撤稿数，避免只按撤稿绝对数量比较。

## 普通人应该怎么读

推荐读法：

1. 从 [普通读者入口](content/public-reader/start-here.md) 开始，知道这个项目能解决什么问题。
2. 读 [15 条结论](content/public-reader/ten-takeaways.md)，快速建立判断框架。
3. 想知道我们怎么筛文献，就看 [证据权重怎么看](content/public-reader/evidence-weight.md)。
4. 想知道哪些成分或方向出现过撤稿记录，就看 [撤稿风险怎么看](content/public-reader/retractions.md)。
5. 想看运动、睡眠、饮食、血压血脂，就看 [大众主题速读](content/public-reader/topics.md)。
6. 想查 NMN、鱼油、维生素、胶原蛋白等，读 [最常见 30 个补剂](content/public-reader/supplements-top-30.md)，再查 [大众补剂速查](content/public-reader/supplements.md)。
7. 想看防晒、皱纹、色斑、屏障、医美设备，就看 [护肤与外观抗老速读](content/public-reader/skin.md)。
8. 看到药物、医美、高剂量补剂、慢病用药，读 [哪些内容必须先问医生](content/public-reader/doctor-first.md)。

只保留一句边界提醒：本项目用于研究整理和内容创作，不提供个人医疗建议、诊断、处方、剂量或购买建议。

## 给内容创作者的用法

你可以把这个项目讲成一张“抗衰证据地图”：

- 它不是告诉大家买什么，而是告诉大家哪些说法不要轻信。
- 它把“健康寿命”和“皮肤外观”分开，避免把护肤效果说成延寿。
- 它把“补剂证据”和“安全边界”放在一起，避免把表格误读成购买清单。
- 它把 PDRN/PN 单独作为美容与医美交叉主题处理，区分外用、导入、注射、skin booster 和填充。
- 它不只看论文数量，也记录近 20 年发表且已被 PubMed 标记撤稿的论文，提醒大家不要只拿单篇论文做宣传。
- 它保留论文卡片和证据矩阵，方便追溯来源。
- 它准备了 GitHub 研究资产和飞书阅读资产，普通人和维护者可以看不同层级。

## 飞书怎么用

仓库里现在区分两个飞书导出包：

- `build/feishu-public-reader/`：普通读者包，只放 11 个入口文件，适合直接分享。
- `build/feishu-docs/`：全量发布包，包含论文卡片、主题页、研究页，适合维护者和深度读者。

普通人不要从全量包开始读。全量包文件很多，适合查证，不适合第一次浏览。

## 仓库结构

```text
data/                     结构化数据：文献、主题、补剂、证据矩阵
content/public-reader/    普通读者入口和人话解释
content/topics/           健康寿命主题页
content/skin-beauty-topics/ 皮肤与外观抗老主题页
content/papers/           论文卡片
content/overview/         总览、方法、术语和公开摘要
content/analysis/         排名和分析页
scripts/                  构建、校验、飞书导出和同步脚本
docs/                     报告、交接和操作说明
```

## For English Readers

This project is a bilingual evidence atlas. The Chinese layer is designed for public communication, while the English metadata and paper cards preserve traceability. Start with the easy reader pages if you want the public-facing interpretation, and use the research pages when you need source-level evidence.

The key design rule is simple: strong evidence does not automatically mean an individual should act, and weak or early evidence should not be marketed as proven longevity advice.
