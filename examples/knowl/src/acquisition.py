"""
知识获取程序：使用 LLM 从实验报告中提取结构化知识。

将 assets/acquisition.md 作为目标，调用 DeepSeek API
提取可编码性评分表、模糊点清单、编码问题等结构化数据。
"""

import os
import json
import yaml
from pathlib import Path
from openai import OpenAI


REPORT_PATH = Path(__file__).resolve().parent.parent / "assets" / "acquisition.md"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"

SYSTEM_PROMPT = """你是一个知识提取工具。从实验报告中提取结构化知识，输出 JSON。

提取内容：
1. rules: 可编码性评分表中的每条规则（name, source, score, reason）
2. rate: 可编码率数值
3. ambiguities: 模糊点清单（category, description）
4. issues: 编码发现的问题（number, title, source, problem, suggestion）
5. observations: 值得记录的观察列表
6. conclusions: 核心结论列表

输出格式为 JSON，不要包含其他文字。"""


def extract_with_llm(text: str) -> dict:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未设置")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"从以下实验报告中提取结构化知识：\n\n{text}"},
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(resp.choices[0].message.content)


def main():
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    data = extract_with_llm(report_text)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "extracted.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, indent=2, sort_keys=False)

    print(f"规则数: {len(data.get('rules', []))}")
    print(f"可编码率: {data.get('rate', 'N/A')}%")
    print(f"模糊点: {len(data.get('ambiguities', []))} 条")
    print(f"编码问题: {len(data.get('issues', []))} 个")
    print(f"\n输出: {OUTPUT_DIR / 'extracted.yaml'}")


if __name__ == "__main__":
    main()
