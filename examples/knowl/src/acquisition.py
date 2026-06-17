"""
知识获取工具：从实验报告中提取结构化知识。

从 markdown 格式的实验报告中提取：
- 可编码性评分表
- 模糊点清单
- 编码发现的问题
- 核心指标
"""

import re
import yaml
from pathlib import Path


def parse_table(lines: list[str]) -> list[dict]:
    """解析 markdown 表格为字典列表。"""
    if not lines:
        return []
    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    rows = []
    for line in lines[2:]:
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def parse_sections(text: str) -> dict[str, str]:
    """按 ## 标题分割文档为章节。"""
    sections = {}
    current_heading = "title"
    current_lines = []
    for line in text.split("\n"):
        if line.startswith("## "):
            sections[current_heading] = "\n".join(current_lines)
            current_heading = line.strip("## ").strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_heading] = "\n".join(current_lines)
    return sections


def extract_ambiguities(text: str) -> list[dict]:
    """从模糊点清单章节提取分类后的模糊点。"""
    ambiguities = []
    current_category = None
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("### "):
            current_category = line.strip("# ")
        elif line.startswith("- ") and current_category:
            ambiguities.append({
                "category": current_category,
                "description": line.lstrip("- "),
            })
    return ambiguities


def extract_issues(text: str) -> list[dict]:
    """从编码发现的 5 个问题章节提取结构化问题。"""
    issues = []
    current = {}
    for line in text.split("\n"):
        line = line.strip()
        bold_match = re.match(r"\*\*(\d+)\.\s+(.+?)\*\*", line)
        if bold_match:
            if current:
                issues.append(current)
            current = {"number": int(bold_match.group(1)), "title": bold_match.group(2)}
        elif line.startswith("- 出处："):
            current["source"] = line.replace("- 出处：", "").strip()
        elif line.startswith("- 问题："):
            current["problem"] = line.replace("- 问题：", "").strip()
        elif line.startswith("- 建议："):
            current["suggestion"] = line.replace("- 建议：", "").strip()
    if current:
        issues.append(current)
    return issues


def extract_observations(text: str) -> list[str]:
    """提取值得记录的观察。"""
    obs = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("- ") and "四层" in line or "手册" in line or "报价单" in line:
            obs.append(line.lstrip("- "))
    return obs


def extract_report(path: Path) -> dict:
    """从实验报告中提取全部结构化知识。"""
    text = path.read_text(encoding="utf-8")
    sections = parse_sections(text)

    result = {
        "title": "商务拓展职能成熟度实验",
        "codifiability": {},
        "ambiguities": [],
        "issues": [],
        "observations": [],
    }

    # 可编码性评分表
    if "可编码性评分" in sections:
        table_lines = sections["可编码性评分"].strip().split("\n")
        table_start = 0
        for i, line in enumerate(table_lines):
            if line.startswith("| 规则"):
                table_start = i
                break
        result["codifiability"]["rules"] = parse_table(table_lines[table_start:])

        # 提取统计
        for line in table_lines:
            m = re.search(r"可编码率\s+\*\*(\d+)%", line)
            if m:
                result["codifiability"]["rate"] = int(m.group(1))

    # 模糊点清单
    if "模糊点清单" in sections:
        result["ambiguities"] = extract_ambiguities(sections["模糊点清单"])

    # 编码发现的 5 个问题
    for heading, content in sections.items():
        if "编码发现" in heading or "5 个问题" in heading:
            result["issues"] = extract_issues(content)
            break

    # 值得记录的观察
    if "值得记录的观察" in sections:
        for line in sections["值得记录的观察"].split("\n"):
            line = line.strip()
            if line.startswith("- "):
                result["observations"].append(line.lstrip("- "))

    # 核心指标
    for heading, content in sections.items():
        if "核心结论" in heading:
            result["conclusions"] = []
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("**"):
                    result["conclusions"].append(line.strip("*"))

    return result


def main():
    root = Path(__file__).resolve().parent.parent
    report_path = root / "assets" / "acquisition.md"
    output_dir = root / "data"

    data = extract_report(report_path)

    # 输出 YAML
    with open(output_dir / "extracted.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, indent=2, sort_keys=False)

    # 输出摘要到终端
    print(f"标题: {data['title']}")
    print(f"规则数: {len(data['codifiability'].get('rules', []))}")
    print(f"可编码率: {data['codifiability'].get('rate', 'N/A')}%")
    print(f"模糊点: {len(data['ambiguities'])} 条")
    print(f"编码问题: {len(data['issues'])} 个")
    print(f"观察记录: {len(data['observations'])} 条")
    print(f"\n输出: {output_dir / 'extracted.yaml'}")


if __name__ == "__main__":
    main()
