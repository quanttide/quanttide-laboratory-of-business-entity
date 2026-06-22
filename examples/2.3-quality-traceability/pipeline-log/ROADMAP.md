# pipeline log

记录处理步骤日志。

## 输入

- 流程 ID
- 执行参数
- 执行时间
- 异常信息（可选）

## 输出

追加日志到 `data/qtdata/pipelines/<id>.json` 的 logs 数组

## 验收

- [ ] 日志附加到正确流程
- [ ] 参数和执行时间记录完整
