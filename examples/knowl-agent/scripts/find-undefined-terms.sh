#!/bin/bash
# 扫描全库加粗术语，对比所有领域定义，找出未定义术语
# Usage: ./scripts/find-undefined-terms.sh [sample/] [domains/]

SAMPLE_DIR=${1:-sample}
DOMAIN_DIR=${2:-domains}

echo "=== 全库使用但未定义的术语 ==="
echo ""

# 收集所有已定义术语
declare -A defined_terms
for domain in "$DOMAIN_DIR"/*/; do
  file="$domain/instances.json"
  [ ! -f "$file" ] && continue
  while read -r term; do
    [ -n "$term" ] && defined_terms["$term"]=1
  done < <(jq -r '.instances[].subject // .instances[].principle // .instances[].risk // .instances[].element // empty' "$file" 2>/dev/null)
  
  while read -r term; do
    [ -n "$term" ] && defined_terms["$term"]=1
  done < <(jq -r '.vocabulary[]' "$domain/domain.json" 2>/dev/null)
done

# 扫描所有 md 文件中的加粗术语
found=0
for f in "$SAMPLE_DIR"/*.md; do
  [ ! -f "$f" ] && continue
  while read -r term; do
    [ -z "$term" ] && continue
    # 过滤条款编号和章节名
    echo "$term" | grep -qE '^第[一二三四五六七八九十]+条|^第[一二三四五六七八九十]+章' && continue
    # 过滤纯数字和单字
    [ ${#term} -le 1 ] && continue
    
    if [ -z "${defined_terms[$term]}" ]; then
      # 再模糊匹配一次（处理空格差异）
      match=0
      for d in "${!defined_terms[@]}"; do
        d_clean=$(echo "$d" | tr -d ' ')
        t_clean=$(echo "$term" | tr -d ' ')
        if [ "$d_clean" = "$t_clean" ]; then
          match=1
          break
        fi
      done
      if [ $match -eq 0 ]; then
        echo "  $(basename "$f"): 使用了术语 \"$term\" 但未在任何 domain 中定义"
        found=1
      fi
    fi
  done < <(grep -oP '\*\*[^*]+\*\*' "$f" | sed 's/^\*\*//;s/\*\*$//' | sort -u)
done

[ $found -eq 0 ] && echo "  （全部术语已有定义）"
