# ROADMAP

## 现状

已完成前四阶段重构（详见 CHANGELOG.md），当前工具链由 9 个 shell 脚本和 1 个 Python 脚本混合组成。下一阶段目标是统一为 Python 工具链。

## 下一阶段：脚本重构 — Shell → Python

**目标**：将 `scripts/` 下的 shell 脚本逐步重构为 Python 脚本，统一归入 `src/`，提升可维护性、跨平台兼容性和可测试性。

### 动机

当前工具链由 10 个 shell 脚本（`.sh`）和 1 个 Python 脚本（`review.py`）混合组成。Shell 脚本存在以下问题：

- **依赖外部工具**：`jq`、`grep -P`（PCRE）、`bash 3+`，不同环境表现不一致
- **数据结构处理能力弱**：JSON 的复杂查询和变换在 shell 中极为笨拙
- **不可测试**：无单元测试、无模块化、无错误处理链
- **`review.py` 硬耦合**：通过 `subprocess.run(["bash", ...])` 调用 shell 脚本，层间耦合紧

### 重构清单

| Shell 脚本 | Python 模块 | 功能 |
|-----------|------------|------|
| `validate.sh` | `src/validate.py` | 领域目录结构完整性验证 |
| `auto-fix.sh` | `src/auto_fix.py` | 骨架文件自动补全 |
| `summary.sh` | `src/summary.py` | 领域概况统计 |
| `check-abstraction.sh` | `src/check_abstraction.py` | 本体抽象度检测 |
| `detect-domain.sh` | `src/detect_domain.py` | 基于词汇匹配推荐领域 |
| `find-undefined-terms.sh` | `src/find_undefined_terms.py` | 未定义术语扫描 |
| `fusion-check.sh` | `src/fusion_check.py` | 跨领域融合检测 |
| `cross-domain-report.sh` | `src/cross_domain_report.py` | 跨域关系覆盖率报告 |
| `init-domain.sh` | `src/init_domain.py` | 新领域目录初始化 |

### 模块化设计

重构后 `src/` 采用分层结构：

```
src/
├── __init__.py
├── cli.py              # 统一 CLI 入口，替代 review.py 的主菜单
├── models.py            # 数据模型（Domain, Ontology, Instance, Relation）
├── loader.py            # 数据加载与持久化
├── reporters/           # 报告生成
│   ├── __init__.py
│   ├── summary.py
│   ├── abstraction.py
│   └── cross_domain.py
├── validators/          # 验证与检测
│   ├── __init__.py
│   ├── validate.py
│   ├── auto_fix.py
│   ├── fusion_check.py
│   └── find_undefined.py
├── detectors/           # 领域检测与初始化
│   ├── __init__.py
│   ├── detect_domain.py
│   └── init_domain.py
└── review/              # 交互式评审（现有 review.py 拆分）
    ├── __init__.py
    ├── ui.py
    ├── ontology_review.py
    ├── instance_review.py
    └── relation_review.py
```

### 迁移策略

1. **保持兼容**：每个 Python 模块实现后，保留对应 shell 脚本作为 fallback，通过 `scripts/.deprecated` 标记
2. **先易后难**：先迁移无外部依赖的脚本（summary.sh → summary.py），再迁移逻辑复杂的脚本（fusion-check.sh → fusion_check.py）
3. **review.py 解耦**：将 shell 调用替换为 Python 模块直接调用，消除 `subprocess` 依赖
4. **增测试**：每个模块附带对应测试文件 `tests/test_*.py`

### 完成标准

- `scripts/` 下不再有活跃的 shell 脚本（`.deprecated` 目录中的可保留）
- `src/cli.py` 提供统一 CLI，覆盖原有 shell 脚本全部功能
- 测试覆盖率达到 80%+（核心逻辑）
- `review.py` 不再引用 shell 脚本

---

## 里程碑

| 阶段 | 预期产出 | 验证方式 |
|------|---------|---------|
| 脚本重构 | Shell → Python 全部迁移完成，统一 CLI | 测试覆盖率 80%+，review.py 解耦 |
