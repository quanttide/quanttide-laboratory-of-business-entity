# 脚本修复前后对比

## 修复项

| 修复 | 涉及脚本 | 问题 |
|------|---------|------|
| 去掉 JSON 自修复 | auto-fix.sh | jq 无法修语法错误，循环空转 |
| fusion-check 去掉 stub 创建 | fusion-check.sh | 脚本越界写文件 |
| detect-domain grep 加 -F | detect-domain.sh | 正则未转义导致匹配偏差 |
| jq 流 `//` 加 `|` 限域 | find-undefined-terms.sh | 查不到任何 term |
| 各脚本加依赖声明 | 全部 | 无运行环境契约 |

## 输出对比

### validate.sh

| 阶段 | 修复前 | 修复后 |
|------|--------|--------|
| hr/ontologies.json | FAIL（循环 10 轮空转） | ✅ PASS |
| 其他 5 个领域 | ✅ PASS | ✅ PASS |

### summary.sh（之前 validate 阻塞无法运行）

修复后：

| 领域 | 本体 | 实例 | 关系 | 文件数 |
|------|------|------|------|--------|
| communication | 3 | 4 | 2 | 1 |
| data-governance | 4 | 9 | 3 | 1 |
| doc-writing | 3 | 12 | 2 | 2 |
| hr | 6 | 11 | 3 | 3 |
| legal-normative | 4 | 23 | 3 | 6 |
| org-management | 7 | 31 | 6 | 9 |

### find-undefined-terms.sh

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 未定义术语数 | 21（含大量模板 false positive） | 0 ✅ |
| 主要假阳性 | 第X条模板词、条款标题 | 已过滤 |
| 真实缺口 | 公司治理机构、工作订单等 | 已补全为实例 |

### fusion-check.sh

| 检测项 | 修复前 | 修复后 |
|--------|--------|--------|
| 本体名称冲突 | 无 | 无（不变） |
| 术语交叉 | "资格" hr ↔ org-management | 同（不变） |
| 引用断裂 | 10 处（含《公司法》《工作订单》等误报） | 2 处（量潮数据岗位权责章程、数据处理服务框架协议） |
| 效力声明 | 存在不一致（已修复） | ✅ 全部一致 |
| 副作用 | 自动创建 stub 文件 | 无（仅报告） |

### detect-domain.sh

| 文件 | 修复前 | 修复后 | 原因 |
|------|--------|--------|------|
| secretary.md | org-management 命中 17 | org-management 命中 89 | 词汇表扩充 + grep -F 精确匹配 |

## 剩余问题

1. `scripts/test-pipeline.sh` 未创建（端到端测试）
2. `find-undefined-terms.sh` 依赖 bash 4+（`declare -A`），macOS 不可用
3. 引用断裂 2 处待 AI 判断后处理
