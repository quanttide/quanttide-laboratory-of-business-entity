#!/usr/bin/env python3
"""Bug is Feature —— 战略假设压力测试机。"""

import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path

from quanttide_agent import LLM
from quanttide_agent.config import settings

DATA_DIR = Path(__file__).parent
HYPOTHESES_FILE = DATA_DIR / "hypotheses.json"
CONTEXT_FILE = DATA_DIR / "context.json"

LLM_CLIENT = LLM(
    model=settings.llm_model or "deepseek-chat",
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
)


def load_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_json(path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_hypotheses():
    return load_json(HYPOTHESES_FILE) if HYPOTHESES_FILE.exists() else []


def save_hypotheses(h):
    save_json(HYPOTHESES_FILE, h)


def load_context():
    return load_json(CONTEXT_FILE)


def save_context(c):
    save_json(CONTEXT_FILE, c)


# System 1: 正常战略分析
SYS1 = """你是一个战略顾问。基于用户的战略上下文，给出正常的战略分析和建议。

要求：
1. 分析当前的战略处境
2. 给出合理的建议
3. 说明你的推导逻辑
4. 输出 JSON：{"analysis": "...", "advice": "...", "rationale": "..."}"""

# System 2: 提取假设
SYS2 = """分析上面的战略分析，列出它依赖的重要假设。

按内部假设（公司自身能力/资源/团队）和外部假设（市场/客户/竞争/技术）分类。

不要评判对错，只需要完整列举。

输出 JSON：{"hypotheses": [{"statement": "假设内容", "type": "internal", "why_matters": "为何重要"}, {"statement": "...", "type": "external", "why_matters": "..."}]}

战略分析：
ANALYSIS_PLACEHOLDER

战略建议：
ADVICE_PLACEHOLDER

推导逻辑：
RATIONALE_PLACEHOLDER"""


def system1(context_text):
    resp = LLM_CLIENT.complete(
        f"{SYS1}\n\n用户的战略上下文：\n{context_text}",
        temperature=0.5,
        max_tokens=1500,
    )
    c = _parse(resp.content.strip())
    return c.get("analysis", ""), c.get("advice", ""), c.get("rationale", "")


def system2(analysis, advice, rationale):
    prompt = (
        SYS2.replace("ANALYSIS_PLACEHOLDER", analysis)
        .replace("ADVICE_PLACEHOLDER", advice)
        .replace("RATIONALE_PLACEHOLDER", rationale)
    )
    print(f"DEBUG: prompt length={len(prompt)}", file=sys.stderr)
    resp = LLM_CLIENT.complete(prompt, temperature=0.5, max_tokens=2000)
    print(f"DEBUG: raw response={resp.content[:200]}", file=sys.stderr)
    c = _parse(resp.content.strip())
    result = c.get("hypotheses", [])
    print(f"DEBUG: parsed hypotheses count={len(result)}", file=sys.stderr)
    return result


def _parse(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n", 1)
        text = lines[1] if len(lines) > 1 else text
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON parse error: {e}", file=sys.stderr)
        print(f"DEBUG: text={text[:300]}", file=sys.stderr)
        return {}


# CLI commands
def cmd_new(context_file=None):
    print("\n=== Bug is Feature ===\n")
    ctx = load_context()
    if context_file:
        raw = json.loads(Path(context_file).read_text())
        ctx = {
            "company": raw.get("corporate_strategy", {}).get("direction", ""),
            "businesses": [
                {"name": b["name"], "challenge": b.get("challenge", "")}
                for b in raw.get("business_strategy", [])
            ],
        }
        save_context(ctx)
        print(f"已从 {context_file} 加载上下文\n")
    elif not ctx:
        ctx["company"] = input("公司方向：").strip()
        ctx["businesses"] = []
        while True:
            name = input("  业务线名称（留空结束）：").strip()
            if not name:
                break
            challenge = input(f"  {name} 的挑战：").strip()
            ctx["businesses"].append({"name": name, "challenge": challenge})
        save_context(ctx)

    context_text = f"公司方向：{ctx['company']}\n" + "\n".join(
        f"业务 - {b['name']}：{b['challenge']}" for b in ctx.get("businesses", [])
    )

    print("System 1 -- 正常战略分析...")
    analysis, advice, rationale = system1(context_text)
    print(f"\n{'=' * 50}")
    print("分析：", textwrap.fill(analysis, width=60))
    print("\n建议：", textwrap.fill(advice, width=60))
    print("\n推导逻辑：", textwrap.fill(rationale, width=60))
    print(f"{'=' * 50}\n")

    print("System 2 -- 提取假设...")
    hypotheses = system2(analysis, advice, rationale)
    print(f"\n发现 {len(hypotheses)} 个假设\n")

    validated = []
    for h in hypotheses:
        s = h.get("statement", "")
        t = h.get("type", "")
        w = h.get("why_matters", "")
        print(f"  [{t}] {s}")
        print(f"  为什么重要：{w}\n")
        validated.append(
            {
                "statement": s,
                "type": t,
                "why_matters": w,
                "verdict": "uncertain",
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )

    all_h = load_hypotheses()
    all_h.extend(validated)
    save_hypotheses(all_h)
    print(f"已保存 {len(validated)} 条假设\n")


def cmd_list():
    h = load_hypotheses()
    if not h:
        print("假设库为空。")
        return
    print(f"\n假设库 ({len(h)} 条)\n")
    for i, item in enumerate(h, 1):
        s = {"confirmed": "Y", "rejected": "N", "uncertain": "?"}.get(
            item.get("verdict", ""), "?"
        )
        t = item.get("type", "")
        print(f"{s} [{t}] [{item.get('date', '?')}] {item['statement']}")
        w = item.get("why_matters", "")
        if w:
            print(f"   为什么重要：{w[:80]}...")
        print()


def cmd_stats():
    h = load_hypotheses()
    if not h:
        print("假设库为空。")
        return
    internal = sum(1 for x in h if x.get("type", "") == "internal")
    external = sum(1 for x in h if x.get("type", "") == "external")
    print(f"\n总计：{len(h)} 条（内部 {internal} / 外部 {external}）")
    print(f"  Y 已确认：{sum(1 for x in h if x['verdict'] == 'confirmed')}")
    print(f"  N 已排除：{sum(1 for x in h if x['verdict'] == 'rejected')}")
    print(f"  ? 待验证：{sum(1 for x in h if x['verdict'] == 'uncertain')}")


def cmd_help():
    print("""Bug is Feature -- 战略假设压力测试机

用法：./strategy.py <命令>

命令：
  new [file]  发起推演（可指定 JSON 上下文文件）
  list        查看假设库
  stats       假设库统计
  help        显示帮助
""")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        cmd_help()
        return
    cmd = sys.argv[1]
    if cmd == "new":
        cmd_new(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "list":
        cmd_list()
    elif cmd == "stats":
        cmd_stats()
    else:
        cmd_help()


if __name__ == "__main__":
    main()
