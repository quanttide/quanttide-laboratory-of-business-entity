# change-request create

提交变更请求。

## 输入

- 关联需求/报价单 ID
- 变更描述
- 影响评估
- 成本变更

## 输出

写入 `data/qtdata/change-requests/<id>.json`

## 验收

- [ ] 变更请求关联到正确父资源
- [ ] 影响评估和成本变更记录完整
