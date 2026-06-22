# 实验 2.4：供应商侧标准映射

**阶段二：技术管理体系代码化**

## 实验目标

将内部交付标准导出为外部可执行格式，让外部供应商也能按统一标准交付并自动校验。

## 验收条件

内部标准可导出为 Markdown/JSON Schema，外部提交的交付物可自动校验是否符合验收准则。

## 任务清单

- [ ] `qtdata standard export` — 导出内部交付规范为外部可读格式（Markdown/JSON schema）
- [ ] `qtdata asset validate` — 校验外部提交的交付物是否符合验收准则
- [ ] `qtdata task assign` — 分配任务给外部供应商（含交付标准、截止日期）

## 数据存储

复用 2.2 的 `data/qtdata/assets/` 目录，新增校验记录字段。
