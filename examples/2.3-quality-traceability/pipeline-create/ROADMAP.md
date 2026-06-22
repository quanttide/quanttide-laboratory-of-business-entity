# pipeline create

创建数据处理流程定义。

## 输入

- 流程名称
- 输入 Dataset 引用
- 输出 Dataset 引用
- 处理步骤描述

## 输出

写入 `data/qtdata/pipelines/<id>.json`

## 验收

- [ ] 流程定义关联了输入/输出 Dataset
- [ ] 可在 issue trace 中被引用
