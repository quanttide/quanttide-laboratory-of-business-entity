# change-request approve|reject

审批变更请求。

## 输入

- 变更请求 ID
- 审批决定（approve/reject）
- 审批意见

## 输出

更新 `data/qtdata/change-requests/<id>.json` 中的状态字段

## 验收

- [ ] 审批后状态正确流转
- [ ] 审批意见被记录
