# 大众版知识库与飞书简化视图实施报告

日期：2026-07-14

## 这次做了什么

本次按“方向 B + 方向 C”新增一套独立的大众版阅读层，同时准备飞书可同步的简化 CSV。研究版资料、论文卡片和原始矩阵不被删除，也不被改写。

## 新增资产

| 资产 | 数量 | 用途 |
| --- | ---: | --- |
| 大众首页入口 | 6 | 按需求进入对应页面 |
| 大众主题速读 | 29 | 覆盖 20 个健康寿命主题和 9 个皮肤外观主题 |
| 大众补剂速查 | 100 | 覆盖 100 个补剂/营养条目 |
| 飞书大众导航 | 7 | 给飞书做第一层导航 |

## 飞书建议新建或同步的表

| 表名 | CSV | 作用 |
| --- | --- | --- |
| 大众阅读首页 | data/easy_reader_home.csv | 第一入口 |
| 大众主题速读 | data/easy_reader_topics.csv | 29 个主题的人话解释 |
| 大众补剂速查 | data/easy_reader_supplements.csv | 100 个补剂的人话解释 |
| 大众阅读导航 | data/easy_reader_navigation.csv | 告诉读者打开哪张表 |

## 飞书 Markdown 导出

运行 `python scripts\prepare_feishu_docs.py` 后，大众版页面会以 `public-reader-*.md` 文件名输出到 `build/feishu-docs/`，方便人工导入飞书时识别。

## 同步命令建议

```powershell
python scripts\sync_feishu_csv_table.py --csv data/easy_reader_home.csv --table-name 大众阅读首页 --primary-key 编号 --primary-field 入口 --delete-stale
python scripts\sync_feishu_csv_table.py --csv data/easy_reader_topics.csv --table-name 大众主题速读 --primary-key 编号 --primary-field 主题 --delete-stale
python scripts\sync_feishu_csv_table.py --csv data/easy_reader_supplements.csv --table-name 大众补剂速查 --primary-key 编号 --primary-field 补剂 --delete-stale
python scripts\sync_feishu_csv_table.py --csv data/easy_reader_navigation.csv --table-name 大众阅读导航 --primary-key 编号 --primary-field 我想了解 --delete-stale
```

## 读者层规则

- 第一层不出现 PICO、AMSTAR、ROBINS-I、RoB、v0.4、v0.5 等术语。
- 公开页优先使用“一句话总结、常见误解、注意”。
- 补剂页避免重复空话，优先放具体证据结论和安全边界。
- 药物、疾病指标、医美、高剂量补剂标出专业评估边界。
- 研究版内容仍保留给维护者和深度读者。
