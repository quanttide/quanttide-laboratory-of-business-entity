# issue resolve

标记工单已修复，关联修复版本。

## 输入

- 工单 ID
- 修复说明
- 修复版本号

## 输出

更新 `data/qtdata/issues/<id>.json`，状态变为 resolved

## 验收

- [ ] 工单状态变更为 resolved
- [ ] 修复版本号被记录
