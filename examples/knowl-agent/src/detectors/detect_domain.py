#!/usr/bin/env python3
"""基于词汇匹配为新文件推荐所属领域"""

import argparse
from pathlib import Path
from src.config import DATA_DIR
from src.loader import load_all_domains


def run(filepath: str, data_dir=None):
    path = Path(filepath)
    base = data_dir or DATA_DIR
    if not path.exists():
        print(f"文件不存在: {filepath}")
        return 1

    content = path.read_text(encoding="utf-8")
    print(f"文件: {path.name}\n")

    results = []
    for d, domain, ontologies, instances, relations in load_all_domains(base):
        if not domain.vocabulary:
            continue
        score = 0
        for term in domain.vocabulary:
            count = content.count(term)
            score += count
        if score > 0:
            results.append((domain.id, score, len(domain.vocabulary)))

    results.sort(key=lambda x: -x[1])
    for name, score, total in results:
        print(f"  {name}: 命中 {score} 次（词汇表 {total} 词）")
    return 0


def main():
    parser = argparse.ArgumentParser(description="基于词汇匹配为新文件推荐所属领域")
    parser.add_argument("file", help="要检测的文件路径")
    args = parser.parse_args()
    exit(run(args.file))


if __name__ == "__main__":
    main()
