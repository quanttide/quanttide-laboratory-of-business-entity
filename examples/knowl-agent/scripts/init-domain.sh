#!/bin/bash
# 依赖: bash 3+
# 初始化新领域目录和骨架文件
# Usage: ./scripts/init-domain.sh <domain-name> [--from-detect <file>]

if [ -z "$1" ]; then
  echo "用法: ./scripts/init-domain.sh <domain-name> [--from-detect <file>]"
  exit 1
fi

DOMAIN=$1
DIR="data/$DOMAIN"
mkdir -p "$DIR"

if [ ! -f "$DIR/domain.json" ]; then
  if [ "$2" = "--from-detect" ] && [ -n "$3" ]; then
    FILE=$(basename "$3")
    cat > "$DIR/domain.json" << EOF
{
  "id": "$DOMAIN",
  "name": "",
  "perspective": "",
  "files": ["sample/$FILE"],
  "vocabulary": []
}
EOF
    echo "  [创建] $DIR/domain.json（基于 $FILE）"
  else
    cat > "$DIR/domain.json" << EOF
{
  "id": "$DOMAIN",
  "name": "",
  "perspective": "",
  "files": [],
  "vocabulary": []
}
EOF
    echo "  [创建] $DIR/domain.json"
  fi
fi

for file in ontologies.json instances.json relations.json; do
  if [ ! -f "$DIR/$file" ]; then
    case "$file" in
      ontologies.json) echo '{"ontologies":[]}' > "$DIR/$file" ;;
      instances.json)  echo '{"instances":[]}' > "$DIR/$file" ;;
      relations.json)  echo '{"relations":[]}' > "$DIR/$file" ;;
    esac
    echo "  [创建] $DIR/$file"
  fi
done

echo "领域 $DOMAIN 初始化完成"
