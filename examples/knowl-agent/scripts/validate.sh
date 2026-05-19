#!/bin/bash
# 依赖: bash 3+, jq
# 验证领域目录结构完整性
# Usage: ./scripts/validate.sh [domains/]

BASE=${1:-domains}
ERRORS=0

for domain in "$BASE"/*/; do
  name=$(basename "$domain")
  echo "=== $name ==="
  
  for file in domain.json ontologies.json instances.json relations.json; do
    if [ -f "$domain$file" ]; then
      # 检查 JSON 合法性
      if ! jq . "$domain$file" > /dev/null 2>&1; then
        echo "  [FAIL] $file - JSON 格式错误"
        ERRORS=$((ERRORS + 1))
      else
        echo "  [OK]   $file"
      fi
    else
      echo "  [MISS] $file"
      ERRORS=$((ERRORS + 1))
    fi
  done
done

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "全部验证通过"
else
  echo "发现 $ERRORS 个问题"
  exit 1
fi
