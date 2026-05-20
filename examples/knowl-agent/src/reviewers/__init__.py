from src.reviewers.ui import clear, header, bold, dim, green, yellow, red, cyan, badge, wait, confirm, subheader
from src.reviewers.data import load_domains, load_reviews, get_review_status
from src.reviewers.ontology_review import run as run_ontology_review
from src.reviewers.instance_review import run as run_instance_review
from src.reviewers.relation_review import run as run_relation_review


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


def run_detection(module_path, title):
    clear()
    header(title)
    print(f"  运行 {dim(module_path)} ...\n")
    try:
        import importlib
        mod = importlib.import_module(module_path)
        result = mod.run()
        if result:
            print(yellow(f"退出码: {result}"))
    except Exception as e:
        print(red(f"错误: {e}"))
    wait()


def select_domain(domains, entity_type, review_func):
    clear()
    header(f"选择领域 — {entity_type}评审")
    for i, d in enumerate(domains, 1):
        items = {"本体": d["ontologies"], "实例": d["instances"], "关系": d["relations"]}
        items_key = {"本体": "ontology", "实例": "instance", "关系": "relation"}
        n_pending = 0
        for item in items[entity_type]:
            key = f"{d['dir']}:{items_key[entity_type]}:{item['id']}"
            s, _ = get_review_status(load_reviews(), key)
            if s == "待评审":
                n_pending += 1
        print(f"  {i}. {d['dir']}  {dim(f'({n_pending} 项待评审)')}")
    sel = input(dim("\n  选择领域 (0 返回): ")).strip()
    if sel.isdigit() and 1 <= int(sel) <= len(domains):
        review_func(domains[int(sel) - 1])


def main():
    domains = load_domains()
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
        print(f"  {bold('6.')} 运行跨领域融合检测  {dim('(fusion_check)')}")
        print(f"  {bold('7.')} 运行未定义术语检查  {dim('(find_undefined)')}")
        print(f"  {'─' * 30}")
        print(f"  {bold('0.')} 退出")
        choice = input(dim("\n  请选择: ")).strip()

        if choice == "1":
            select_domain(domains, "本体", run_ontology_review)
        elif choice == "2":
            select_domain(domains, "实例", run_instance_review)
        elif choice == "3":
            select_domain(domains, "关系", run_relation_review)
        elif choice == "4":
            view_review_summary(domains, reviews)
        elif choice == "5":
            from src.reviewers.data import REVIEW_FILE
            if confirm("确定要重置所有评审记录"):
                if REVIEW_FILE.exists():
                    REVIEW_FILE.unlink()
                print("  已重置")
                wait()
        elif choice == "6":
            run_detection("src.validators.fusion_check", "跨领域融合检测")
        elif choice == "7":
            run_detection("src.validators.find_undefined", "未定义术语检查")
        elif choice == "0":
            clear()
            print("再见。")
            break


if __name__ == "__main__":
    main()
