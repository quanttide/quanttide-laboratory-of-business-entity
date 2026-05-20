#!/usr/bin/env python3
"""知识工程智能体 — 统一 CLI 入口"""

import sys
import argparse


def main():
    if len(sys.argv) < 2:
        print("用法: python -m src.cli <command> [args...]")
        print("")
        print("命令:")
        print("  summary                 领域概况统计")
        print("  validate                领域目录结构完整性验证")
        print("  auto-fix                骨架文件自动补全")
        print("  check-abstraction       本体抽象度检测")
        print("  cross-domain-report     跨领域关系覆盖率报告")
        print("  find-undefined-terms    未定义术语扫描 <sample_dir> [data_dir]")
        print("  fusion-check            跨领域融合检测 [data_dir] [sample_dir]")
        print("  detect-domain           推荐所属领域 <file>")
        print("  init-domain             初始化新领域 <domain_name> [--from-detect <file>]")
        return 1

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "summary":
        from src.reporters.summary import run
        return run(*args)

    elif command == "validate":
        from src.validators.validate import run
        return run(*args)

    elif command == "auto-fix":
        from src.validators.auto_fix import run
        return run(*args)

    elif command == "check-abstraction":
        from src.reporters.abstraction import run
        return run(*args)

    elif command == "cross-domain-report":
        from src.reporters.cross_domain import run
        return run(*args)

    elif command == "find-undefined-terms":
        from src.validators.find_undefined import run
        return run(*args)

    elif command == "fusion-check":
        from src.validators.fusion_check import run
        return run(*args)

    elif command == "detect-domain":
        from src.detectors.detect_domain import run
        if not args:
            print("用法: python -m src.cli detect-domain <file>")
            return 1
        return run(args[0])

    elif command == "init-domain":
        from src.detectors.init_domain import run
        if not args:
            print("用法: python -m src.cli init-domain <domain_name> [--from-detect <file>]")
            return 1
        kwargs = {"domain_name": args[0]}
        if "--from-detect" in args:
            idx = args.index("--from-detect")
            if idx + 1 < len(args):
                kwargs["from_detect_file"] = args[idx + 1]
        return run(**kwargs)

    else:
        print(f"未知命令: {command}")
        return 1


if __name__ == "__main__":
    exit(main())
