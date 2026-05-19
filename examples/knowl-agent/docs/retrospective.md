# 脚本设计反思

## 未修复

### 端到端测试

每个脚本都是独立写、独立提交。直到第一次跑完整 pipeline 才发现交叉问题。

如果写完后立刻跑一遍完整流程（加一个 `scripts/test-pipeline.sh`），这些 bug 会在提交前暴露。

### bash 版本兼容性

`find-undefined-terms.sh` 使用 `declare -A`（关联数组），这是 bash 4.0+ 的特性。macOS 默认 bash 3.2 不支持。

**教训**：如果脚本需要跨平台运行，应避免 bash 4+ 特有语法，改用 `printf` + `grep` 管道或兼容 POSIX sh 的方案。

## 已修复

| 问题 | 修复 |
|------|------|
| JSON 自修复假象 | auto-fix.sh 去掉 json 修复，改由 validate 报错 → AI 修 |
| jq `//` 流误用 | find-undefined-terms.sh 加 `|` 限域 |
| 无保护文件覆写 | 去掉所有写操作 |
| fusion-check stub 副作用 | 去掉自动创建，仅报告 |
| detect-domain grep 未转义 | 加 `-F` 固定字符串匹配 |
| 缺少运行环境声明 | 各脚本头部加依赖注释 |
| auto-fix 明知故犯 | 已修复 |
