#!/bin/bash
# 依赖: bash 3+, jq, grep
# 检查 ontology pattern 的抽象度——扫描未抽象信号
# Usage: ./scripts/check-abstraction.sh [data/]

BASE=${1:-data}
ERRORS=0

echo "====== 本体抽象度检测 ======"
echo ""

for domain_dir in "$BASE"/*/; do
  domain=$(basename "$domain_dir")
  ontologies_file="$domain_dir/ontologies.json"

  if [ ! -f "$ontologies_file" ]; then
    continue
  fi

  echo "=== $domain ==="

  while IFS=$'\t' read -r id pattern; do
    signals=""

    # 信号1: 包含源文件引用
    if echo "$pattern" | grep -qE '见\s+\S+\.md'; then
      signals="$signals [源文件引用见.*.md]"
    fi

    # 信号2: 包含《》书名号引用
    if echo "$pattern" | grep -qE '《[^》]+》'; then
      signals="$signals [书名号引用]"
    fi

    # 信号3: 包含具体角色名/人名（中文常见角色模式）
    if echo "$pattern" | grep -qE '(项目经理|商务经理|数据工程师|总经理|总监|主管|总裁|副总裁|董事|秘书长|部门秘书|实训生|实习生|培训生|管培生|公司代表)'; then
      signals="$signals [具体角色名]"
    fi

    # 信号4: 包含具体等级编码
    if echo "$pattern" | grep -qE '\b(L[0-9]|M[0-9]|T序列|M序列)\b'; then
      signals="$signals [具体等级编码]"
    fi

    # 信号5: 包含具体数字约束（天数、字数、次数等）
    if echo "$pattern" | grep -qE '[零一二三四五六七八九十百千]+[日天个小时份]|三十日|五个工作'; then
      signals="$signals [具体数字约束]"
    fi

    if [ -n "$signals" ]; then
      echo "  [检测到] $id:$signals"
      ERRORS=$((ERRORS + 1))
    else
      echo "  [通过]   $id"
    fi
  done < <(jq -r '.ontologies[] | [.id, .pattern] | @tsv' "$ontologies_file" 2>/dev/null || true)

  echo ""
done

echo "====== 汇总 ======"
if [ $ERRORS -eq 0 ]; then
  echo "所有本体 pattern 通过抽象度检测"
else
  echo "共检测到 $ERRORS 个未抽象信号"
fi
