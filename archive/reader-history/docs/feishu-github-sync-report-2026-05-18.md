# GitHub 与飞书同步状态报告
生成日期：2026-05-20

## 当前结论

飞书侧已经把公开权限设成“互联网上获得链接的人可阅读”，并且所有公开数据表都已经同步完成。GitHub 侧仓库 `yuyohe/longevity-antiaging-evidence-atlas-EnCn` 仍是 private；在仓库没有切 public、当前本地改动没有推送前，隐身窗口无法从 GitHub 看到这些资产。

如果飞书链接在隐身模式仍然空白，原因通常不是表格没公开，而是飞书 Web 端在匿名浏览器里只返回前端壳，表格数据加载还会受到租户安全策略、浏览器隐私策略、地区网络或飞书登录态影响。飞书 API 当前读到的权限是：`external_access=true`，`link_share_entity=anyone_readable`，`lock_switch=true`。

## 当前飞书公开入口

| 类型 | 飞书表 | 记录数 | 链接 | 本地/GitHub 路径 |
| --- | --- | ---: | --- | --- |
| 公开总索引 | 公开数据_公开资产总索引_2026-05 | 11 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblxLlIN4LvohIHv | `data/public_asset_index_2026_05.csv` |
| 公开视觉资产 | 视觉资产_热力图图片_2026-05 | 6 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblv6lnYWiNIsX1o | `data/visual_heatmap_assets_2026_05.csv` |
| 公开视觉资产 | 公开入口_前50成分单卡_2026-05 | 50 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblgxZHbMWOTRjX4 | `data/visual_ingredient_cards_2026_05.csv` |
| 公开数据资产 | 公开数据_成分证据含金量_2026-05 | 50 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblPqnliNb81vsy2 | `data/evidence_yield_metrics_2026_05.csv` |
| 公开数据资产 | 公开数据_主题证据产出率_2026-05 | 13 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblpn0KpsgAMTKPJ | `data/topic_evidence_yield_metrics_2026_05.csv` |
| 公开数据资产 | 公开数据_撤稿密度_2026-05 | 117 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbl6HESOmAlZgUO8 | `data/retraction_risk_summary_20y.csv` |
| 公开全量数据 | 公开数据_全量文献候选库_2026-05 | 11,476 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblF5bAj1BfGIAfp | `public-data/literature-library-2026-05.csv` |
| 公开全量数据 | 公开数据_候选来源原始表_2026-05 | 11,476 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tbluJ36RHMdzcUqe | `public-data/candidate-sources-2026-05.csv` |
| 公开全量数据 | 公开数据_入选短名单_2026-05 | 3,000 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblCHOdOojbsmRdL | `public-data/shortlist-sources-2026-05.csv` |
| 公开全量数据 | 公开数据_证据发现表_2026-05 | 3,000 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblDkp1CCSam5JzL | `public-data/evidence-findings-2026-05.csv` |
| 公开全量数据 | 公开数据_证据矩阵_2026-05 | 1,500 | https://ucngl3rlrux2.feishu.cn/wiki/WriBw4TXZiOsjQkJWk8ctL1xnVg?table=tblM9GnRhWQYIId3 | `public-data/evidence-matrix-2026-05.csv` |

## GitHub 全量公开包

已经生成 `public-data/`：

| 文件 | 记录数 | 内容 |
| --- | ---: | --- |
| `public-data/literature-library-2026-05.csv` | 11,476 | 全量文献候选库 |
| `public-data/candidate-sources-2026-05.csv` | 11,476 | 候选来源原始表 |
| `public-data/shortlist-sources-2026-05.csv` | 3,000 | 入选短名单 |
| `public-data/evidence-findings-2026-05.csv` | 3,000 | 证据发现表 |
| `public-data/evidence-matrix-2026-05.csv` | 1,500 | 证据矩阵 |

合计公开记录数：30,452。飞书为了避免单元格超限，长文本字段是浏览版；完整内容以 `public-data/` CSV 为准。

## 仍需手动完成

GitHub 公开需要在网页上操作：`Settings -> General -> Danger Zone -> Change repository visibility -> Public`。切为 public 后，普通访客默认只能浏览、fork 或提 PR，不能直接改主仓库内容。
