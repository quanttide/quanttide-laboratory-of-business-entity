# blueprint — 数据处理蓝图

## 概念

Blueprint 是一份描述"数据怎么流、怎么变"的契约。它不是数据定义（data contract），而是处理流程定义——从数据采集到最终产出，每步的输入输出和操作。

## 文件

- `blueprint.cue` — CUE 类型定义 + 实例

一个 blueprint 包含：

| 字段 | 说明 |
|------|------|
| `workflow` | 步骤列表，每步含 `from/to/desc/depends` |
| `status` | 当前状态（draft/submitted/confirmed/rejected） |
| `timeline` | 操作日志 |

## 实例

以高频价格指数计算为例的完整蓝图见 `blueprint.cue`，定义了 6 步处理流程：

```
数据采集 → 数据预处理 → 异常处理 → 分类加权平均 → 链式指数计算 → 可视化
```

## 使用

```bash
cue vet blueprint.cue              # 校验
cue export blueprint.cue --out json # 导出
```
