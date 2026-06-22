# 实验 2.3：质量回溯机制

**阶段二：技术管理体系代码化**

## 实验目标

建立交付物到数据来源、处理步骤、责任人的完整血缘链，让问题可追溯、可定位。

## 验收条件

一个交付物可通过 CLI 展示其完整血缘链（数据来源→处理步骤→产出），问题工单可关联交付物并标记修复。

## 任务清单

- [ ] `qtdata pipeline create` — 创建数据处理流程定义（输入/输出 Dataset 关联）
- [ ] `qtdata pipeline log` — 记录处理步骤日志（参数、执行时间、异常）
- [ ] `qtdata issue create` — 创建问题工单，关联交付物/数据集
- [ ] `qtdata issue trace` — 展示指定交付物的完整血缘链（数据来源→处理步骤→产出）
- [ ] `qtdata issue resolve` — 标记工单已修复，关联修复版本

## 数据存储

```
data/qtdata/
  pipelines/       — 流程定义 JSON
  issues/          — 问题工单 JSON
```
