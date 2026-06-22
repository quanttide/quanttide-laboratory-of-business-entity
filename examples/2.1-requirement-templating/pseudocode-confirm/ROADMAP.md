# pseudocode confirm

客户确认数据处理蓝图（blueprint），触发状态流转。

## 命令

```
qtdata pseudocode confirm <id> [--approve|--reject] [--note "<原因>"]
```

## 行为

| 参数 | 效果 |
|------|------|
| `--approve` | blueprint.status → `confirmed` |
| `--reject` + `--note` | blueprint.status → `rejected` |
| 已确认/已驳回的 id 重复操作 | 报错 |
| 不存在的 id | 报错 |

## 数据依赖

读取 `data/qtdata/pseudocodes/<id>.json`，写入 `status` 和 `timeline` 字段。

## 验收

- [ ] `--approve` 后 status = `confirmed`
- [ ] `--reject` 后 status = `rejected`
- [ ] 重复操作报错
- [ ] 不存在的 id 报错
