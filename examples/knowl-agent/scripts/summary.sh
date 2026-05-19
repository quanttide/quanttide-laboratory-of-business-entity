#!/bin/bash
# 生成领域概况表
# Usage: ./scripts/summary.sh [domains/]

BASE=${1:-domains}

printf "%-24s %-10s %-10s %-10s %-10s\n" "领域" "本体" "实例" "关系" "文件数"
printf "%.0s-" {1..64}
echo ""

for domain in "$BASE"/*/; do
  name=$(basename "$domain")
  
  ontologies=$(jq '.ontologies | length' "$domain/ontologies.json" 2>/dev/null || echo 0)
  instances=$(jq '.instances | length' "$domain/instances.json" 2>/dev/null || echo 0)
  relations=$(jq '.relations | length' "$domain/relations.json" 2>/dev/null || echo 0)
  files=$(jq '.files | length' "$domain/domain.json" 2>/dev/null || echo 0)
  
  printf "%-24s %-10s %-10s %-10s %-10s\n" "$name" "$ontologies" "$instances" "$relations" "$files"
done
