#!/usr/bin/env python3
"""
p40 手册质量多维度评估 —— LLM 实现
=======================================
对 quanttide-tech/docs/handbook/ 下的所有 .md 文件，
用 DeepSeek V4 从叙事工程、知识工程、认知工程三个维度打分，
输出结构化 JSON 结果 + 汇总报告。

用法：
  python3 p40-evaluate.py
  python3 p40-evaluate.py --output results.json  # 指定输出路径
  python3 p40-evaluate.py --resume                # 断点续评（读取已有结果继续）
  python3 p40-evaluate.py --quick                 # 快速模式：仅评估 index.md 和非 index 代表文件
"""

import os
import sys
import json
import re
import time
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
HANDBOOK_DIR = os.path.expanduser(
    "~/repos/quanttide/default/quanttide-tech/docs/handbook"
)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODEL = "deepseek-chat"  # DeepSeek V4
BASE_URL = "https://api.deepseek.com/v1"

# 15 个评估指标
METRICS = {
    "narrative_scene_anchor": {
        "dimension": "narrative",
        "label": "叙事·场景锚定",
        "prompt": "评估此手册是否以具体工作场景（而非抽象概念）开头：前三段是否让读者能说清'在什么情况下该用这个手册'？",
    },
    "narrative_role_clarity": {
        "dimension": "narrative",
        "label": "叙事·角色代入",
        "prompt": "评估此手册是否明确说明'谁是执行者、谁是审批者'：手册中的'你'对应哪个具体岗位或角色？",
    },
    "narrative_causal_loop": {
        "dimension": "narrative",
        "label": "叙事·因果闭环",
        "prompt": "评估此手册是否说明了'为什么这么做'：是否有'设计者注''设计理由'类的元注释来解释规则背后的逻辑？",
    },
    "narrative_counterexample": {
        "dimension": "narrative",
        "label": "叙事·反例教育",
        "prompt": "评估此手册是否指出了典型错误做法：是否有'你不得做的事情''常见错误''注意'等约束或警示内容？",
    },
    "narrative_rhythm": {
        "dimension": "narrative",
        "label": "叙事·节奏控制",
        "prompt": "评估此手册的信息密度是否均匀：长段落是否合理分节？关键规则是否用列表、表格等方式突出？有无大段无结构的文字墙？",
    },
    "knowledge_atomicity": {
        "dimension": "knowledge",
        "label": "知识·原子性",
        "prompt": "评估知识是否拆分为最小独立单元：一段话是否包含多个不相关的知识点？内容是否可被独立引用和复用？",
    },
    "knowledge_indexability": {
        "dimension": "knowledge",
        "label": "知识·可索引性",
        "prompt": "评估知识的检索入口是否清晰：如果是 index.md，是否提供了导航功能？如果是子文件，是否被 index.md 引用？",
    },
    "knowledge_hierarchy": {
        "dimension": "knowledge",
        "label": "知识·层级一致性",
        "prompt": "评估章节结构与知识层级是否匹配：标题深度（# → ## → ###）是否反映知识点的从属关系？目录结构是否合理？",
    },
    "knowledge_crossref": {
        "dimension": "knowledge",
        "label": "知识·交叉引用",
        "prompt": "评估知识点之间是否有显式的交叉引用：是否有'详见X章''参照Y手册''相关：[链接]'等关联？",
    },
    "knowledge_version_alignment": {
        "dimension": "knowledge",
        "label": "知识·版本对齐",
        "prompt": "评估手册引用的版本号是否明确且一致：是否有章程/教程版本号？版本号是否可能是过时的？",
    },
    "cognitive_working_memory": {
        "dimension": "cognitive",
        "label": "认知·工作记忆负担",
        "prompt": "评估阅读和执行手册所需的工作记忆：操作步骤是否超过 7±2 项？是否需要同时对照多份其他文档才能理解？是否有检查清单/步骤编号来降低负担？",
    },
    "cognitive_decision_ambiguity": {
        "dimension": "cognitive",
        "label": "认知·决策歧义度",
        "prompt": "评估读者在哪些节点需要自己做判断：是否有'视情况而定''酌情处理'而无判断标准？决策条件是否明确？",
    },
    "cognitive_process_visibility": {
        "dimension": "cognitive",
        "label": "认知·流程可见性",
        "prompt": "评估流程是否可在一页内看清：是否有流程图、时间线、步骤编号或检查清单？整体流程是否直观可见？",
    },
    "cognitive_exception_coverage": {
        "dimension": "cognitive",
        "label": "认知·异常路径覆盖",
        "prompt": "评估是否覆盖了常见异常和边界情况：是否有'如果...则...'的条件分支？是否处理了'出错时怎么办'？",
    },
    "cognitive_progressive_disclosure": {
        "dimension": "cognitive",
        "label": "认知·渐进披露",
        "prompt": "评估复杂知识是否分层呈现：是否有'新手必读''进阶参考''快速上手'等阅读路径区分？内容是否按难度梯度组织？",
    },
}

# 评分标准
SCORE_PROMPT_TEMPLATE = """你是一位专业的文档质量评估师。请对以下工作手册文件进行单一维度的评估。

## 评估指标
{metric_prompt}

## 评分标准
- 5分：优秀 —— 完全满足该指标要求，可作范本
- 4分：良好 —— 基本满足，有少量改进空间
- 3分：及格 —— 部分满足，存在明显不足
- 2分：较差 —— 很少满足，大部分缺失
- 1分：很差 —— 完全不满足或文件内容几乎不存在（如只有标题几行字）

你必须只输出 JSON 格式，不要输出其他内容：
{{
  "score": <整数1-5>,
  "reason": "<一句话解释打分的理由>",
  "evidence": "<从手册原文中摘录的一两句最有说服力的证据>"
}}

## 手册内容
文件路径：{filepath}
文件大小：{filesize} 行 / {chars} 字符

```
{content}
```
"""


def call_llm(prompt: str, retries: int = 3) -> str:
    """调用 DeepSeek V4 API"""
    if not DEEPSEEK_API_KEY:
        return json.dumps({"score": 0, "reason": "API key 未配置", "evidence": ""})

    from openai import OpenAI

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位严格的文档质量评估师。请严格按照评分标准打分，输出纯 JSON。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            text = resp.choices[0].message.content.strip()
            return text
        except Exception as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                return json.dumps({"score": 0, "reason": f"API 调用失败: {e}", "evidence": ""})


def parse_score_response(text: str, metric_key: str) -> dict:
    """解析 LLM 返回的 JSON，提取 score/reason/evidence"""
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # 尝试从文本中提取 JSON 块
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                result = {"score": 0, "reason": f"JSON 解析失败: {text[:200]}", "evidence": ""}
        else:
            result = {"score": 0, "reason": f"JSON 解析失败: {text[:200]}", "evidence": ""}

    # 确保字段存在
    result.setdefault("score", 0)
    result.setdefault("reason", "")
    result.setdefault("evidence", "")

    # 确保分数在 0-5
    score = int(result["score"])
    result["score"] = max(0, min(5, score))

    return result


def evaluate_file(filepath: str) -> dict:
    """对单个文件评估所有 15 个指标"""
    relpath = os.path.relpath(filepath, HANDBOOK_DIR)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"file": relpath, "error": str(e), "metrics": {}}

    lines = content.count("\n") + 1
    chars = len(content)

    # 跳过极短文件（只有标题）
    if chars < 20:
        return {
            "file": relpath,
            "error": None,
            "lines": lines,
            "chars": chars,
            "dimension_scores": {},
            "metrics": {
                k: {"score": 1, "reason": "文件过短（<20字符），无法评估", "evidence": ""}
                for k in METRICS
            },
        }

    # 截断内容（LLM 上下文限制）
    truncated = content[:8000] if len(content) > 8000 else content

    metrics_result = {}
    for metric_key, metric_info in METRICS.items():
        prompt = SCORE_PROMPT_TEMPLATE.format(
            metric_prompt=metric_info["prompt"],
            filepath=relpath,
            filesize=lines,
            chars=chars,
            content=truncated,
        )
        raw_response = call_llm(prompt)
        result = parse_score_response(raw_response, metric_key)
        metrics_result[metric_key] = result

    # 计算维度平均分
    dimension_scores = {"narrative": 0, "knowledge": 0, "cognitive": 0}
    dimension_counts = {"narrative": 0, "knowledge": 0, "cognitive": 0}
    for metric_key, result in metrics_result.items():
        dim = METRICS[metric_key]["dimension"]
        dimension_scores[dim] += result["score"]
        dimension_counts[dim] += 1
    for dim in dimension_scores:
        if dimension_counts[dim] > 0:
            dimension_scores[dim] = round(
                dimension_scores[dim] / dimension_counts[dim], 2
            )

    return {
        "file": relpath,
        "error": None,
        "lines": lines,
        "chars": chars,
        "dimension_scores": dimension_scores,
        "overall_score": round(
            sum(dimension_scores.values()) / len(dimension_scores), 2
        ),
        "metrics": metrics_result,
    }


def get_all_handbook_files() -> list:
    """获取 handbook 下所有 .md 文件（排除 AGENTS/CONTRIBUTING/CHANGELOG 等）"""
    handbook = Path(HANDBOOK_DIR)
    exclude = {"AGENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", "README.md", "ROADMAP.md", ".git", "LICENSE"}
    files = []
    for f in sorted(handbook.rglob("*.md")):
        if f.name in exclude:
            continue
        # 排除 .git 目录下的
        if ".git" in f.parts:
            continue
        files.append(str(f))
    return files


def load_existing_results(path: str) -> dict:
    """加载已有的评估结果（用于断点续评）"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"files": [], "stats": {}}


def save_results(results: dict, path: str):
    """保存结果"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def compute_stats(results: list) -> dict:
    """计算汇总统计"""
    if not results:
        return {}

    total_files = len(results)
    files_with_error = sum(1 for r in results if r.get("error"))
    files_evaluated = total_files - files_with_error

    # 维度平均
    dim_totals = {"narrative": 0, "knowledge": 0, "cognitive": 0}
    overall_total = 0
    overall_count = 0
    for r in results:
        if r.get("error"):
            continue
        for dim in dim_totals:
            dim_totals[dim] += r.get("dimension_scores", {}).get(dim, 0)
        overall_total += r.get("overall_score", 0)
        overall_count += 1

    dim_avg = {}
    for dim in dim_totals:
        dim_avg[dim] = round(dim_totals[dim] / files_evaluated, 2) if files_evaluated else 0

    overall_avg = round(overall_total / overall_count, 2) if overall_count else 0

    # 健康度分布
    health_dist = {"healthy": 0, "moderate": 0, "unhealthy": 0}
    for r in results:
        if r.get("error"):
            continue
        s = r.get("overall_score", 0)
        if s >= 4:
            health_dist["healthy"] += 1
        elif s >= 2.5:
            health_dist["moderate"] += 1
        else:
            health_dist["unhealthy"] += 1

    # 最差/最好文件
    valid = [r for r in results if not r.get("error")]
    best = max(valid, key=lambda r: r.get("overall_score", 0)) if valid else None
    worst = min(valid, key=lambda r: r.get("overall_score", 0)) if valid else None

    # 指标平均分
    metric_avgs = {}
    for mk in METRICS:
        scores = [
            r["metrics"].get(mk, {}).get("score", 0)
            for r in valid
            if mk in r.get("metrics", {})
        ]
        metric_avgs[mk] = round(sum(scores) / len(scores), 2) if scores else 0

    return {
        "total_files": total_files,
        "files_evaluated": files_evaluated,
        "files_with_error": files_with_error,
        "overall_average": overall_avg,
        "dimension_averages": dim_avg,
        "health_distribution": health_dist,
        "best_file": best["file"] if best else None,
        "best_score": best.get("overall_score") if best else None,
        "worst_file": worst["file"] if worst else None,
        "worst_score": worst.get("overall_score") if worst else None,
        "metric_averages": dict(sorted(metric_avgs.items(), key=lambda x: x[1])),
    }


def generate_markdown_report(results: dict) -> str:
    """从 JSON results 生成可读的 Markdown 报告"""
    stats = results.get("stats", {})
    files = results.get("files", [])

    lines = []
    lines.append("# p40 手册质量多维度评估 —— LLM 评估报告\n")
    lines.append(f"> 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"> 评估文件数：{stats.get('files_evaluated', 0)} / {stats.get('total_files', 0)}\n")
    lines.append("")

    # 总览
    lines.append("## 一、总体健康度\n")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 总体平均分 | {stats.get('overall_average', 'N/A')} / 5 |")
    dim_avgs = stats.get("dimension_averages", {})
    lines.append(f"| 叙事工程 | {dim_avgs.get('narrative', 'N/A')} / 5 |")
    lines.append(f"| 知识工程 | {dim_avgs.get('knowledge', 'N/A')} / 5 |")
    lines.append(f"| 认知工程 | {dim_avgs.get('cognitive', 'N/A')} / 5 |")
    lines.append("")
    health = stats.get("health_distribution", {})
    lines.append(f"| 🟢 健康 (≥4.0) | {health.get('healthy', 0)} 个 |")
    lines.append(f"| 🟡 亚健康 (2.5-3.9) | {health.get('moderate', 0)} 个 |")
    lines.append(f"| 🔴 不健康 (<2.5) | {health.get('unhealthy', 0)} 个 |")
    lines.append("")
    lines.append(f"| 🏆 最佳手册 | {stats.get('best_file', 'N/A')} ({stats.get('best_score', 'N/A')}) |")
    lines.append(f"| 😱 最差手册 | {stats.get('worst_file', 'N/A')} ({stats.get('worst_score', 'N/A')}) |")
    lines.append("")

    # 维度分析
    lines.append("## 二、维度深度分析\n")

    for dim_key, dim_label in [
        ("narrative", "叙事工程"),
        ("knowledge", "知识工程"),
        ("cognitive", "认知工程"),
    ]:
        lines.append(f"### {dim_label}\n")
        lines.append(f"维度平均分：**{dim_avgs.get(dim_key, 'N/A')}** / 5\n")

        # 该维度的指标排行
        metric_avgs = stats.get("metric_averages", {})
        dim_metrics = {k: v for k, v in metric_avgs.items() if k.startswith(dim_key)}
        sorted_metrics = sorted(dim_metrics.items(), key=lambda x: x[1])

        lines.append(f"| 指标 | 平均分 |")
        lines.append(f"|------|-------|")
        for mk, avg in sorted_metrics:
            label = METRICS.get(mk, {}).get("label", mk)
            icon = "🟢" if avg >= 4 else ("🟡" if avg >= 2.5 else "🔴")
            lines.append(f"| {icon} {label} | {avg} |")
        lines.append("")

    # 详细文件评分
    lines.append("## 三、按文件评分详情\n")
    lines.append(f"| 文件 | 总分 | 叙事 | 知识 | 认知 | 行数 |")
    lines.append(f"|------|------|------|------|------|------|")
    for f in sorted(files, key=lambda x: x.get("overall_score", 0), reverse=True):
        if f.get("error"):
            lines.append(f"| {f['file']} | ❌ {f['error']} | - | - | - | - |")
            continue
        lines.append(
            f"| {f['file']} | {f.get('overall_score', '')} | "
            f"{f.get('dimension_scores', {}).get('narrative', '')} | "
            f"{f.get('dimension_scores', {}).get('knowledge', '')} | "
            f"{f.get('dimension_scores', {}).get('cognitive', '')} | "
            f"{f.get('lines', '')} |"
        )
    lines.append("")

    # 指标改进建议
    lines.append("## 四、关键改进方向\n")
    metric_avgs = stats.get("metric_averages", {})
    worst_metrics = sorted(metric_avgs.items(), key=lambda x: x[1])[:5]
    lines.append("### 最需改进的 5 个指标\n")
    for mk, avg in worst_metrics:
        label = METRICS.get(mk, {}).get("label", mk)
        dim = METRICS.get(mk, {}).get("dimension", "")
        lines.append(f"- **{label}** ({avg}/5) — 来自 {dim} 维度")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="p40 手册质量多维度评估")
    parser.add_argument("--output", "-o", default="p40-results.json", help="输出 JSON 路径")
    parser.add_argument("--report", "-r", default="p40-report.md", help="输出 Markdown 报告路径")
    parser.add_argument("--resume", action="store_true", help="断点续评")
    parser.add_argument("--quick", action="store_true", help="快速模式：仅评估 index.md 文件")
    parser.add_argument("--limit", type=int, default=0, help="限制评估文件数量（用于测试）")
    args = parser.parse_args()

    if not DEEPSEEK_API_KEY:
        print("错误：DEEPSEEK_API_KEY 环境变量未设置", file=sys.stderr)
        sys.exit(1)

    print(f"📂 手册目录: {HANDBOOK_DIR}")
    print(f"🤖 模型: {MODEL}")
    print()

    # 获取文件列表
    all_files = get_all_handbook_files()

    if args.quick:
        # 快速模式：只评估 index.md
        files_to_eval = [f for f in all_files if f.endswith("index.md")]
        print(f"⚡ 快速模式：仅评估 {len(files_to_eval)} 个 index.md 文件")
    else:
        files_to_eval = all_files
        print(f"📋 共 {len(files_to_eval)} 个文件待评估")

    if args.limit > 0:
        files_to_eval = files_to_eval[: args.limit]
        print(f"🔒 限制为前 {args.limit} 个")

    # 加载已有结果（断点续评）
    existing = {}
    if args.resume and os.path.exists(args.output):
        existing = load_existing_results(args.output)
        existing_files = {e["file"] for e in existing.get("files", [])}
        files_to_eval = [f for f in files_to_eval if os.path.relpath(f, HANDBOOK_DIR) not in existing_files]
        print(f"♻️ 断点续评：跳过 {len(existing.get('files', []))} 个已评估文件，剩余 {len(files_to_eval)} 个")
        results = existing.get("files", [])
    else:
        results = []

    # 逐个评估
    total = len(files_to_eval)
    for i, filepath in enumerate(files_to_eval, 1):
        relpath = os.path.relpath(filepath, HANDBOOK_DIR)
        print(f"  [{i}/{total}] {relpath} ... ", end="", flush=True)
        result = evaluate_file(filepath)
        results.append(result)
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(
                f"✅ 总分={result.get('overall_score', '?')} "
                f"(叙事={result.get('dimension_scores', {}).get('narrative', '?')} "
                f"知识={result.get('dimension_scores', {}).get('knowledge', '?')} "
                f"认知={result.get('dimension_scores', {}).get('cognitive', '?')})"
            )

        # 每次评估后保存中间结果（支持断点续评）
        stats = compute_stats(results)
        save_results({"files": results, "stats": stats}, args.output)

    # 最终统计和报告
    print("\n📊 计算汇总统计...")
    stats = compute_stats(results)
    full_results = {"files": results, "stats": stats}

    # 保存 JSON
    save_results(full_results, args.output)
    print(f"💾 JSON 结果已保存: {args.output}")

    # 生成 Markdown 报告
    report = generate_markdown_report(full_results)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📝 Markdown 报告已保存: {args.report}")

    # 打印摘要
    print(f"\n{'='*50}")
    print(f"📈 评估摘要")
    print(f"{'='*50}")
    print(f"  总文件: {stats.get('total_files', 0)}")
    print(f"  评估成功: {stats.get('files_evaluated', 0)}")
    print(f"  总体平均分: {stats.get('overall_average', 'N/A')} / 5")
    print(f"  叙事工程: {stats.get('dimension_averages', {}).get('narrative', 'N/A')}")
    print(f"  知识工程: {stats.get('dimension_averages', {}).get('knowledge', 'N/A')}")
    print(f"  认知工程: {stats.get('dimension_averages', {}).get('cognitive', 'N/A')}")
    print(f"  🟢 健康: {stats.get('health_distribution', {}).get('healthy', 0)}")
    print(f"  🟡 亚健康: {stats.get('health_distribution', {}).get('moderate', 0)}")
    print(f"  🔴 不健康: {stats.get('health_distribution', {}).get('unhealthy', 0)}")
    if stats.get("best_file"):
        print(f"  🏆 最佳: {stats['best_file']} ({stats['best_score']})")
    if stats.get("worst_file"):
        print(f"  😱 最差: {stats['worst_file']} ({stats['worst_score']})")


if __name__ == "__main__":
    main()
