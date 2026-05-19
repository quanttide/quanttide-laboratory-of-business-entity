#!/usr/bin/env python3
"""交互式知识库评审工具"""

import json
import os
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = BASE_DIR / "sample"
SCRIPTS_DIR = BASE_DIR / "scripts"


# ── 数据加载 ──────────────────────────────────────────────

def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_domains():
    domains = []
    if not DATA_DIR.exists():
        return domains
    for d in sorted(DATA_DIR.iterdir()):
        if d.is_dir():
            domain_file = d / "domain.json"
            if domain_file.exists():
                info = load_json(domain_file)
                ont = load_json(d / "ontologies.json")
                inst = load_json(d / "instances.json")
                rel = load_json(d / "relations.json")
                domains.append({
                    "dir": d.name,
                    "info": info,
                    "ontologies": ont["ontologies"],
                    "instances": inst["instances"],
                    "relations": rel["relations"],
                })
    return domains


# ── 终端渲染 ──────────────────────────────────────────────

def t(code, text):
    return f"\033[{code}m{text}\033[0m"


def bold(text):
    return t("1", text)


def dim(text):
    return t("2", text)


def green(text):
    return t("32", text)


def yellow(text):
    return t("33", text)


def cyan(text):
    return t("36", text)


def header(text):
    w = shutil.get_terminal_size().columns
    print()
    print(green("=" * w))
    print(green(f"  {text}"))
    print(green("=" * w))


def subheader(text):
    print()
    print(cyan(f"── {text} ──"))


def wait():
    input(dim("\n按 Enter 继续..."))


def clear():
    os.system("clear" if os.name == "posix" else "cls")


# ── 领域总览 ──────────────────────────────────────────────

def show_overview(domains):
    header("知识库领域总览")
    print(f"  {'领域':<12} {'视角':<24} {'文件':>4} {'本体':>4} {'实例':>4} {'关系':>4}")
    print(f"  {'-'*12} {'-'*24} {'-'*4} {'-'*4} {'-'*4} {'-'*4}")
    for d in domains:
        name = d["dir"]
        perspective = d["info"].get("perspective", "")[:22]
        nf = len(d["info"].get("files", []))
        no = len(d["ontologies"])
        ni = len(d["instances"])
        nr = len(d["relations"])
        print(f"  {name:<12} {perspective:<24} {nf:>4} {no:>4} {ni:>4} {nr:>4}")
    print()
    print(f"  共 {len(domains)} 个领域, "
          f"{sum(len(d['info'].get('files',[])) for d in domains)} 个文件, "
          f"{sum(len(d['ontologies']) for d in domains)} 个本体, "
          f"{sum(len(d['instances']) for d in domains)} 个实例, "
          f"{sum(len(d['relations']) for d in domains)} 条关系")


# ── 领域详情 ──────────────────────────────────────────────

def show_domain_info(d):
    subheader(f"领域：{d['dir']}")
    info = d["info"]
    print(f"  名称：{info.get('name', '')}")
    print(f"  视角：{info.get('perspective', '')}")
    print(f"  文件：")
    for f in info.get("files", []):
        print(f"    - {f}")
    print(f"  词汇表 ({len(info.get('vocabulary', []))} 词)：")
    vocab = info.get("vocabulary", [])
    for i in range(0, len(vocab), 6):
        print(f"    {'  '.join(vocab[i:i+6])}")


def show_ontologies(d):
    subheader(f"本体列表 ({len(d['ontologies'])} 个)")
    for i, o in enumerate(d["ontologies"], 1):
        label = f"{i}. {o['name']}"
        print(f"\n  {bold(label)}  {dim(o['id'])}")
        print(f"    视角：{o.get('perspective', '')}")
        print(f"    描述：{o.get('description', '')}")
        if "pattern" in o:
            print(f"    模式：{json.dumps(o['pattern'], ensure_ascii=False, indent=6)}")
        if o.get("source_files"):
            print(f"    来源：{', '.join(o['source_files'])}")


def show_instances(d):
    subheader(f"实例列表 ({len(d['instances'])} 个)")
    # 按本体分组
    by_onto = {}
    for inst in d["instances"]:
        onto = inst.get("ontology", "未知")
        by_onto.setdefault(onto, []).append(inst)
    for onto, insts in by_onto.items():
        onto_name = next((o["name"] for o in d["ontologies"] if o["id"] == onto), onto)
        print(f"\n  {cyan(onto_name)} ({len(insts)} 条)")
        for inst in insts:
            src = f"{inst.get('source', '')} {inst.get('article', '')}".strip()
            subject = inst.get("subject", "")
            print(f"    · {bold(subject)}{f'  {dim(src)}' if src else ''}")
            # 显示关键字段
            for key in ["authority", "responsibility", "rule", "principle",
                        "requirements", "levels", "stages", "tracks"]:
                val = inst.get(key)
                if val:
                    if isinstance(val, list):
                        for item in val[:3]:
                            if isinstance(item, dict):
                                item = item.get("name", item)
                            print(f"      - {item}")
                        if len(val) > 3:
                            print(f"      {dim(f'... 共 {len(val)} 项')}")
                    else:
                        print(f"      {str(val)[:80]}")
                    break


def show_relations(d):
    subheader(f"关系列表 ({len(d['relations'])} 条)")
    for i, r in enumerate(d["relations"], 1):
        label = f"{i}. {r.get('relation', '')}"
        print(f"\n  {bold(label)}")
        print(f"    {r.get('source_instance', '')}  {dim('→')}  {r.get('target_instance', '')}")
        print(f"    描述：{r.get('description', '')}")
        if r.get("detail"):
            print(f"    详情：{r['detail'][:100]}")


def domain_menu(d):
    while True:
        clear()
        header(f"领域：{d['dir']} — {d['info'].get('name', '')}")
        print(f"  1. 领域信息")
        print(f"  2. 本体列表 ({len(d['ontologies'])})")
        print(f"  3. 实例列表 ({len(d['instances'])})")
        print(f"  4. 关系列表 ({len(d['relations'])})")
        print(f"  0. 返回")
        choice = input(dim("\n  请选择: ")).strip()
        clear()
        if choice == "1":
            show_domain_info(d)
            wait()
        elif choice == "2":
            show_ontologies(d)
            wait()
        elif choice == "3":
            show_instances(d)
            wait()
        elif choice == "4":
            show_relations(d)
            wait()
        elif choice == "0":
            break


# ── 跨领域融合 ────────────────────────────────────────────

def show_fusion():
    header("跨领域融合检测")
    print(f"  运行 {dim('scripts/fusion-check.sh')} ...\n")
    result = subprocess.run(
        ["bash", str(SCRIPTS_DIR / "fusion-check.sh")],
        capture_output=True, text=True, cwd=BASE_DIR
    )
    print(result.stdout)
    if result.stderr:
        print(yellow(result.stderr))


# ── 未定义术语 ────────────────────────────────────────────

def show_undefined():
    header("未定义术语检查")
    print(f"  运行 {dim('scripts/find-undefined-terms.sh')} ...\n")
    result = subprocess.run(
        ["bash", str(SCRIPTS_DIR / "find-undefined-terms.sh")],
        capture_output=True, text=True, cwd=BASE_DIR
    )
    print(result.stdout)
    if result.stderr:
        print(yellow(result.stderr))


# ── 主菜单 ────────────────────────────────────────────────

def main():
    domains = get_domains()
    if not domains:
        print("未找到领域数据，请先运行知识发现流程。")
        return

    while True:
        clear()
        header("知识库交互式评审工具")
        show_overview(domains)
        print()
        print(f"  1. 查看具体领域")
        print(f"  2. 跨领域融合检测")
        print(f"  3. 未定义术语检查")
        print(f"  0. 退出")
        choice = input(dim("\n  请选择: ")).strip()

        if choice == "1":
            clear()
            header("选择领域")
            for i, d in enumerate(domains, 1):
                print(f"  {i}. {d['dir']}  {dim(d['info'].get('name', ''))}")
            print(f"  0. 返回")
            sel = input(dim("\n  请选择: ")).strip()
            if sel.isdigit() and 1 <= int(sel) <= len(domains):
                domain_menu(domains[int(sel) - 1])
        elif choice == "2":
            clear()
            show_fusion()
            wait()
        elif choice == "3":
            clear()
            show_undefined()
            wait()
        elif choice == "0":
            clear()
            print("再见。")
            break


if __name__ == "__main__":
    main()
