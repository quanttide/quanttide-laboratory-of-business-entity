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
    resp = LLM_CLIENT.complete(prompt, temperature=0.5, max_tokens=2000)
    c = _parse(resp.content.strip())
    return c.get("hypotheses", [])


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
    except json.JSONDecodeError:
        return {}


def cmd_new(context_file=None):
    print("\n=== Bug is Feature ===\n")
    ctx = {}
    if context_file:
        raw = json.loads(Path(context_file).read_text())
        ctx = {
            "company": raw.get("corporate_strategy", {}).get("direction", ""),
            "businesses": [
                {"name": b["name"], "challenge": b.get("challenge", "")}
                for b in raw.get("business_strategy", [])
            ],
        }
        print(f"已从 {context_file} 加载上下文\n")
    else:
        ctx["company"] = input("公司方向：").strip()
        ctx["businesses"] = []
        while True:
            name = input("  业务线名称（留空结束）：").strip()
            if not name:
                break
            challenge = input(f"  {name} 的挑战：").strip()
            ctx["businesses"].append({"name": name, "challenge": challenge})

    context_text = f"公司方向：{ctx['company']}\n" + "\n".join(
        f"业务 - {b['name']}：{b['challenge']}" for b in ctx.get("businesses", [])
    )

    print("System 1 -- 正常战略分析...")
    analysis, advice, rationale = system1(context_text)
    print(f"\n分析：{textwrap.fill(analysis, width=60)}")
    print(f"\n建议：{textwrap.fill(advice, width=60)}")
    print(f"\n推导逻辑：{textwrap.fill(rationale, width=60)}\n")

    print("System 2 -- 提取假设...")
    hypotheses = system2(analysis, advice, rationale)
    print(f"发现 {len(hypotheses)} 个假设\n")

    for h in hypotheses:
        s, t, w = h.get("statement", ""), h.get("type", ""), h.get("why_matters", "")
        print(f"  [{t}] {s}")
        print(f"  为什么重要：{w}\n")

    all_h = load_hypotheses()
    for h in hypotheses:
        all_h.append(
            {
                "statement": h.get("statement", ""),
                "type": h.get("type", ""),
                "why_matters": h.get("why_matters", ""),
                "verdict": "uncertain",
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
    save_hypotheses(all_h)
    print(f"已保存 {len(hypotheses)} 条假设。用 `review` 命令逐条判断。\n")


def cmd_review():
    h = load_hypotheses()
    pending = [x for x in h if x.get("verdict") == "uncertain"]
    done = len(h) - len(pending)
    if not pending:
        print(f"没有待验证的假设（共 {len(h)} 条，已判断 {done} 条）。\n")
        return

    print(f"\n待验证假设 ({len(pending)} 条，已判断 {done}/{len(h)})\n")
    for i, item in enumerate(pending, 1):
        print(f"--- {i}. [{item.get('type', '')}] {item['statement']} ---")
        print(f"   为什么重要：{item.get('why_matters', '')}\n")
        verdict = _ask_verdict()
        if verdict == "skip":
            print()
            continue
        evidence = input("  证据（什么数据支持这个判断）：").strip()
        item["verdict"] = verdict
        item["evidence"] = evidence
        item["date"] = datetime.now().strftime("%Y-%m-%d")
        if verdict == "evidence_with_difficulty":
            item["obstacle"] = input("  障碍（什么在阻碍）：").strip()
        print("已记录\n")

    save_hypotheses(h)
    pending_left = sum(1 for x in h if x.get("verdict") == "uncertain")
    print(f"已更新判断。剩余待验证：{pending_left} 条\n")


def _ask_verdict():
    while True:
        v = (
            input("  判断 [y=已确认/n=已排除/d=有证据但有障碍/?=无证据/s=跳过]：")
            .strip()
            .lower()
        )
        if v == "y":
            return "confirmed"
        if v == "n":
            return "rejected"
        if v == "d":
            return "evidence_with_difficulty"
        if v == "?":
            return "no_evidence"
        if v == "s":
            return "skip"


def cmd_report():
    h = load_hypotheses()
    if not h:
        print("假设库为空。\n")
        return

    labels = {
        "confirmed": "已确认",
        "rejected": "已排除",
        "evidence_with_difficulty": "有证据但有障碍",
        "no_evidence": "无证据",
        "uncertain": "待验证",
    }
    status_count = {}
    for x in h:
        v = x.get("verdict", "uncertain")
        status_count[v] = status_count.get(v, 0) + 1

    print(f"\n=== 战略假设验证报告 ===\n")
    print(f"总假设：{len(h)} 条\n")
    for v, c in sorted(status_count.items(), key=lambda kv: -kv[1]):
        print(f"  {labels.get(v, v)}：{c} 条")
    print()

    for item in h:
        v = item.get("verdict", "uncertain")
        icon = {
            "confirmed": "Y",
            "rejected": "N",
            "evidence_with_difficulty": "D",
            "no_evidence": "?",
            "uncertain": "?",
        }.get(v, "?")
        print(f"{icon} [{item.get('type', '')}] {item['statement']}")
        if item.get("evidence"):
            print(f"   证据：{item['evidence'][:100]}...")
        if item.get("obstacle"):
            print(f"   障碍：{item['obstacle'][:100]}...")
        print()


def cmd_list():
    h = load_hypotheses()
    if not h:
        print("假设库为空。\n")
        return
    print(f"\n假设库 ({len(h)} 条)\n")
    for i, item in enumerate(h, 1):
        v = item.get("verdict", "uncertain")
        icon = {
            "confirmed": "Y",
            "rejected": "N",
            "evidence_with_difficulty": "D",
            "no_evidence": "?",
            "uncertain": "?",
        }.get(v, "?")
        print(f"{icon} [{item.get('date', '?')}] {item['statement']}")


def cmd_stats():
    h = load_hypotheses()
    if not h:
        print("假设库为空。\n")
        return
    internal = sum(1 for x in h if x.get("type") == "internal")
    external = sum(1 for x in h if x.get("type") == "external")
    uncertain = sum(1 for x in h if x.get("verdict") == "uncertain")
    confirmed = sum(1 for x in h if x.get("verdict") == "confirmed")
    rejected = sum(1 for x in h if x.get("verdict") == "rejected")
    print(f"\n假设库：{len(h)} 条（内部 {internal} / 外部 {external}）")
    print(f"  Y 已确认：{confirmed}")
    print(f"  N 已排除：{rejected}")
    print(
        f"  D 有障碍：{sum(1 for x in h if x.get('verdict') == 'evidence_with_difficulty')}"
    )
    print(f"  ? 无证据：{sum(1 for x in h if x.get('verdict') == 'no_evidence')}")
    print(f"  ? 待验证：{uncertain}")


def cmd_help():
    print("""Bug is Feature -- 战略假设压力测试机

用法：./strategy.py <命令>

命令：
  new [file]  发起推演（可指定 JSON 上下文文件）
  review      逐条审查待验证的假设
  report      生成假设验证报告
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
    cmds = {
        "new": lambda: cmd_new(sys.argv[2] if len(sys.argv) > 2 else None),
        "review": cmd_review,
        "report": cmd_report,
        "list": cmd_list,
        "stats": cmd_stats,
    }
    cmds.get(cmd, cmd_help)()


if __name__ == "__main__":
    main()
