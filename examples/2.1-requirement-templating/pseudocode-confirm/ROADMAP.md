# pseudocode confirm

客户确认伪代码，触发状态流转。

## 输入

- 伪代码 ID
- 确认结果（confirm/reject）
- 备注（可选）

## 输出

更新 `data/qtdata/pseudocodes/<id>.json` 中的状态字段

## 验收

- [ ] 确认后状态变为 confirmed
- [ ] 驳回后状态变为 rejected，可重新提交
