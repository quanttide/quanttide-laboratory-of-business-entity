#!/usr/bin/env python3
"""交互式知识库评审工具"""

import json
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = BASE_DIR / "sample"
SCRIPTS_DIR = BASE_DIR / "scripts"
REVIEW_FILE = DATA_DIR / ".review.json"


# ── 数据加载 ──────────────────────────────────────────────

def load_json(path):
    with open(path) as f:
        return json.load(f)


def get_domains():
    domains = []
    if not DATA_DIR.exists():
        return domains
    for d in sorted(DATA_DIR.iterdir()):
        if d.is_dir() and (d / "domain.json").exists():
            info = load_json(d / "domain.json")
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


# ── 评审数据 ──────────────────────────────────────────────

def load_reviews():
    if REVIEW_FILE.exists():
        with open(REVIEW_FILE) as f:
            return json.load(f)
    return {}


def save_reviews(reviews):
    REVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REVIEW_FILE, "w") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


def get_review_status(reviews, key):
    r = reviews.get(key, {})
    return r.get("status", "待评审"), r.get("comment", "")


def set_review_status(reviews, key, status, comment=""):
    reviews[key] = {"status": status, "comment": comment, "updated": datetime.now().isoformat()}


# ── 终端 ──────────────────────────────────────────────────

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


def red(text):
    return t("31", text)


def header(title):
    w = shutil.get_terminal_size().columns
    print()
    print(green("=" * w))
    print(green(f"  {title}"))
    print(green("=" * w))


def subheader(title):
    print()
    print(cyan(f"── {title}"))


def badge(status):
    return {"待评审": yellow("○ 待评审"), "通过": green("✓ 通过"), "需修改": red("✗ 需修改")}.get(status, status)


def wait():
    input(dim("\n按 Enter 继续..."))


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def confirm(prompt):
    return input(f"\n  {prompt} (y/n): ").strip().lower() == "y"


def ask_comment():
    c = input(f"  意见（可选，直接 Enter 跳过）: ").strip()
    return c


# ── 总览 ──────────────────────────────────────────────────

def show_overview(domains, reviews):
    header("知识库评审")
    print(f"  {'领域':<12} {'文件':>4} {'本体':>4} {'实例':>4} {'关系':>4}")
    print(f"  {'─'*12} {'─'*4} {'─'*4} {'─'*4} {'─'*4}")
    for d in domains:
        nf = len(d["info"].get("files", []))
        no = len(d["ontologies"])
        ni = len(d["instances"])
        nr = len(d["relations"])
        print(f"  {d['dir']:<12} {nf:>4} {no:>4} {ni:>4} {nr:>4}")

    total_items = sum(len(d["ontologies"]) + len(d["instances"]) + len(d["relations"]) for d in domains)
    reviewed = sum(1 for v in reviews.values() if v.get("status") == "通过")
    flagged = sum(1 for v in reviews.values() if v.get("status") == "需修改")
    print(f"\n  评审进度：{reviewed} 项已通过  {flagged} 项需修改  {total_items - reviewed - flagged} 项待评审")


# ── 逐项评审 ──────────────────────────────────────────────

def review_entity(entity_type, entity, reviews):
    """评审单个实体，返回是否继续"""
    key = entity.get("id") or entity.get("subject") or entity.get("name", "")
    domain_key = entity.get("_domain", "")
    full_key = f"{domain_key}:{entity_type}:{key}"
    status, comment = get_review_status(reviews, full_key)
    return full_key


def print_status_line(full_key, reviews):
    s, c = get_review_status(reviews, full_key)
    badge_str = badge(s)
    if c:
        print(f"  {badge_str}  {dim(f'意见: {c}')}")
    else:
        print(f"  {badge_str}")


def review_ontologies(domain):
    reviews = load_reviews()
    for o in domain["ontologies"]:
        key = f"{domain['dir']}:ontology:{o['id']}"
        s, c = get_review_status(reviews, key)
        if s != "待评审":
            continue
        clear()
        header(f"本体评审 — {domain['dir']}")
        print(f"\n  {bold(o['label'])}")
        print(f"  视角：{o.get('perspective', '')}")
        print(f"  描述：{o.get('description', '')}")
        if o.get("pattern"):
            print(f"\n  {bold('模式：')}")
            print(f"    {o['pattern']}")
        if o.get("source_files"):
            print(f"\n  来源文件：{', '.join(o['source_files'])}")
        print(f"\n  {dim('---')}")
        act = input(f"  [a]通过  [s]需修改  [p]跳过  [q]退出评审: ").strip().lower()
        if act == "q":
            break
        elif act == "a":
            cmt = ask_comment()
            set_review_status(reviews, key, "通过", cmt)
            save_reviews(reviews)
        elif act == "s":
            cmt = input(f"  请说明问题: ").strip()
            set_review_status(reviews, key, "需修改", cmt)
            save_reviews(reviews)


def review_instances(domain):
    reviews = load_reviews()
    for inst in domain["instances"]:
        key = f"{domain['dir']}:instance:{inst['id']}"
        s, c = get_review_status(reviews, key)
        if s != "待评审":
            continue
        clear()
        header(f"实例评审 — {domain['dir']}")
        onto_label = next((o.get("label", o["name"]) for o in domain["ontologies"] if o["id"] == inst.get("ontology")), inst.get("ontology", ""))
        print(f"\n  本体：{onto_label}")
        print(f"  主题：{bold(inst.get('subject', ''))}")
        src = f"{inst.get('source', '')} {inst.get('article', '')}".strip()
        if src:
            print(f"  来源：{src}")

        for key_field in ["authority", "responsibility", "rule", "principle",
                          "identities", "stages", "levels", "tracks",
                          "requirements", "exclusions", "triggers",
                          "description"]:
            val = inst.get(key_field)
            if val:
                label = {"authority": "职权", "responsibility": "职责", "rule": "规则",
                         "principle": "原则", "identities": "身份", "stages": "阶段",
                         "levels": "等级", "tracks": "通道", "requirements": "要求",
                         "exclusions": "排除", "triggers": "触发条件",
                         "description": "说明"}.get(key_field, key_field)
                print(f"\n  {bold(f'{label}：')}")
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            for sk, sv in item.items():
                                print(f"    · {sk}: {sv}")
                        else:
                            print(f"    · {item}")
                else:
                    print(f"    {val}")
                break

        # 显示其他非关键字段
        shown_keys = {"id", "ontology", "subject", "source", "article",
                      "authority", "responsibility", "rule", "principle",
                      "identities", "stages", "levels", "tracks",
                      "requirements", "exclusions", "triggers", "description",
                      "risks", "controls", "rules", "prohibition",
                      "handover_items", "succession_priority", "assessment_content",
                      "risk_items", "violations", "_domain"}
        other = {k: v for k, v in inst.items() if k not in shown_keys}
        if other:
            print(f"\n  {bold('其他信息：')}")
            for k, v in other.items():
                if isinstance(v, list):
                    print(f"    {k}:")
                    for item in v[:5]:
                        print(f"      · {item}")
                elif isinstance(v, dict):
                    print(f"    {k}: {json.dumps(v, ensure_ascii=False)}")
                else:
                    print(f"    {k}: {v}")

        print(f"\n  {dim('---')}")
        act = input(f"  [a]通过  [s]需修改  [p]跳过  [q]退出评审: ").strip().lower()
        if act == "q":
            break
        elif act == "a":
            cmt = ask_comment()
            set_review_status(reviews, key, "通过", cmt)
            save_reviews(reviews)
        elif act == "s":
            cmt = input(f"  请说明问题: ").strip()
            set_review_status(reviews, key, "需修改", cmt)
            save_reviews(reviews)


def review_relations(domain):
    reviews = load_reviews()
    for r in domain["relations"]:
        key = f"{domain['dir']}:relation:{r['id']}"
        s, c = get_review_status(reviews, key)
        if s != "待评审":
            continue
        clear()
        header(f"关系评审 — {domain['dir']}")
        src_label = r.get("source_instance", "") or r.get("source_ontology", "")
        tgt_label = r.get("target_instance", "") or r.get("target_ontology", "")
        rel_type = r.get("relation", "")
        print(f"\n  {bold(src_label)}  {dim(f'─{rel_type}→')}  {bold(tgt_label)}")
        print(f"  描述：{r.get('description', '')}")
        if r.get("detail"):
            print(f"  详情：{r['detail']}")
        print(f"\n  {dim('---')}")
        act = input(f"  [a]通过  [s]需修改  [p]跳过  [q]退出评审: ").strip().lower()
        if act == "q":
            break
        elif act == "a":
            cmt = ask_comment()
            set_review_status(reviews, key, "通过", cmt)
            save_reviews(reviews)
        elif act == "s":
            cmt = input(f"  请说明问题: ").strip()
            set_review_status(reviews, key, "需修改", cmt)
            save_reviews(reviews)


# ── 查看结果 ──────────────────────────────────────────────

def view_review_summary(domains, reviews):
    clear()
    header("评审汇总")
    for d in domains:
        print(f"\n{cyan(d['dir'])}")
        for o in d["ontologies"]:
            key = f"{d['dir']}:ontology:{o['id']}"
            s, c = get_review_status(reviews, key)
            print(f"  本体 {o.get('label', o['name']):20} {badge(s)}" + (f"  {dim(c)}" if c else ""))
        for inst in d["instances"]:
            key = f"{d['dir']}:instance:{inst['id']}"
            s, c = get_review_status(reviews, key)
            print(f"  实例 {inst.get('subject','')[:20]:20} {badge(s)}" + (f"  {dim(c)}" if c else ""))
        for r in d["relations"]:
            key = f"{d['dir']}:relation:{r['id']}"
            s, c = get_review_status(reviews, key)
            print(f"  关系 {r.get('relation','')[:20]:20} {badge(s)}" + (f"  {dim(c)}" if c else ""))
    wait()


# ── 运行脚本 ──────────────────────────────────────────────

def run_script(name, title):
    clear()
    header(title)
    print(f"  运行 {dim(f'scripts/{name}')} ...\n")
    result = subprocess.run(
        ["bash", str(SCRIPTS_DIR / name)],
        capture_output=True, text=True, cwd=BASE_DIR
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(yellow(result.stderr))
    wait()


# ── 主菜单 ──────────────────────────────────────────────

def main():
    domains = get_domains()
    if not domains:
        print("未找到领域数据，请先运行知识发现流程。")
        return

    while True:
        reviews = load_reviews()
        clear()
        header("知识库评审工具")
        show_overview(domains, reviews)
        print(f"\n  {bold('1.')} 逐项评审 — 本体")
        print(f"  {bold('2.')} 逐项评审 — 实例")
        print(f"  {bold('3.')} 逐项评审 — 关系")
        print(f"  {'─' * 30}")
        print(f"  {bold('4.')} 查看评审汇总")
        print(f"  {bold('5.')} 重置评审记录")
        print(f"  {'─' * 30}")
        print(f"  {bold('6.')} 运行跨领域融合检测  {dim('(fusion-check.sh)')}")
        print(f"  {bold('7.')} 运行未定义术语检查  {dim('(find-undefined-terms.sh)')}")
        print(f"  {'─' * 30}")
        print(f"  {bold('0.')} 退出")
        choice = input(dim("\n  请选择: ")).strip()

        if choice == "1":
            clear()
            header("选择领域 — 本体评审")
            for i, d in enumerate(domains, 1):
                n_pending = sum(1 for o in d["ontologies"]
                                if get_review_status(reviews, f"{d['dir']}:ontology:{o['id']}")[0] == "待评审")
                print(f"  {i}. {d['dir']}  {dim(f'({n_pending} 项待评审)')}")
            sel = input(dim("\n  选择领域 (0 返回): ")).strip()
            if sel.isdigit() and 1 <= int(sel) <= len(domains):
                review_ontologies(domains[int(sel) - 1])
        elif choice == "2":
            clear()
            header("选择领域 — 实例评审")
            for i, d in enumerate(domains, 1):
                n_pending = sum(1 for inst in d["instances"]
                                if get_review_status(reviews, f"{d['dir']}:instance:{inst['id']}")[0] == "待评审")
                print(f"  {i}. {d['dir']}  {dim(f'({n_pending} 项待评审)')}")
            sel = input(dim("\n  选择领域 (0 返回): ")).strip()
            if sel.isdigit() and 1 <= int(sel) <= len(domains):
                review_instances(domains[int(sel) - 1])
        elif choice == "3":
            clear()
            header("选择领域 — 关系评审")
            for i, d in enumerate(domains, 1):
                n_pending = sum(1 for r in d["relations"]
                                if get_review_status(reviews, f"{d['dir']}:relation:{r['id']}")[0] == "待评审")
                print(f"  {i}. {d['dir']}  {dim(f'({n_pending} 项待评审)')}")
            sel = input(dim("\n  选择领域 (0 返回): ")).strip()
            if sel.isdigit() and 1 <= int(sel) <= len(domains):
                review_relations(domains[int(sel) - 1])
        elif choice == "4":
            view_review_summary(domains, reviews)
        elif choice == "5":
            if confirm("确定要重置所有评审记录"):
                if REVIEW_FILE.exists():
                    REVIEW_FILE.unlink()
                print("  已重置")
                wait()
        elif choice == "6":
            run_script("fusion-check.sh", "跨领域融合检测")
        elif choice == "7":
            run_script("find-undefined-terms.sh", "未定义术语检查")
        elif choice == "0":
            clear()
            print("再见。")
            break


if __name__ == "__main__":
    main()
