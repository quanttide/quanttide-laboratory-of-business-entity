# asset accept|reject

签署验收/驳回，触发状态流转。

## 输入

- 交付物 ID
- 决定（accept/reject）
- 签署意见

## 输出

更新 `data/qtdata/assets/<id>.json`，状态流转为 accepted/rejected

## 验收

- [ ] 接受后状态变为 accepted
- [ ] 驳回后状态变为 rejected，可重新提交
