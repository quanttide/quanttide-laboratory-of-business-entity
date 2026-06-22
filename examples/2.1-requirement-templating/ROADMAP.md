# 实验 2.1：需求拆解模板化

**阶段二：技术管理体系代码化**

## 实验目标

把 PRD 定义的 5 阶段用户故事地图从「人在群里走流程」变为 CLI 命令驱动的标准化表单和流转。

## 验收条件

一个需求从创建规格→伪代码确认→报价→变更的全过程，可通过 CLI 完成，状态可查。

## 任务清单

- [ ] `qtdata requirement create` — 创建需求规格（业务目标、场景描述、样本数据、验收标准）
- [ ] `qtdata requirement list` — 列出需求清单及确认状态
- [ ] `qtdata pseudocode submit` — 提交清洗伪代码版本
- [ ] `qtdata pseudocode confirm` — 客户确认伪代码，状态流转
- [ ] `qtdata quotation create` — 创建报价单（定价规则、分阶段付款、变更成本）
- [ ] `qtdata change-request create` — 提交变更请求（影响评估、成本变更）
- [ ] `qtdata change-request approve|reject` — 审批变更请求

## 数据存储

```
data/qtdata/
  requirements/    — 需求规格 JSON
  pseudocodes/     — 伪代码版本 JSON
  quotations/      — 报价单 JSON
  change-requests/ — 变更请求 JSON
```
