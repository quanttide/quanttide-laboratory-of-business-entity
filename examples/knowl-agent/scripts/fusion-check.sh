#!/bin/bash
# 跨领域术语冲突检测
# 扫描所有领域 ontologies.json 中的本体名称，找出同名本体
# Usage: ./scripts/fusion-check.sh [domains/]

BASE=${1:-domains}
declare -A ontology_names

echo "=== 跨领域本体名称冲突检测 ==="
echo ""

for domain in "$BASE"/*/; do
  name=$(basename "$domain")
  file="$domain/ontologies.json"
  
  if [ ! -f "$file" ]; then
    continue
  fi
  
  while read -r oname; do
    if [ -n "$oname" ]; then
      key=$(echo "$oname" | tr -d ' ')
      if [ -n "${ontology_names[$key]}" ]; then
        echo "[冲突] \"$oname\" 同时出现在: ${ontology_names[$key]} ←→ $name"
      else
        ontology_names["$key"]="$name"
      fi
    fi
  done < <(jq -r '.ontologies[].name' "$file" 2>/dev/null)
done

echo ""
echo "=== 术语交叉引用 ==="
echo ""

for domain in "$BASE"/*/; do
  name=$(basename "$domain")
  file="$domain/domain.json"
  
  if [ ! -f "$file" ]; then
    continue
  fi
  
  vocab=$(jq -r '.vocabulary[]' "$file" 2>/dev/null)
  
  for other in "$BASE"/*/; do
    other_name=$(basename "$other")
    if [ "$name" = "$other_name" ]; then
      continue
    fi
    
    other_file="$other/domain.json"
    [ ! -f "$other_file" ] && continue
    
    while read -r term; do
      if [ -n "$term" ] && jq -e ".vocabulary[] | select(. == \"$term\")" "$other_file" > /dev/null 2>&1; then
        echo "  \"$term\" 同时属于: $name, $other_name"
      fi
    done <<< "$vocab"
  done
done 2>/dev/null | sort -u
