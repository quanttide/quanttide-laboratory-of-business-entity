from src.reviewers.ui import clear, header, bold, dim, ask_comment
from src.reviewers.data import load_reviews, get_review_status, set_review_status, save_reviews


def run(domain):
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
