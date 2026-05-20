#!/usr/bin/env python3
"""循环检测+自动修复已知问题（仅补缺失文件，不修 JSON 格式）"""

import json
import argparse
from pathlib import Path
from src.config import DATA_DIR
from src.validators.validate import run as validate_run


REQUIRED_FILES = ["ontologies.json", "instances.json", "relations.json"]
SKELETONS = {
    "ontologies.json": {"ontologies": []},
    "instances.json": {"instances": []},
    "relations.json": {"relations": []},
}
MAX_ITER = 10


def run(data_dir=None, sample_dir=None):
    base = data_dir or DATA_DIR
    print("骨架文件自动补全开始（不修复 JSON 格式错误）\n")

    for i in range(1, MAX_ITER + 1):
        print(f"--- 第 {i} 轮 ---")
        issues = 0

        # 1. 报告 JSON 错误
        for domain_dir in sorted(base.iterdir()):
            if not domain_dir.is_dir():
                continue
            name = domain_dir.name
            for file in REQUIRED_FILES + ["domain.json"]:
                fpath = domain_dir / file
                if not fpath.exists():
                    continue
                try:
                    with open(fpath, encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError:
                    print(f"  [错误] {name}/{file} JSON 格式错误 — 需手动修复")
                    issues += 1

        # 2. 补齐 MISS 骨架
        for domain_dir in sorted(base.iterdir()):
            if not domain_dir.is_dir():
                continue
            name = domain_dir.name
            for file in REQUIRED_FILES:
                fpath = domain_dir / file
                if not fpath.exists():
                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(SKELETONS[file], f, ensure_ascii=False, indent=2)
                    print(f"  [补全] {name}/{file}")
                    issues += 1

        if issues == 0:
            print("全部通过")
            break

    print("")
    return validate_run(base)


def main():
    parser = argparse.ArgumentParser(description="循环检测+自动修复已知问题")
    parser.add_argument("data_dir", nargs="?", default=DATA_DIR, help="data 目录路径")
    parser.add_argument("sample_dir", nargs="?", default=None, help="sample 目录路径")
    args = parser.parse_args()
    exit(run(args.data_dir, args.sample_dir))


if __name__ == "__main__":
    main()
