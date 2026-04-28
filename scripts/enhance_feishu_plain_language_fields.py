"""Add plain-language fields to Feishu-facing summary CSVs.

These fields are designed for non-specialist readers. They do not change
the evidence grade; they explain how to read the grade safely.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = date.today().isoformat()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def add_fields(path: Path, extra_fields: list[str], fill) -> None:
    rows, fields = read_csv(path)
    for field in extra_fields:
        if field not in fields:
            fields.append(field)
    for row in rows:
        row.update(fill(row))
    write_csv(path, rows, fields)


def level_word(level: str) -> str:
    return {
        "A": "证据相对最扎实，适合优先阅读，但仍不是个人处方。",
        "B": "有较多支持，但仍要看适用人群、终点和边界。",
        "C": "有线索，但还不能当作确定结论。",
        "D": "主要是早期、机制、动物或很有限的人体线索。",
        "E": "目前证据不足，不适合作为行动依据。",
    }.get(level, "等级待定，先不要下结论。")


def topic_plain(row: dict[str, str]) -> dict[str, str]:
    topic_id = row.get("topic_id", "")
    title = row.get("title_zh", "")
    level = row.get("evidence_level_top", "")
    position = row.get("current_public_position_zh") or row.get("evidence_summary_zh", "")
    doctor = "一般先当作知识阅读；如果你有慢病、正在用药、准备改变治疗或做高强度干预，请先问医生。"
    if any(key in topic_id for key in ["blood-pressure", "ldl", "glp1", "metformin", "rapamycin", "senolytics", "klotho", "partial"]):
        doctor = "需要医生或专业人员参与判断。不要根据表格自行加药、停药、换药或组合药物。"
    if any(key in topic_id for key in ["fitness", "physical-activity", "resistance", "dietary", "sleep"]):
        doctor = "生活方式方向可以先理解原则；如果已有疾病、损伤、用药或明显不适，执行前请问医生。"
    return {
        "plain_takeaway_zh": f"{title}：{position} 白话理解：{level_word(level)}",
        "read_first_zh": "先看这一行的白话结论，再看证据等级，最后看“不确定”和“不能这么说”。",
        "do_not_misread_zh": "不要把相关性当因果；不要把群体研究直接当成个人方案；不要把草稿等级当成购买、用药或治疗建议。",
        "doctor_boundary_plain_zh": doctor,
        "plain_language_updated": TODAY,
    }


def skin_plain(row: dict[str, str]) -> dict[str, str]:
    topic_id = row.get("topic_id") or row.get("\ufefftopic_id", "")
    title = row.get("title_zh", "")
    level = row.get("evidence_level_top", "")
    position = row.get("current_public_position_zh", "")
    professional = "普通护肤方向可先理解原则；处方药、激光、换肤、注射、设备类医美需要专业人员评估。"
    if "retinoids" in topic_id or "energy" in topic_id:
        professional = "需要皮肤科医生或合格医美专业人员评估，尤其是敏感皮、孕期备孕、皮肤病或正在用药的人。"
    return {
        "plain_takeaway_zh": f"{title}：{position} 白话理解：{level_word(level)}",
        "endpoint_plain_zh": "这里看的主要是皮肤终点，例如光老化、皱纹、色斑、弹性、水分、经皮水分流失和屏障，不等于延寿。",
        "do_not_misread_zh": "不要把皮肤水分、皱纹评分或仪器指标改善说成“逆龄”或“延寿”；也不要把单个成分当作万能方案。",
        "professional_boundary_plain_zh": professional,
        "plain_language_updated": TODAY,
    }


def supplement_plain(row: dict[str, str]) -> dict[str, str]:
    name = row.get("name_zh", "")
    longevity_level = row.get("longevity_evidence_level", "")
    skin_level = row.get("skin_beauty_evidence_level", "")
    unsupported = row.get("unsupported_claim_zh", "")
    safety = row.get("safety_notes_zh", "")
    supervision = str(row.get("medical_supervision_needed", "")).lower() == "true"
    if supervision:
        doctor = "建议先问医生或营养/药学专业人员，尤其是慢病、用药、孕期备孕、肝肾问题或准备长期高剂量使用。"
    else:
        doctor = "仍然不建议把它当作治疗方案；如果已有疾病、正在用药或准备长期叠加补剂，请先问专业人员。"
    return {
        "plain_takeaway_zh": f"{name}：健康寿命证据 {longevity_level or '待定'}，皮肤美容证据 {skin_level or '待定'}。先看安全边界和不支持的说法，再看等级。",
        "not_a_buying_guide_zh": "这不是购买清单，也不提供品牌、剂量或处方。等级只说明证据强弱，不说明你个人一定需要补。",
        "overclaim_warning_plain_zh": f"常见误读：{unsupported}" if unsupported else "常见误读：把补剂宣传语当成医学结论。",
        "safety_plain_zh": safety or doctor,
        "doctor_boundary_plain_zh": doctor,
        "plain_language_updated": TODAY,
    }


def main() -> None:
    add_fields(
        DATA / "public_summary.csv",
        ["plain_takeaway_zh", "read_first_zh", "do_not_misread_zh", "doctor_boundary_plain_zh", "plain_language_updated"],
        topic_plain,
    )
    add_fields(
        DATA / "skin_beauty_summary.csv",
        ["plain_takeaway_zh", "endpoint_plain_zh", "do_not_misread_zh", "professional_boundary_plain_zh", "plain_language_updated"],
        skin_plain,
    )
    add_fields(
        DATA / "supplement_matrix.csv",
        [
            "plain_takeaway_zh",
            "not_a_buying_guide_zh",
            "overclaim_warning_plain_zh",
            "safety_plain_zh",
            "doctor_boundary_plain_zh",
            "plain_language_updated",
        ],
        supplement_plain,
    )
    print("plain-language Feishu fields enhanced")


if __name__ == "__main__":
    main()
