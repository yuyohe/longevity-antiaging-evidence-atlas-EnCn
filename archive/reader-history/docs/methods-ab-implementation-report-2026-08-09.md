# 方法 A/B 落地报告 / Methods A-B Implementation Report

- 日期：2026-08-09
- 目的：把发布前最低加固版（方法 A）和方法学增强版（方法 B）做成可管理的数据层、页面和飞书表。

## 已生成的数据表

| 表 | 行数 | 用途 |
|---|---:|---|
| data/literature_library.csv | 11079 | 全量文献库，供飞书完整展示。 |
| data/core_review_queue.csv | 54 | A/B 级主题核心文献人工复核队列。 |
| data/public_topic_explanations.csv | 29 | 每个主题为什么是当前等级、为什么不是医疗建议。 |
| data/topic_pico_peco.csv | 29 | 每个主题的 PICO/PECO 问题框架。 |
| data/claim_level_grading.csv | 58 | 每个主题拆成支持 claim 和不支持/过度宣传 claim。 |
| data/methodology_appraisal_plan.csv | 54 | 给核心队列分配 AMSTAR 2 / RoB 2 / ROBINS-I / domain screen。 |

## 飞书同步目标表

| 飞书表 | table_id | 行数 |
|---|---|---:|
| 文献库全量 | tblphEOQSzMb3dFi | 11079 |
| 核心复核队列 | tblRyAJ5afGo6tGj | 54 |
| 主题评级说明 | tblMfLdNDc4zkrDk | 28 |
| PICO_PECO问题框架 | tblPJ2AHChIV7gGo | 29 |
| Claim级证据评级 | tblgsBeHJ7LI7uKf | 58 |
| 方法学复核计划 | tblwZVdgFQRYd1fA | 54 |

## 关键原则

- A/B 不是个人医疗建议；公开等级只说明人群层面证据和结论边界。
- 同一主题必须按 claim 分级，不能把强结论扩展到弱结论。
- 补剂矩阵仍是边界矩阵，不是购买清单或处方建议。
- IF/JCR 仍不伪造；若后续导入授权数据，只作为 authority signal，不覆盖 GRADE/RoB。

## 下一步复核动作

1. 先复核所有 P1 核心文献，重点是 A 级主题。
2. 每篇系统综述用 AMSTAR 2，每篇 RCT 用 RoB 2，每篇观察研究用 ROBINS-I。
3. 对每个 public claim 做 lock / downgrade / rewrite 决策。
4. 将飞书表中的 `manual_review_status` 从 `queued_not_started` 推进到 `reviewed_locked` 或 `reviewed_downgraded`。
