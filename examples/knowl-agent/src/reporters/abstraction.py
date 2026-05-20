#!/usr/bin/env python3
"""检查 ontology pattern 的抽象度——扫描未抽象信号"""

import re
import argparse
from src.config import DATA_DIR
from src.loader import load_all_domains


SIGNAL_PATTERNS = [
    ("源文件引用", re.compile(r"见\s+\S+\.md")),
    ("书名号引用", re.compile(r"《[^》]+》")),
    ("具体角色名", re.compile(r"(项目经理|商务经理|数据工程师|总经理|总监|主管|总裁|副总裁|董事|秘书长|部门秘书|实训生|实习生|培训生|管培生|公司代表)")),
    ("具体等级编码", re.compile(r"\b(L[0-9]|M[0-9]|T序列|M序列)\b")),
    ("具体数字约束", re.compile(r"[零一二三四五六七八九十百千]+[日天个小时份]|三十日|五个工作")),
]


def run(data_dir=None):
    base = data_dir or DATA_DIR
    errors = 0

    print("====== 本体抽象度检测 ======\n")

    for d, domain, ontologies, instances, relations in load_all_domains(base):
        print(f"=== {domain.id} ===")

        for onto in ontologies:
            signals = []
            for name, pattern in SIGNAL_PATTERNS:
                if pattern.search(onto.pattern):
                    signals.append(f"[{name}]")

            if signals:
                print(f"  [检测到] {onto.id}: {' '.join(signals)}")
                errors += 1
            else:
                print(f"  [通过]   {onto.id}")

        print("")

    print("====== 汇总 ======")
    if errors == 0:
        print("所有本体 pattern 通过抽象度检测")
    else:
        print(f"共检测到 {errors} 个未抽象信号")
    return 0 if errors == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="检查 ontology pattern 的抽象度")
    parser.add_argument("data_dir", nargs="?", default=DATA_DIR, help="data 目录路径")
    args = parser.parse_args()
    exit(run(args.data_dir))


if __name__ == "__main__":
    main()
