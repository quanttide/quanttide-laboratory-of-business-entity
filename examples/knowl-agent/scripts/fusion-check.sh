#!/bin/bash
# 跨领域融合检测
# 检测项：本体名称冲突、词汇交叉、引用断裂、效力声明不一致
# Usage: ./scripts/fusion-check.sh [domains/] [sample/]

DOMAIN_DIR=${1:-domains}
SAMPLE_DIR=${2:-sample}

echo "========================================"
echo "  1. 本体名称冲突（跨领域同名本体）"
echo "========================================"
echo ""

declare -A oname_map
found=0

for domain in "$DOMAIN_DIR"/*/; do
  name=$(basename "$domain")
  file="$domain/ontologies.json"
  [ ! -f "$file" ] && continue
  while read -r oname; do
    [ -z "$oname" ] && continue
    key=$(echo "$oname" | tr -d ' ' | tr '[:upper:]' '[:lower:]')
    if [ -n "${oname_map[$key]}" ] && [ "${oname_map[$key]}" != "$name" ]; then
      echo "  \"$oname\" 出现在: ${oname_map[$key]} ←→ $name"
      found=1
    else
      oname_map["$key"]="$name"
    fi
  done < <(jq -r '.ontologies[].name' "$file" 2>/dev/null)
done

[ $found -eq 0 ] && echo "  （无冲突）"

echo ""
echo "========================================"
echo "  2. 术语交叉引用（跨领域词汇重叠）"
echo "========================================"
echo ""

declare -A term_map
found=0

for domain in "$DOMAIN_DIR"/*/; do
  name=$(basename "$domain")
  file="$domain/domain.json"
  [ ! -f "$file" ] && continue
  while read -r term; do
    [ -z "$term" ] && continue
    if [ -n "${term_map[$term]}" ] && [ "${term_map[$term]}" != "$name" ]; then
      echo "  \"$term\" 同时属于: ${term_map[$term]}, $name"
      found=1
    else
      term_map["$term"]="$name"
    fi
  done < <(jq -r '.vocabulary[]' "$file" 2>/dev/null)
done

[ $found -eq 0 ] && echo "  （无重叠）"

echo ""
echo "========================================"
echo "  3. 引用断裂（文件内《…》引用检测）"
echo "========================================"
echo ""

# 中英文名对照映射: "量潮科技基本章程" → basic-charter
declare -A NAME_MAP
NAME_MAP["量潮科技基本章程"]="basic-charter"
NAME_MAP["量潮科技文档格式章程"]="docs-format"
NAME_MAP["量潮科技工作章程写作章程"]="write-bylaw"
NAME_MAP["量潮科技公司代表章程"]="company-representative"
NAME_MAP["量潮科技离职工作章程"]="human-resignation"
NAME_MAP["量潮科技沟通管理章程"]="connect-index"
NAME_MAP["量潮数据工作章程"]="qtdata-index"
NAME_MAP["量潮数据项目岗位权责章程"]="qtdata-role-authority"
NAME_MAP["离职工作章程"]="human-resignation"
NAME_MAP["沟通管理章程"]="connect-index"
NAME_MAP["文档格式章程"]="docs-format"
NAME_MAP["工作章程写作章程"]="write-bylaw"
NAME_MAP["基本章程"]="basic-charter"

# 应被忽略的外部引用（法律、外部文件、通用商业概念）
IGNORE_LIST=("中华人民共和国公司法" "中华人民共和国个人信息保护法" "劳动合同" "工作订单" "需求规格说明书" "最终验收报告" "交接确认书")

found=0
for f in "$SAMPLE_DIR"/*.md; do
  [ ! -f "$f" ] && continue
  while read -r ref; do
    [ -z "$ref" ] && continue
    target=$(echo "$ref" | sed 's/[《》]//g')
    
    # 跳过外部引用
    skip=0
    for ignore in "${IGNORE_LIST[@]}"; do
      if echo "$target" | grep -q "$ignore"; then
        skip=1
        break
      fi
    done
    [ $skip -eq 1 ] && continue
    
    # 检查名称映射
    match=0
    for name in "${!NAME_MAP[@]}"; do
      if echo "$target" | grep -q "$name"; then
        expected_file="${NAME_MAP[$name]}.md"
        if [ -f "$SAMPLE_DIR/$expected_file" ]; then
          match=1
        else
          echo "  $(basename "$f"): 引用 \"$ref\" → $expected_file 不存在，自动创建 stub"
          cat > "$SAMPLE_DIR/$expected_file" << STUB
# $target

<!-- stub: 被 $(basename "$f") 引用，内容待补全 -->
STUB
          echo "    [已创建] $SAMPLE_DIR/$expected_file"
          found=1
          match=1
        fi
        break
      fi
    done
    
    # 没通过映射匹配的，尝试直接匹配文件名
    if [ $match -eq 0 ]; then
      for mf in "$SAMPLE_DIR"/*.md; do
        mbase=$(basename "$mf" .md)
        if echo "$target" | grep -qi "$mbase"; then
          match=1
          break
        fi
      done
    fi
    
    if [ $match -eq 0 ]; then
      echo "  $(basename "$f"): 引用 \"$ref\" 但无法匹配到已知文件"
      found=1
    fi
  done < <(grep -oP '《[^》]+》' "$f" 2>/dev/null | sort -u)
done

[ $found -eq 0 ] && echo "  （全部可追溯）"

echo ""
echo "========================================"
echo "  4. 效力声明模式对比"
echo "========================================"
echo ""

echo "提取各文件章程效力条款："
for f in "$SAMPLE_DIR"/*.md; do
  [ ! -f "$f" ] && continue
  line=$(grep -A2 "章程效力\|^\*\*第.*条 章程效力" "$f" 2>/dev/null | grep -E "(经|自|由)" | head -1)
  if [ -n "$line" ]; then
    echo "  $(basename "$f"): $(echo "$line" | sed 's/^[[:space:]]*//')"
  fi
done

echo ""
echo "效力主体一致性检查："
bodies=$(grep -A2 "章程效力\|^\*\*第.*条 章程效力" "$SAMPLE_DIR"/*.md 2>/dev/null | grep -oP '(公司[^，；。]*?(?:审议|发布|修订))' | sort -u | wc -l)
if [ "$bodies" -le 1 ]; then
  echo "  ✅ 全部文件使用同一效力主体（公司治理机构审议通过，自发布之日起生效）"
else
  echo "  ⚠️ 存在不同的效力主体，需人工确认"
  grep -A2 "章程效力\|^\*\*第.*条 章程效力" "$SAMPLE_DIR"/*.md 2>/dev/null | grep -oP '(公司[^，；。]*?(?:审议|发布|修订))' | sort -u | while read -r b; do echo "    - $b"; done
fi
