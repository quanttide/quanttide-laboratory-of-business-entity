#!/usr/bin/env python3
"""初始化新领域目录和骨架文件"""

import json
import argparse
from pathlib import Path
from src.config import DATA_DIR


SKELETONS = {
    "ontologies.json": {"ontologies": []},
    "instances.json": {"instances": []},
    "relations.json": {"relations": []},
}


def run(domain_name: str, from_detect_file: str = None):
    domain_dir = DATA_DIR / domain_name
    domain_dir.mkdir(parents=True, exist_ok=True)

    domain_json_path = domain_dir / "domain.json"
    if not domain_json_path.exists():
        if from_detect_file:
            filename = Path(from_detect_file).name
            domain_data = {
                "id": domain_name,
                "name": "",
                "perspective": "",
                "files": [f"tests/fixtures/input/{filename}"],
                "vocabulary": [],
            }
            print(f"  [创建] {domain_json_path}（基于 {filename}）")
        else:
            domain_data = {
                "id": domain_name,
                "name": "",
                "perspective": "",
                "files": [],
                "vocabulary": [],
            }
            print(f"  [创建] {domain_json_path}")

        with open(domain_json_path, "w", encoding="utf-8") as f:
            json.dump(domain_data, f, ensure_ascii=False, indent=2)

    for filename, skeleton in SKELETONS.items():
        fpath = domain_dir / filename
        if not fpath.exists():
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(skeleton, f, ensure_ascii=False, indent=2)
            print(f"  [创建] {fpath}")

    print(f"领域 {domain_name} 初始化完成")
    return 0


def main():
    parser = argparse.ArgumentParser(description="初始化新领域目录和骨架文件")
    parser.add_argument("domain_name", help="领域名称")
    parser.add_argument("--from-detect", help="从检测结果创建（指定源文件路径）")
    args = parser.parse_args()
    exit(run(args.domain_name, args.from_detect))


if __name__ == "__main__":
    main()
