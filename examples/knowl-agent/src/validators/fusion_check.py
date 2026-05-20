#!/usr/bin/env python3
"""跨领域融合检测：本体名称冲突、词汇交叉、引用断裂、效力声明不一致"""

import re
import argparse
from pathlib import Path
from src.config import DATA_DIR, SAMPLE_DIR
from src.loader import load_all_domains, load_json


NAME_MAP = {
    "量潮科技基本章程": "basic-charter",
    "量潮科技文档格式章程": "docs-format",
    "量潮科技工作章程写作章程": "write-bylaw",
    "量潮科技公司代表章程": "company-representative",
    "量潮科技离职工作章程": "human-resignation",
    "量潮科技沟通管理章程": "connect-index",
    "量潮数据工作章程": "qtdata-index",
    "量潮数据组织管理章程": "qtdata-org",
    "离职工作章程": "human-resignation",
    "沟通管理章程": "connect-index",
    "文档格式章程": "docs-format",
    "工作章程写作章程": "write-bylaw",
    "基本章程": "basic-charter",
}

IGNORE_LIST = [
    "中华人民共和国公司法", "中华人民共和国个人信息保护法",
    "劳动合同", "工作订单", "需求规格说明书",
    "最终验收报告", "交接确认书", "数据处理服务框架协议",
]


def check_name_conflict(data_dir):
    print("========================================")
    print("  1. 本体名称冲突（跨领域同名本体）")
    print("========================================\n")

    name_map = {}
    found = 0

    for d, domain, ontologies, instances, relations in load_all_domains(data_dir):
        for onto in ontologies:
            key = onto.label.replace(" ", "").lower() if onto.label else onto.name.replace(" ", "").lower()
            if key in name_map and name_map[key] != domain.id:
                print(f'  "{onto.label or onto.name}" 出现在: {name_map[key]} ←→ {domain.id}')
                found = 1
            else:
                name_map[key] = domain.id

    if not found:
        print("  （无冲突）")
    print()


def check_term_overlap(data_dir):
    print("========================================")
    print("  2. 术语交叉引用（跨领域词汇重叠）")
    print("========================================\n")

    term_map = {}
    found = 0

    for d, domain, ontologies, instances, relations in load_all_domains(data_dir):
        for term in domain.vocabulary:
            if term in term_map and term_map[term] != domain.id:
                print(f'  "{term}" 同时属于: {term_map[term]}, {domain.id}')
                found = 1
            else:
                term_map[term] = domain.id

    if not found:
        print("  （无重叠）")
    print()


def check_broken_references(sample_dir=None):
    print("========================================")
    print("  3. 引用断裂（文件内《…》引用检测）")
    print("========================================\n")

    sdir = Path(sample_dir) if sample_dir else SAMPLE_DIR
    ref_re = re.compile(r"《([^》]+)》")
    found = 0

    for f in sorted(sdir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        refs = set(ref_re.findall(content))

        for ref in refs:
            skip = any(ignore in ref for ignore in IGNORE_LIST)
            if skip:
                continue

            matched = False
            for name, expected in NAME_MAP.items():
                if name in ref:
                    expected_file = sdir / f"{expected}.md"
                    if expected_file.exists():
                        matched = True
                    else:
                        print(f'  {f.name}: 引用 "《{ref}》" → 期望 {expected}.md 但不存在')
                        found = 1
                        matched = True
                    break

            if not matched:
                for mf in sdir.glob("*.md"):
                    mbase = mf.stem
                    if mbase.lower() in ref.lower():
                        matched = True
                        break

            if not matched:
                print(f'  {f.name}: 引用 "《{ref}》" 但无法匹配到已知文件')
                found = 1

    if not found:
        print("  （全部可追溯）")
    print()


def check_effectiveness_consistency(sample_dir=None):
    print("========================================")
    print("  4. 效力声明模式对比")
    print("========================================\n")

    sdir = Path(sample_dir) if sample_dir else SAMPLE_DIR
    print("提取各文件章程效力条款：")

    statements = []
    for f in sorted(sdir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "章程效力" in line or re.match(r"\*\*第.*条 章程效力", line):
                for j in range(i, min(i + 5, len(lines))):
                    if re.search(r"(经|自|由)", lines[j]):
                        stmt = lines[j].strip().lstrip("*").strip()
                        print(f"  {f.name}: {stmt}")
                        statements.append(stmt)
                        break

    print("\n效力主体一致性检查：")
    bodies = set()
    for stmt in statements:
        m = re.search(r"(公司[^，；。]*?(?:审议|发布|修订))", stmt)
        if m:
            bodies.add(m.group(1))

    if len(bodies) <= 1:
        print("  ✅ 全部文件使用同一效力主体（公司治理机构审议通过，自发布之日起生效）")
    else:
        print("  ⚠️ 存在不同的效力主体，需人工确认")
        for b in bodies:
            print(f"    - {b}")


def run(data_dir=None, sample_dir=None):
    ddir = Path(data_dir) if data_dir else DATA_DIR
    sdir = Path(sample_dir) if sample_dir else SAMPLE_DIR
    check_name_conflict(ddir)
    check_term_overlap(ddir)
    check_broken_references(sdir)
    check_effectiveness_consistency(sdir)
    return 0


def main():
    parser = argparse.ArgumentParser(description="跨领域融合检测")
    parser.add_argument("data_dir", nargs="?", default=DATA_DIR, help="data 目录路径")
    parser.add_argument("sample_dir", nargs="?", default=SAMPLE_DIR, help="sample 目录路径")
    args = parser.parse_args()
    exit(run(args.data_dir, args.sample_dir))


if __name__ == "__main__":
    main()
