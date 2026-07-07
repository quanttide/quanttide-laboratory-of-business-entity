#!/usr/bin/env python3
"""Bug is Feature —— 战略假设压力测试机。

把 AI 当辩论对手而非算命先生：
AI 抛出的极端观点（Bug）→ 剖析背后的假设（Feature）→ 人类验证 → 存入假设库。

数据存储在本地 ~/.qtstrategy/ 目录。
"""

import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path

from quanttide_agent import LLM
from quanttide_agent.config import settings

DATA_DIR = Path.home() / ".qtstrategy"
LLM_CLIENT = LLM(
    model=settings.llm_model or "deepseek-chat",
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
)

# ── 数据层 ──────────────────────────────────────────────────────

HYPOTHESES_FILE = DATA_DIR / "hypotheses.json"
CONTEXT_FILE = DATA_DIR / "context.json"


def load_hypotheses():
    if HYPOTHESES_FILE.exists():
        return json.loads(HYPOTHESES_FILE.read_text())
    return []


def save_hypotheses(hypotheses):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HYPOTHESES_FILE.write_text(json.dumps(hypotheses, ensure_ascii=False, indent=2))


def load_context():
    if CONTEXT_FILE.exists():
        return json.loads(CONTEXT_FILE.read_text())
    return {}


def save_context(ctx):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps(ctx, ensure_ascii=False, indent=2))


# ── 核心流程 ────────────────────────────────────────────────────

BUG_PROMPT = """你是一个战略"魔鬼代言人"。你的任务不是给出正确建议，而是基于用户的战略上下文，
给出一个极端的、大概率错误的战略建议（Bug）。

要求：
1. 基于用户的战略上下文，顺着市场的宏观逻辑推演到极致
2. 输出一个具体的、可执行的建议（哪怕听起来很疯狂）
3. 用 JSON 输出：{{"bug": "建议内容", "rationale": "你为什么这么建议——你基于什么市场假设/逻辑得出这个结论"}}

不要委婉，不要中庸。极端才有趣。"""

EXTRACT_PROMPT = """分析以下"魔鬼代言人"建议，提取它背后隐藏的假设。
这些假设是 AI 得出这个荒谬结论所依赖的"公理"。

输出 JSON：{{"hypotheses": [{{"statement": "假设描述", "evidence": "AI 的推导逻辑"}}]}}

建议：{bug}
推导逻辑：{rationale}"""


def generate_bug(context_text):
    """Step 1: 让 AI 生成一个极端建议（Bug）"""
    prompt = f"{BUG_PROMPT}\n\n用户的战略上下文：\n{context_text}"
    resp = LLM_CLIENT.complete(prompt, temperature=0.8, max_tokens=1500)
    content = _parse_json(resp.content.strip())
    return content.get("bug", ""), content.get("rationale", "")


def extract_hypotheses(bug, rationale):
    """Step 2: 从 Bug 中提取背后的假设"""
    prompt = EXTRACT_PROMPT.format(bug=bug, rationale=rationale)
    resp = LLM_CLIENT.complete(prompt, temperature=0.3, max_tokens=1500)
    content = _parse_json(resp.content.strip())
    return content.get("hypotheses", [])


def _parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n", 1)
        text = lines[1] if len(lines) > 1 else text
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text) if text else {}


# ── CLI ─────────────────────────────────────────────────────────


def cmd_new(context_file=None):
    """发起一轮新的战略推演"""
    print("\n=== Bug is Feature —— 战略假设压力测试 ===\n")

    # 加载上下文：优先从文件，否则交互输入
    ctx = load_context()
    if context_file:
        raw = json.loads(Path(context_file).read_text())
        company = raw.get("corporate_strategy", {}).get("direction", "")
        ctx = {
            "company": company,
            "businesses": [
                {"name": b["name"], "challenge": b.get("challenge", "")}
                for b in raw.get("business_strategy", [])
            ],
        }
        save_context(ctx)
        print(f"已从 {context_file} 加载上下文\n")
    elif not ctx:
        print("还没有战略上下文。请先输入：")
        ctx["company"] = input("公司方向（如：从项目制转型PaaS）：").strip()
        ctx["businesses"] = []
        while True:
            name = input("  业务线名称（留空结束）：").strip()
            if not name:
                break
            challenge = input(f"  {name} 的挑战：").strip()
            ctx["businesses"].append({"name": name, "challenge": challenge})
        save_context(ctx)
        print()

    context_text = f"公司方向：{ctx['company']}\n"
    for b in ctx["businesses"]:
        context_text += f"业务 - {b['name']}：{b['challenge']}\n"

    # Step 1: 生成 Bug
    print("🤖 正在让 AI 扮演魔鬼代言人...")
    bug, rationale = generate_bug(context_text)
    print(f"\n{'=' * 50}")
    print(f"🐛 BUG（极端建议）：")
    print(textwrap.fill(bug, width=60))
    print(f"\n🤔 它的推导逻辑：")
    print(textwrap.fill(rationale, width=60))
    print(f"{'=' * 50}\n")

    # Step 2: 提取假设
    print("🔍 正在从 Bug 中解剖假设...")
    hypotheses = extract_hypotheses(bug, rationale)
    print(f"\n发现 {len(hypotheses)} 个隐藏假设：\n")

    validated = []
    for h in hypotheses:
        print(f"  假设：{h['statement']}")
        print(f"  来源：{h['evidence']}")
        while True:
            verdict = (
                input("  你的判断 [y=同意/n=不同意/?=不确定/s=跳过]：").strip().lower()
            )
            if verdict in ("y", "n", "?", "s"):
                break
        if verdict == "s":
            print()
            continue
        validated.append(
            {
                "statement": h["statement"],
                "evidence": h["evidence"],
                "verdict": {"y": "confirmed", "n": "rejected", "?": "uncertain"}[
                    verdict
                ],
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        print()

    # Step 3: 存入假设库
    all_h = load_hypotheses()
    all_h.extend(validated)
    save_hypotheses(all_h)
    print(f"✅ 已将 {len(validated)} 条假设存入假设库 ({HYPOTHESES_FILE})\n")


def cmd_list():
    """查看假设库"""
    hypotheses = load_hypotheses()
    if not hypotheses:
        print("假设库为空。运行 `new` 开始一轮推演。")
        return

    print(f"\n=== 假设库 ({len(hypotheses)} 条) ===\n")
    for i, h in enumerate(hypotheses, 1):
        status = {"confirmed": "✅", "rejected": "❌", "uncertain": "❓"}.get(
            h["verdict"], "❓"
        )
        print(f"{status} [{h.get('date', '?')}] {h['statement']}")
        print(f"   来源：{h['evidence'][:80]}...")
        print()


def cmd_context():
    """查看/修改战略上下文"""
    ctx = load_context()
    if not ctx:
        print("还没有上下文。运行 `new` 创建。")
        return

    print(f"\n公司方向：{ctx['company']}")
    for b in ctx.get("businesses", []):
        print(f"  {b['name']}：{b['challenge']}")

    if input("\n重新输入？[y/N]：").strip().lower() == "y":
        os.remove(CONTEXT_FILE)
        cmd_new()


def cmd_stats():
    """查看假设库统计"""
    hypotheses = load_hypotheses()
    if not hypotheses:
        print("假设库为空。")
        return

    confirmed = sum(1 for h in hypotheses if h["verdict"] == "confirmed")
    rejected = sum(1 for h in hypotheses if h["verdict"] == "rejected")
    uncertain = sum(1 for h in hypotheses if h["verdict"] == "uncertain")

    print(f"\n=== 假设库统计 ===")
    print(f"  总计：{len(hypotheses)} 条")
    print(f"  ✅ 已确认：{confirmed}")
    print(f"  ❌ 已排除：{rejected}")
    print(f"  ❓ 待验证：{uncertain}")
    print(f"  确认率：{confirmed / max(len(hypotheses), 1) * 100:.0f}%")
    print()


def cmd_help():
    print("""
Bug is Feature —— 战略假设压力测试机

用法：./docs.py <命令>

命令：
  new      发起一轮新的战略推演（AI 出极端建议 → 提取假设 → 人类验证）
  list     查看假设库
  stats    假设库统计
  context  查看/修改战略上下文
  help     显示本帮助

数据存储在 ~/.qtstrategy/，纯本地 JSON 文件。
""")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) < 2 or sys.argv[1] == "help":
        cmd_help()
        return

    cmd = sys.argv[1]
    if cmd == "new":
        context_file = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_new(context_file)
    elif cmd == "list":
        cmd_list()
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "context":
        cmd_context()
    else:
        cmd_help()


if __name__ == "__main__":
    main()
