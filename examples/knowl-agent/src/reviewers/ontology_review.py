from src.reviewers.ui import clear, header, bold, dim, ask_comment
from src.reviewers.data import load_reviews, get_review_status, set_review_status, save_reviews


def run(domain):
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
