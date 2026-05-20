# 变更记录

## [1.0.0] - 2026-05-19

### 第一阶段：本体重构

14 个 ontology pattern 完成抽象重构，去除具体值改为可复用抽象模式。

| 领域 | 本体 | 抽象方向 |
|------|------|---------|
| biz-ops | role-responsibility | 角色以职责+权限成对定义 |
| biz-ops | service-process | 流程由阶段序列组成 |
| biz-ops | risk-control | 风险领域→控制措施集→措施分类 |
| biz-ops | cognitive-sovereignty | 原则约束行为边界 |
| doc-std | document-structure | 文档由元信息+引言+主体+结尾构成 |
| doc-std | format-rule | 格式要素有允许使用和禁止使用两种边界 |
| doc-std | content-standard | 内容受通用性/稳定性/域分离约束 |
| hr | development-track | 职业发展经历预备阶段后进入并行通道 |
| hr | rank-level | 等级递增表示资深程度 |
| hr | resignation-process | 流程由阶段序列组成 |
| org-gov | authority-responsibility | 清理 pattern 中的具体引用 |
| org-gov | hierarchy-system | 层级中上层效力高于下层 |
| org-gov | deliberation-procedure | 审议流程：召集→出席→辩论→表决→记录 |
| org-gov | qualification-condition | 清理末尾的具体例子 |

### 第二阶段：实例归位

- 从 ontology pattern 中提取具体值迁移到 instances.json
- 移除 ontology 中的 `source_files` 字段，移至实例层
- 补充 7 个新实例，全部本体达到 ≥3 实例的覆盖率标准

### 第三阶段：跨领域关系网

建立 8 条跨领域关系，每领域 ≥2 条：

| 源领域 | 源概念 | 目标领域 | 目标概念 | 关系类型 |
|--------|--------|---------|---------|---------|
| org-gov | 资格-条件 | hr | 职级等级 | references |
| biz-ops | 角色-职责 | org-gov | 权责结构 | instance-of |
| doc-std | 文档结构 | org-gov | 层级体系 | governs |
| hr | 离职流程 | biz-ops | 服务流程 | intersects |

### 第四阶段：工具链升级

- 新增 `scripts/check-abstraction.sh` — 本体抽象度检测脚本
- 新增 `scripts/cross-domain-report.sh` — 跨领域关系覆盖率报告
- 修复四个脚本问题：auto-fix、find-undefined-terms、fusion-check、detect-domain
- `.review.json` 新增 79 条评审记录，覆盖全部 83 项
