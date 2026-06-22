# 蓝图契约

## package blueprint

### #Timestamp

```
=~"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}$"
```

ISO 8601 时间戳格式。

### #Step

```
{
  name:    string
  from:    string
  to:      string
  desc:    string
  depends?: [...string]
}
```

一个处理步骤。`from` 输入，`to` 输出，`desc` 操作描述，`depends` 依赖的上一步名称（可选）。

### #Pipeline

```
{
  name:  string
  steps: [...#Step]
}
```

步骤管道。`name` 工作流名称，`steps` 有序步骤列表。

### #Status

```
"draft" | "submitted" | "confirmed" | "rejected"
```

蓝图状态枚举。

### #Blueprint

```
{
  id:             =~"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
  requirement_id: string
  version:        >0
  workflow:       #Pipeline
  status:         #Status
  created_at:     #Timestamp
  updated_at:     #Timestamp
}
```

蓝图主类型。`id` UUID 格式，`version` 大于 0，`workflow` 处理管道。
