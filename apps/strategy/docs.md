# Bug is Feature —— 战略假设压力测试机

## 概念

把 AI 当辩论对手而非算命先生：

1. **System 1**：AI 基于你的战略上下文，给出一个正常的战略分析和建议
2. **System 2**：假设上面的建议一定是错的，审视可能错误的原因和隐藏假设
3. 你看每条假设，判断和实际情况是否一致——同意、排除、或存疑
4. 验证结果存入本地假设库，成为可追溯的战略资产

## 用法

```bash
./strategy.py new       # 发起一轮推演
./strategy.py list      # 查看假设库
./strategy.py stats     # 假设库统计
./strategy.py context   # 查看/修改战略上下文
./strategy.py help      # 帮助
```

## 数据

存储在 `~/.qtstrategy/`，纯 JSON 格式，完全本地。

- `context.json`：你的战略上下文（公司方向 + 业务线挑战）
- `hypotheses.json`：假设库，每一条含：假设内容、AI 来源、你的判断（confirmed/rejected/uncertain）、日期

## 原理解释

为什么这比直接让 AI 给建议更有用：

> 以前：AI 是"算命先生"，算不准我就骂它。
> 现在：AI 是"辩论对手"，它抛出的极端观点（Bug），是为了逼迫我审视我潜意识里忽略的假设（Feature）。

AI 没有你的私有上下文（只有不到10人、刚被限流、CTO 今天心情不好），所以它的结论必然错。但背后的逻辑路径里，藏着对宏观市场的理解——这才是真正有价值的部分。
