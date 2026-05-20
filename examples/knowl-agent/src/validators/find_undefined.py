#!/usr/bin/env python3
"""扫描全库加粗术语，对比所有领域定义，找出未定义术语"""

import re
import argparse
from pathlib import Path
from src.config import DATA_DIR, SAMPLE_DIR
from src.loader import load_all_domains


IGNORED_TERMS = {
    "制定依据", "目的", "适用范围", "定义", "章程效力", "解释权",
    "第X条", "第X章",
}
IGNORED_PREFIXES = ("第", "第")
IGNORED_CHAPTER_RE = re.compile(r"^第[一二三四五六七八九十]+条|^第[一二三四五六七八九十]+章")


def collect_defined_terms(sample_dir, data_dir):
    terms = set()
    for d, domain, ontologies, instances, relations in load_all_domains(data_dir):
        for inst in instances:
            for val in [inst.subject, inst.data.get("principle"), inst.data.get("risk"),
                        inst.data.get("element"), inst.data.get("term")]:
                if val:
                    if isinstance(val, str):
                        terms.add(val)
                    elif isinstance(val, list):
                        for v in val:
                            if isinstance(v, str):
                                terms.add(v)
        for v in domain.vocabulary:
            terms.add(v)
    return terms


def run(sample_dir=None, data_dir=None):
    sdir = Path(sample_dir) if sample_dir else SAMPLE_DIR
    defined = collect_defined_terms(sdir, data_dir)
    defined_clean = {t.replace(" ", "") for t in defined}

    print("=== 全库使用但未定义的术语 ===\n")

    found = 0
    for f in sorted(sdir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        bold_terms = set(re.findall(r"\*\*([^*]+)\*\*", content))

        for term in bold_terms:
            term = term.strip()
            if not term or len(term) <= 1:
                continue
            if term in IGNORED_TERMS:
                continue
            if IGNORED_CHAPTER_RE.match(term):
                continue

            term_clean = term.replace(" ", "")
            if term in defined or term_clean in defined_clean:
                continue

            print(f'  {f.name}: 使用了术语 "{term}" 但未在任何 domain 中定义')
            found = 1

    if not found:
        print("  （全部术语已有定义）")
    return 0


def main():
    parser = argparse.ArgumentParser(description="扫描全库加粗术语，找出未定义术语")
    parser.add_argument("sample_dir", nargs="?", default=SAMPLE_DIR, help="sample 目录路径")
    parser.add_argument("data_dir", nargs="?", default=DATA_DIR, help="data 目录路径")
    args = parser.parse_args()
    exit(run(args.sample_dir, args.data_dir))


if __name__ == "__main__":
    main()
