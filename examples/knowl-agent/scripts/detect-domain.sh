#!/bin/bash
# 依赖: bash 3+, jq, grep
# 基于词汇匹配为新文件推荐所属领域
# Usage: ./scripts/detect-domain.sh <file>

FILE=$1
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "用法: ./scripts/detect-domain.sh <file>"
  exit 1
fi

echo "文件: $FILE"
echo ""

for domain in domains/*/; do
  name=$(basename "$domain")
  file="$domain/domain.json"
  
  [ ! -f "$file" ] && continue
  
  score=0
  total=0
  
  while read -r term; do
    [ -z "$term" ] && continue
    total=$((total + 1))
    count=$(grep -oF "$term" "$FILE" | wc -l)
    score=$((score + count))
  done < <(jq -r '.vocabulary[]' "$file" 2>/dev/null)
  
  if [ "$total" -gt 0 ] && [ "$score" -gt 0 ]; then
    echo "  $name: 命中 $score 次（词汇表 $total 词）"
  fi
done | sort -t: -k2 -rn
