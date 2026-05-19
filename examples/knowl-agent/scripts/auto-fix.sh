#!/bin/bash
# 依赖: bash 3+, jq
# 循环检测+自动修复已知问题（仅补缺失文件，不修 JSON 格式）
# Usage: ./scripts/auto-fix.sh [data/] [sample/]

DOMAIN_DIR=${1:-data}
SAMPLE_DIR=${2:-sample}
MAX_ITER=10

echo "自动修复开始"
echo ""

for ((i=1; i<=MAX_ITER; i++)); do
  echo "--- 第 $i 轮 ---"
  
  # 1. validate + 自动修 JSON
  issues=0
  for domain in "$DOMAIN_DIR"/*/; do
    name=$(basename "$domain")
    for file in domain.json ontologies.json instances.json relations.json; do
      f="$domain$file"
      [ ! -f "$f" ] && continue
      if ! jq . "$f" > /dev/null 2>&1; then
        echo "  [跳过] $name/$file JSON 格式错误 — 需 AI 手动修复"
      fi
    done
  done
  
  # 2. 补齐 MISS 骨架
  for domain in "$DOMAIN_DIR"/*/; do
    name=$(basename "$domain")
    for file in ontologies.json instances.json relations.json; do
      f="$domain$file"
      if [ ! -f "$f" ]; then
        case "$file" in
          ontologies.json) echo '{"ontologies":[]}' > "$f" ;;
          instances.json)  echo '{"instances":[]}' > "$f" ;;
          relations.json)  echo '{"relations":[]}' > "$f" ;;
        esac
        echo "  [补全] $name/$file"
        issues=$((issues + 1))
      fi
    done
  done
  
  if [ $issues -eq 0 ]; then
    echo "全部通过"
    break
  fi
done

# 最终验证
echo ""
./scripts/validate.sh "$DOMAIN_DIR"
