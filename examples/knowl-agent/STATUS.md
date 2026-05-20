# 知识工程智能体 — 状态报告

## 项目概览

原始知识库质量反向检测系统。通过对量潮科技公司治理章程（10 份文档）进行知识工程分析，检测知识库的结构质量。

## 数据规模

| 领域 | 视角 | 本体 | 实例 | 关系 | 源文件 |
|------|------|------|------|------|--------|
| biz-ops | 业务管理 | 4 | 12 | 7 | 3 |
| doc-std | 写作学 | 3 | 9 | 6 | 2 |
| hr | 人力资源管理 | 3 | 9 | 6 | 2 |
| org-gov | 组织管理 | 4 | 13 | 7 | 4 |
| **合计** | **4 视角** | **14** | **43** | **26** | **11** |
| 其中跨域关系 | | | | 8 | |

## 完成阶段

### ✅ 第一阶段：本体重构

14 个 ontology pattern 已完成抽象重构，全部通过"换源测试"和"填空测试"。pattern 不再包含具体角色名、阶段名、等级值等具体值。

### ✅ 第二阶段：实例归位

所有具体值已从本体层迁移至实例层。`source_files` 字段仅出现在 instances.json。每个本体 ≥3 实例。

### ✅ 第三阶段：跨领域关系网

建立 8 条跨领域关系，每领域均 ≥2 条。覆盖 org-gov↔hr、biz-ops↔org-gov、doc-std↔org-gov、hr↔biz-ops 四组连接。

### ✅ 第四阶段：工具链升级 (Shell)

9 个 shell 脚本就绪：validate、auto-fix、summary、check-abstraction、detect-domain、find-undefined-terms、fusion-check、cross-domain-report、init-domain。全部已修复已知问题。

### ✅ 第五阶段：脚本重构 (Shell → Python)

已完成，详见下方工具链状态。

## 工具链状态

### 统一 CLI

通过 `python -m src.cli <command>` 调用，9 个命令全部可用：

| 命令 | 模块 | 功能 |
|------|------|------|
| `summary` | `src/reporters/summary.py` | 领域概况统计 |
| `validate` | `src/validators/validate.py` | JSON 合法性验证 |
| `auto-fix` | `src/validators/auto_fix.py` | 骨架文件自动补全 |
| `check-abstraction` | `src/reporters/abstraction.py` | 本体抽象度检测 |
| `cross-domain-report` | `src/reporters/cross_domain.py` | 跨域关系覆盖率 |
| `find-undefined-terms` | `src/validators/find_undefined.py` | 未定义术语扫描 |
| `fusion-check` | `src/validators/fusion_check.py` | 跨领域融合检测 |
| `detect-domain` | `src/detectors/detect_domain.py` | 词汇匹配推荐领域 |
| `init-domain` | `src/detectors/init_domain.py` | 新领域初始化 |

### 交互式评审

`src/review.py` 提供 TUI 交互式逐项评审，已解除对 shell 脚本的 subprocess 依赖。

### 测试

`tests/` 下 4 个测试文件、5 个用例，全部通过。

### 旧脚本

shell 脚本已归档至 `scripts/.deprecated/`，保留作为回退。

## 已知问题

| 问题 | 影响 | 状态 |
|------|------|------|
| `find-undefined-terms` 将模板术语（"第X条 定义"等）误报为未定义 | write-bylaw.md 检测结果含 8 个误报 | 需优化过滤规则 |
| `fusion-check` 检测到 "交接" 一词同时属于 hr 和 org-gov | 术语重叠 1 处，需人工确认是否合理 | **【需人确认】** |
| `fusion-check` 检测到 qtdata-index.md 引用 "量潮数据项目岗位权责章程" 无法匹配文件 | 引用断裂 1 处，可能缺少对应 sample 文件 | **【需人确认】** |
| review.py 的 `review/` 子包尚未拆分 | 仍为单文件 `src/review.py`，未拆分为 review/ 子包 | 待下次重构 |

## 文件索引

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 智能体自描述、工作纪律、本体质量标准 |
| `ROADMAP.md` | 下一阶段路线图（脚本重构已完成） |
| `STATUS.md` | 本文件：当前状态报告 |
| `CHANGELOG.md` | 已完成阶段的变更记录 |
| `CONTRIBUTING.md` | 贡献指南（Python 工具链版） |
| `README.md` | 项目概览 |
| `docs/workflow.md` | 五步执行流程 |
| `docs/responsibility-matrix.md` | 人机权责分工 |
| `docs/report.md` | 最近一次执行报告 |
