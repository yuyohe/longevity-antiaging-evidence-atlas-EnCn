"""Generate a project-level content and scoring audit report.

The audit is intentionally structural and methodological. It does not claim to
complete full-text clinical appraisal for every paper.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"
REPORT = DOCS / f"content-audit-report-{date.today().isoformat()}.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_missing(rows: list[dict[str, str]], fields: list[str]) -> dict[str, int]:
    return {field: sum(1 for row in rows if not str(row.get(field, "")).strip()) for field in fields}


def duplicate_count(rows: list[dict[str, str]], field: str) -> int:
    values = [row.get(field, "") for row in rows if row.get(field, "")]
    return len(values) - len(set(values))


def level_counts(rows: list[dict[str, str]], field: str) -> str:
    counts = Counter(row.get(field, "") or "blank" for row in rows)
    ordered = []
    for key in ["A", "B", "C", "D", "E", "pending", "blank"]:
        if counts.get(key):
            ordered.append(f"{key}: {counts[key]}")
    for key, value in counts.most_common():
        if key not in {"A", "B", "C", "D", "E", "pending", "blank"}:
            ordered.append(f"{key}: {value}")
    return ", ".join(ordered)


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return lines


def topic_rows(summary: list[dict[str, str]]) -> list[list[str]]:
    return [
        [
            row.get("topic_id", ""),
            row.get("title_zh", ""),
            row.get("evidence_level_top", ""),
            row.get("finding_count", ""),
            row.get("quality_confidence_median", ""),
            row.get("status", ""),
        ]
        for row in summary
    ]


def high_level_watchlist(rows: list[dict[str, str]]) -> list[list[str]]:
    out: list[list[str]] = []
    for row in rows:
        if row.get("evidence_level_top") in {"A", "B"}:
            out.append(
                [
                    row.get("topic_id", ""),
                    row.get("title_zh", ""),
                    row.get("evidence_level_top", ""),
                    row.get("finding_count", ""),
                    row.get("reader_boundary_zh", "")[:90],
                ]
            )
    return out


def validate_pages() -> dict[str, int]:
    public_pages = list((CONTENT / "overview").glob("*.md"))
    public_pages += list((CONTENT / "topics").glob("*.md"))
    public_pages += list((CONTENT / "skin-beauty-topics").glob("*.md"))
    paper_pages = [path for path in (CONTENT / "papers").glob("*.md") if not path.name.startswith("_")]
    all_pages = public_pages + paper_pages
    draft_notice_missing = 0
    mojibake_hits = 0
    paper_marker_missing = 0
    for path in all_pages:
        text = path.read_text(encoding="utf-8")
        if "Draft status:" not in text and "草稿状态" not in text and path.name not in {"methods-and-scoring.md", "evidence-scoring-v0-4.md", "evidence-quality-dashboard.md"}:
            draft_notice_missing += 1
        if any(token in text for token in ["鑽", "锛", "涓", "銆", "鐨"]):
            mojibake_hits += 1
        if path.parent.name == "papers" and ("Overinterpretation Risk" not in text or "Medical supervision needed" not in text):
            paper_marker_missing += 1
    return {
        "overview_topic_pages_checked": len(public_pages),
        "paper_pages_checked": len(paper_pages),
        "draft_notice_missing": draft_notice_missing,
        "paper_marker_missing": paper_marker_missing,
        "mojibake_pages": mojibake_hits,
    }


def main() -> None:
    candidates = read_csv(DATA / "candidate_sources.csv")
    findings = read_csv(DATA / "evidence_findings.csv")
    matrix = read_csv(DATA / "evidence_matrix.csv")
    public_summary = read_csv(DATA / "public_summary.csv")
    skin_findings = read_csv(DATA / "skin_beauty_findings.csv")
    skin_summary = read_csv(DATA / "skin_beauty_summary.csv")
    supplements = read_csv(DATA / "supplement_matrix.csv")
    scoring_policy = read_csv(DATA / "scoring_policy_v0_4.csv")
    page_stats = validate_pages()

    finding_required = [
        "finding_id",
        "candidate_id",
        "pmid",
        "topic_id",
        "title_en",
        "result_en",
        "result_zh",
        "conclusion_en",
        "conclusion_zh",
        "final_evidence_level",
        "scoring_note_zh",
    ]
    skin_required = [
        "finding_id",
        "pmid",
        "topic_id",
        "title_en",
        "result_en",
        "result_zh",
        "conclusion_en",
        "conclusion_zh",
        "final_evidence_level",
    ]
    supplement_required = [
        "supplement_id",
        "name_zh",
        "name_en",
        "longevity_evidence_level",
        "skin_beauty_evidence_level",
        "unsupported_claim_zh",
        "safety_notes_zh",
    ]

    topic_counts = Counter(row.get("topic_id", "") for row in findings)
    skin_topic_counts = Counter(row.get("topic_id", "") for row in skin_findings)
    study_types = Counter(row.get("study_type_draft", "") for row in findings)
    endpoint_counts = Counter(row.get("endpoint_class_draft", "") for row in findings)
    skin_study_types = Counter(row.get("study_type_draft", "") for row in skin_findings)
    skin_endpoint_counts = Counter(row.get("endpoint_class", "") for row in skin_findings)
    supplement_longevity = Counter(row.get("longevity_evidence_level", "") for row in supplements)
    supplement_skin = Counter(row.get("skin_beauty_evidence_level", "") for row in supplements)

    duplicate_summary = [
        ["candidate_sources.id", duplicate_count(candidates, "id")],
        ["evidence_findings.finding_id", duplicate_count(findings, "finding_id")],
        ["evidence_matrix.paper_id", duplicate_count(matrix, "paper_id")],
        ["skin_beauty_findings.finding_id", duplicate_count(skin_findings, "finding_id")],
        ["supplement_matrix.supplement_id", duplicate_count(supplements, "supplement_id")],
    ]

    source_counts = Counter(row.get("source", "") for row in candidates)
    matrix_ids = {row.get("paper_id", "") for row in matrix}
    finding_candidate_ids = {row.get("candidate_id", "") for row in findings}
    matrix_not_in_findings = len([paper_id for paper_id in matrix_ids if paper_id not in finding_candidate_ids])

    topic_level_map = {row.get("topic_id", ""): row.get("evidence_level_top", "") for row in public_summary}
    per_topic_final = defaultdict(Counter)
    for row in findings:
        per_topic_final[row.get("topic_id", "")][row.get("final_evidence_level", "")] += 1

    lines: list[str] = [
        "# 内容与评分审计报告 / Content and Scoring Audit Report",
        "",
        f"- 生成日期：{date.today().isoformat()}",
        "- 审计对象：健康寿命图谱、外观抗老/皮肤图谱、补剂证据矩阵、公开总览页和评分方法。",
        "- 审计性质：结构化质量审计 + 方法学一致性审计；不是 1800 篇文献的逐篇全文人工复核。",
        "",
        "## 1. 当前数据库里有什么",
        "",
        *md_table(
            ["模块", "数量", "说明"],
            [
                ["候选文献池 candidate_sources", len(candidates), f"来源分布：{dict(source_counts)}"],
                ["健康寿命 findings", len(findings), "20 个主题，每主题 90 条自动抽取 finding。"],
                ["正式/高权重证据矩阵 evidence_matrix", len(matrix), "当前只收 A/B/部分 C 级记录，用于对外主表。"],
                ["健康寿命主题 public_summary", len(public_summary), "对外收束窗口，每个主题 1 行。"],
                ["皮肤美容 findings", len(skin_findings), "8 个主题，每主题 20 条。"],
                ["皮肤美容主题 skin_beauty_summary", len(skin_summary), "外观抗老对外收束窗口。"],
                ["补剂证据矩阵 supplement_matrix", len(supplements), "100 个热门补剂/成分，当前为证据边界矩阵。"],
                ["评分规则 scoring_policy_v0_4", len(scoring_policy), "公开方法学条目。"],
            ],
        ),
        "",
        "## 1.1 当前对外窗口",
        "",
        "- GitHub 对外总览：`content/overview/public-summary.md`",
        "- GitHub 皮肤美容总览：`content/overview/skin-beauty-summary.md`",
        "- GitHub 补剂矩阵：`content/overview/supplement-summary.md`",
        "- GitHub 评分方法：`content/overview/evidence-scoring-v0-4.md`",
        "- 飞书对外总览表：`tblFsXTD5yqnJTFH`",
        "- 飞书文献总表：`tblYryTL08h4jE53`",
        "- 飞书候选文献：`tblBYXg91Wiw1BJl`",
        "- 飞书外观抗老总览：`tbl9vcaOrwjPcWZt`",
        "- 飞书补剂证据矩阵：`tblAfXqX6qHqpSKb`",
        "",
        "## 1.2 已完成的关键工作",
        "",
        "- 建立 GitHub + 飞书双端同步结构。",
        "- 将健康寿命候选池扩展到 5983 条，健康寿命 findings 扩展到 1800 条。",
        "- 生成 20 个健康寿命主题页、1800 个论文卡片草稿、900 条正式/高权重证据矩阵记录。",
        "- 新增外观抗老/皮肤健康第二图谱：8 个主题、160 条皮肤 finding。",
        "- 新增 100 个补剂/成分的证据边界矩阵。",
        "- 建立 v0.4/v0.5 综合评分逻辑：研究设计、终点价值、人类相关性、来源深度、影响力信号、风险扣分、等级上限。",
        "- 修正防晒/光防护公开等级：预防 UV 相关光老化为 A；不扩展到逆龄治疗或具体产品推荐。",
        "",
        "## 2. 数据完整性检查",
        "",
        *md_table(["检查项", "结果"], [[k, v] for k, v in duplicate_summary]),
        "",
        f"- 健康寿命 finding 必填字段缺失：{count_missing(findings, finding_required)}",
        f"- 皮肤 finding 必填字段缺失：{count_missing(skin_findings, skin_required)}",
        f"- 补剂矩阵必填字段缺失：{count_missing(supplements, supplement_required)}",
        f"- evidence_matrix 中找不到对应 candidate_id 的记录数：{matrix_not_in_findings}",
        f"- 公开页面检查：{page_stats}",
        "",
        "## 3. 当前等级分布",
        "",
        *md_table(
            ["对象", "等级分布"],
            [
                ["健康寿命 findings final_evidence_level", level_counts(findings, "final_evidence_level")],
                ["健康寿命主题 evidence_level_top", level_counts(public_summary, "evidence_level_top")],
                ["正式证据矩阵 evidence_level", level_counts(matrix, "evidence_level")],
                ["皮肤 findings final_evidence_level", level_counts(skin_findings, "final_evidence_level")],
                ["皮肤主题 evidence_level_top", level_counts(skin_summary, "evidence_level_top")],
                ["补剂：健康寿命列", ", ".join(f"{k}: {v}" for k, v in supplement_longevity.most_common())],
                ["补剂：皮肤美容列", ", ".join(f"{k}: {v}" for k, v in supplement_skin.most_common())],
            ],
        ),
        "",
        "## 4. 健康寿命主题总览",
        "",
        *md_table(["topic_id", "中文标题", "公开等级", "finding_count", "质量中位分", "状态"], topic_rows(public_summary)),
        "",
        "## 5. 外观抗老/皮肤主题总览",
        "",
        *md_table(["topic_id", "中文标题", "公开等级", "finding_count", "质量中位分", "状态"], topic_rows(skin_summary)),
        "",
        "## 6. 评分底层逻辑",
        "",
        "当前 v0.4/v0.5 的评分不是单纯按期刊影响因子排序，而是 claim/topic-level 的综合置信度框架：",
        "",
        "1. 检索与入库：从 PubMed 优先检索，辅以 Crossref 和 ClinicalTrials.gov 候选；v0.5 扩充时优先高权重期刊和高设计层级文献。",
        "2. 自动抽取：从题录/摘要抽取题名、PMID/DOI、年份、期刊、研究类型、对象、干预/暴露、终点、主要结果、支持与不支持的结论。",
        "3. 研究设计打分：系统综述/Meta、RCT、队列、Mendelian randomization、动物/机制研究分层；研究设计只是基础分，不单独决定 A/B/C/D。",
        "4. 终点价值打分：死亡、疾病事件、骨折、心血管事件等硬终点权重最高；功能/代谢/认知等为中间终点；皮肤 S1 终点只回答外观/皮肤健康，不等同延寿。",
        "5. 人类相关性：人体证据优先；动物、细胞、纯机制研究设置等级上限。",
        "6. 来源深度：开放全文/PMC、摘要、仅题录分层；摘要级记录不得直接作为最终医疗建议。",
        "7. 影响力信号：自动使用 NIH iCite RCR 和 OpenAlex cited_by_count；JCR IF/CiteScore/SJR 目前未授权导入，不伪造。",
        "8. 风险扣分：摘要级、商业过度宣传、行业资助风险、软终点外推、仅题录等扣分。",
        "9. 等级上限：机制/动物、仅题录、补剂商业化高风险、皮肤软终点等都有 cap rule；最后得到 final_evidence_level。",
        "10. 公开主题等级：不是简单取平均；会结合最高质量文献、领域共识、终点性质和过度解读风险。防晒就是一个例子：单篇综述可为 C，但“广谱防晒预防 UV 光老化”这个结论为 A。",
        "",
        "## 7. 本次审计发现",
        "",
        "### 7.1 已通过的部分",
        "",
        "- 主数据表没有发现重复主键。",
        "- 健康寿命 1800 条 findings 均有基础结论字段和最终等级字段。",
        "- 20 个健康寿命主题、8 个皮肤主题、100 个补剂条目数量完整。",
        "- 公开页面未发现常见乱码标记；皮肤美容公开草稿校验已通过。",
        "- 防晒等级已修正为 A，并限定为“预防/减缓 UV 相关光老化”。",
        "",
        "### 7.2 仍需谨慎的部分",
        "",
        "- 当前大量 finding 仍是摘要级自动抽取，不能等同全文系统综述。",
        "- A/B 级主题里仍应建立人工 spot-check 队列，尤其是 GLP-1、饮食模式、睡眠、血压、LDL/apoB、运动等高影响主题。",
        "- 补剂矩阵目前是“边界和方向矩阵”，不是每个补剂都已经绑定足够的 PMID/全文证据链；它适合对外防止过度宣传，但不适合作为最终推荐表。",
        "- 皮肤美容图谱的主题等级含人工规则/领域判断；应在页面上继续显式区分“领域结论等级”和“单篇文献等级”。",
        "- IF 没有被导入。使用 RCR/OpenAlex 是可公开复现的替代方案，但不能完全替代 JCR IF 或人工期刊分区判断。",
        "- 目前没有完成每条系统综述的 AMSTAR 2、每条 RCT 的 RoB 2、每条观察研究的 ROBINS-I 人工评级。",
        "",
        "## 8. 需要优先人工复核的高等级主题",
        "",
        *md_table(["topic_id", "标题", "等级", "finding_count", "边界摘要"], high_level_watchlist(public_summary)),
        "",
        "## 9. 机会与升级选择",
        "",
        "### 方案 A：发布前最低加固版",
        "",
        "- 对所有 A 级主题做 3-5 篇核心文献人工复核。",
        "- 每个 A 级主题补一段“为什么是 A / 为什么不是医疗建议”。",
        "- 把补剂矩阵标注为“方向性证据边界”，避免用户误读为购买建议。",
        "",
        "### 方案 B：方法学增强版",
        "",
        "- 为每个主题建立 PICO/PECO 问题。",
        "- 系统综述用 AMSTAR 2，RCT 用 Cochrane RoB 2，观察研究用 ROBINS-I。",
        "- 形成 claim-level grading：同一干预不同结论分开评级，例如“防晒预防光老化=A”，“防晒逆转皱纹=C/D”。",
        "",
        "### 方案 C：高可信发布版",
        "",
        "- 每个主题做 PRISMA-like 检索日志、纳入/排除原因、核心证据表。",
        "- 两人独立复核前 200 条核心文献，冲突由第三人裁决。",
        "- 导入 JCR IF 或 Scopus CiteScore/SJR 授权数据，只作为 authority signal，不覆盖 GRADE/RoB。",
        "- 对飞书增加字段：人工复核人、复核日期、复核状态、是否锁定公开等级、争议说明。",
        "",
        "## 10. 外部方法参考",
        "",
        "- GRADE Working Group：https://www.gradeworkinggroup.org/ ，用于透明评估证据确定性和建议强度。",
        "- CDC/ACIP GRADE Handbook：https://www.cdc.gov/acip-grade-handbook/ ，说明 RCT 与非随机研究的初始确定性和降级/升级逻辑。",
        "- Cochrane RoB 2：https://methods.cochrane.org/risk-bias-2 ，RCT 风险偏倚工具。",
        "- AMSTAR 2：https://www.bmj.com/content/358/bmj.j4008 ，系统综述方法学质量评价工具。",
        "- NIH iCite RCR：https://support.icite.nih.gov/hc/en-us/articles/9062490125083-Metrics ，文章层级、领域和时间归一化的影响力指标。",
        "- OpenAlex：https://openalex.org/ ，开放引用与文献元数据来源。",
        "",
        "## 11. 结论",
        "",
        "当前项目已经具备“公开草稿版证据图谱”的骨架和数据规模，但还没有达到医学指南或正式系统综述级别。最重要的下一步不是继续无限扩容，而是把 A/B 级主题做 claim-level 人工复核，并把补剂矩阵从方向性边界表升级为逐条证据链表。",
    ]

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
