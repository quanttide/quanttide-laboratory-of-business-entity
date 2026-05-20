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

14 个 ontology pattern 已完成抽象重构，全部通过 `check-abstraction.sh` 信号检测。pattern 不再包含具体角色名、阶段名、等级值等具体值。

### ✅ 第二阶段：实例归位

所有具体值已从本体层迁移至实例层。`source_files` 字段仅出现在 instances.json。每个本体 ≥3 实例。

### ✅ 第三阶段：跨领域关系网

建立 8 条跨领域关系，每领域均 ≥2 条。覆盖 org-gov↔hr、biz-ops↔org-gov、doc-std↔org-gov、hr↔biz-ops 四组连接。

### ✅ 第四阶段：Shell 工具链

9 个 shell 脚本全部修复已知问题后已删除，功能由 Python 工具链替代。

### ✅ 第五阶段：脚本重构 (Shell → Python)

9 个 Python 模块全部实现，通过统一 CLI 调用。shell 脚本已移除。

## 目录结构

```
├── AGENTS.md               # 智能体自描述、工作纪律、质量标准
├── CHANGELOG.md            # 已完成阶段的变更记录
├── CONTRIBUTING.md         # 贡献指南
├── README.md               # 项目概览
├── ROADMAP.md              # 下一阶段路线图
├── STATUS.md               # 本文件：当前状态报告
├── docs/
│   ├── acceptance-criteria.md   # 本体评审与验收标准
│   ├── index.md                 # AI 能力边界分析
│   ├── responsibility-matrix.md # 人机权责分工
│   └── workflow.md              # 知识发现与建模流程
├── src/
│   ├── cli.py              # 统一 CLI 入口
│   ├── models.py           # 数据模型
│   ├── loader.py           # 数据加载
│   ├── reporters/          # 报告生成
│   ├── validators/         # 验证与检测
│   ├── detectors/          # 领域检测与初始化
│   └── review/             # 交互式评审子包（python -m src.review）
│       ├── __init__.py     # 主菜单与协调逻辑
│       ├── __main__.py     # 入口（python -m src.review）
│       ├── ui.py           # 终端 UI 工具
│       ├── data.py         # 数据加载与评审持久化
│       ├── ontology_review.py
│       ├── instance_review.py
│       └── relation_review.py
└── tests/
    ├── fixtures/input/     # 原始知识库（10 份章程文档）
    ├── fixtures/output/    # 领域建模结果（4 领域）
    ├── test_abstraction.py
    ├── test_loader.py
    ├── test_summary.py
    └── test_validate.py
```

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

`src/review.py` 提供 TUI 交互式逐项评审。

### 测试

`tests/` 下 4 个测试文件、5 个用例，全部通过。

## 已知问题

| 问题 | 影响 | 状态 |
|------|------|------|
| `find-undefined-terms` 将模板术语（"第X条 定义"等）误报为未定义 | write-bylaw.md 检测结果含 8 个误报 | 需优化过滤规则 |
| `fusion-check` 检测到 "交接" 一词同时属于 hr 和 org-gov | 术语重叠 1 处，需人工确认是否合理 | **【需人确认】** |
| `fusion-check` 检测到 qtdata-index.md 引用 "量潮数据项目岗位权责章程" 无法匹配文件 | 引用断裂 1 处，可能缺少对应 sample 文件 | **【需人确认】** |
| 测试断言偏弱 | 仅验证返回值，未验证输出内容 | 待增强 |

## 文件索引

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 智能体自描述、工作纪律、本体质量标准 |
| `ROADMAP.md` | 下一阶段路线图 |
| `STATUS.md` | 本文件：当前状态报告 |
| `CHANGELOG.md` | 已完成阶段的变更记录 |
| `CONTRIBUTING.md` | 贡献指南 |
| `README.md` | 项目概览 |
| `docs/workflow.md` | 知识发现与建模流程（五步） |
| `docs/responsibility-matrix.md` | 人机权责分工 |
| `docs/acceptance-criteria.md` | 本体评审与验收标准 |
| `docs/index.md` | AI 能力边界分析 |
