#!/usr/bin/env python3
"""领域目录结构完整性验证"""

import json
import argparse
from pathlib import Path
from src.config import DATA_DIR


REQUIRED_FILES = ["domain.json", "ontologies.json", "instances.json", "relations.json"]


def run(data_dir=None):
    base = data_dir or DATA_DIR
    errors = 0

    for domain_dir in sorted(base.iterdir()):
        if not domain_dir.is_dir():
            continue
        name = domain_dir.name
        print(f"=== {name} ===")

        for file in REQUIRED_FILES:
            fpath = domain_dir / file
            if not fpath.exists():
                print(f"  [MISS] {file}")
                errors += 1
                continue
            try:
                with open(fpath, encoding="utf-8") as f:
                    json.load(f)
                print(f"  [OK]   {file}")
            except json.JSONDecodeError as e:
                print(f"  [FAIL] {file} - JSON 格式错误: {e}")
                errors += 1

    print("")
    if errors == 0:
        print("全部验证通过")
        return 0
    else:
        print(f"发现 {errors} 个问题")
        return 1


def main():
    parser = argparse.ArgumentParser(description="领域目录结构完整性验证")
    parser.add_argument("data_dir", nargs="?", default=DATA_DIR, help="data 目录路径")
    args = parser.parse_args()
    exit(run(args.data_dir))


if __name__ == "__main__":
    main()
