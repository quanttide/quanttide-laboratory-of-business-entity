# Bug is Feature —— 战略假设压力测试机

## 概念

把 AI 当辩论对手而非算命先生：

1. **System 1**：AI 基于你的战略上下文，给出正常分析和建议
2. **System 2**：AI 提取 System 1 背后依赖的内外部假设（不评判对错）
3. **review**：你逐条审查假设，用实际数据判断——已确认/已排除/有证据但有障碍/无证据
4. **report**：生成假设验证报告，看清哪些前提成立、哪些崩塌

## 用法

```bash
./strategy.py new [file]    # 发起推演（可指定 JSON 上下文文件）
./strategy.py review        # 逐条审查待验证的假设
./strategy.py report        # 生成假设验证报告
./strategy.py list          # 查看假设库
./strategy.py stats         # 假设库统计
./strategy.py help          # 帮助
```

## 数据

存储在 `apps/strategy/hypotheses.json`，纯 JSON 格式。

每条假设包含：内容、类型（internal/external）、你的判断（confirmed/rejected/evidence_with_difficulty/no_evidence）、证据、障碍、日期。
