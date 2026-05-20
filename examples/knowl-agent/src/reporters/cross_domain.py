#!/usr/bin/env python3
"""统计每个领域的跨领域关系覆盖率"""

import argparse
from src.config import DATA_DIR
from src.loader import load_all_domains


def run(data_dir=None):
    base = data_dir or DATA_DIR
    domains_data = load_all_domains(base)

    print("====== 跨领域关系覆盖率报告 ======\n")

    total_cross = 0
    for d, domain, ontologies, instances, relations in domains_data:
        cross = [r for r in relations if ":" in r.target_ontology]
        if cross:
            print(f"=== {domain.id} ===")
            print(f"  跨域关系数: {len(cross)}\n")
            for r in cross:
                print(f"  [{r.relation}] {r.source_ontology} → {r.target_ontology}: {r.description}")
            print("")
        total_cross += len(cross)

    print("====== 汇总 ======")
    print(f"跨域关系总数: {total_cross}\n")

    print("--- 各领域跨域关系明细 ---")
    for d, domain, ontologies, instances, relations in domains_data:
        cross = [r for r in relations if ":" in r.target_ontology]
        print(f"{domain.id}: {len(cross)} 条跨域关系")
        for r in cross:
            print(f"    源: {r.source_ontology} → 目标: {r.target_ontology}")

    print("")
    print("--- 判断 ---")
    for d, domain, ontologies, instances, relations in domains_data:
        cross = [r for r in relations if ":" in r.target_ontology]
        if len(cross) >= 2:
            print(f"{domain.id}: ✓ 达标（≥2条）")
        else:
            print(f"{domain.id}: ✗ 未达标（{len(cross)}/2）")

    return 0


def main():
    parser = argparse.ArgumentParser(description="统计每个领域的跨领域关系覆盖率")
    parser.add_argument("data_dir", nargs="?", default=DATA_DIR, help="data 目录路径")
    args = parser.parse_args()
    exit(run(args.data_dir))


if __name__ == "__main__":
    main()
