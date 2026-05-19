#!/bin/bash
# 依赖: bash 3+, jq
# 统计每个领域的跨领域关系覆盖率
# Usage: ./scripts/cross-domain-report.sh [data/]

BASE=${1:-data}

echo "====== 跨领域关系覆盖率报告 ======"
echo ""

total_cross=0

for domain_dir in "$BASE"/*/; do
  domain=$(basename "$domain_dir")
  relations_file="$domain_dir/relations.json"

  if [ ! -f "$relations_file" ]; then
    continue
  fi

  # 统计跨领域关系（target_ontology 包含 ":" 的表示跨域引用）
  cross_count=$(jq '[.relations[] | select(.target_ontology | contains(":"))] | length' "$relations_file" 2>/dev/null || echo 0)

  # 列出跨域关系详情
  if [ "$cross_count" -gt 0 ]; then
    echo "=== $domain ==="
    echo "  跨域关系数: $cross_count"
    echo ""
    jq -r '.relations[] | select(.target_ontology | contains(":")) | "  [\(.relation)] \(.source_ontology) → \(.target_ontology): \(.description)"' "$relations_file" 2>/dev/null
    echo ""
  fi

  total_cross=$((total_cross + cross_count))
done

echo "====== 汇总 ======"
echo "跨域关系总数: $total_cross"

# 按目标领域分类统计
echo ""
echo "--- 各领域跨域关系明细 ---"
for domain_dir in "$BASE"/*/; do
  domain=$(basename "$domain_dir")
  relations_file="$domain_dir/relations.json"
  [ ! -f "$relations_file" ] && continue

  cross_count=$(jq '[.relations[] | select(.target_ontology | contains(":"))] | length' "$relations_file" 2>/dev/null || echo 0)

  if [ "$cross_count" -gt 0 ]; then
    echo "$domain: $cross_count 条跨域关系"
    jq -r '.relations[] | select(.target_ontology | contains(":")) | "    源: \(.source_ontology) → 目标: \(.target_ontology)"' "$relations_file" 2>/dev/null
  else
    echo "$domain: 0 条跨域关系"
  fi
done

echo ""
echo "--- 判断 ---"
for domain_dir in "$BASE"/*/; do
  domain=$(basename "$domain_dir")
  relations_file="$domain_dir/relations.json"
  [ ! -f "$relations_file" ] && continue

  cross_count=$(jq '[.relations[] | select(.target_ontology | contains(":"))] | length' "$relations_file" 2>/dev/null || echo 0)

  if [ "$cross_count" -ge 2 ]; then
    echo "$domain: ✓ 达标（≥2条）"
  else
    echo "$domain: ✗ 未达标（$cross_count/2）"
  fi
done
