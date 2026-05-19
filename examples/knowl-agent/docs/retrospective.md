# 脚本设计反思

## 1. JSON 自修复的假象

`auto-fix.sh` 用 `jq .` 来修复 JSON 格式——但 `jq` 遇到语法错误（如缺少逗号）只会失败退出，什么都不输出。`&& mv` 永远不会执行，循环等于空转 10 轮然后报同样的错。

**根因**：工具选型错误。`jq` 是查询工具不是修复工具。应该用 `python3 json` 模块做带 fallback 的解析，或者去掉"自动修 JSON"这个功能——告诉人有语法错误，由 AI 读文件修，而不是假装脚本能修。

**教训**：不要用只读工具做写操作。

## 2. `//` 操作符在 jq 流中的误用

```jq
# 错的
.instances[].a // .instances[].b

# 对的
.instances[] | (.a // .b)
```

前者的问题：`.instances[].a` 对整个数组求值，`//` 后面又对整个数组求值，结果不是"取每个实例的 a 或 b"，而是"取所有 a，如果第一个是 null 就取所有 b"。

后者才真正表达"对每个实例，取 a，a 不存在则取 b"。

**教训**：jq 的 `//` 在流式上下文中行为不直观，必须用 `|` 限定作用域。

## 3. 脚本写完后没有端到端测试

每个脚本都是独立写、独立提交。直到第一次跑完整 pipeline 才发现：
- `auto-fix.sh` 修不了 JSON → 循环空转
- `fusion-check.sh` 引用检测全是误报 → 需要 NAME_MAP + IGNORE_LIST
- `find-undefined-terms.sh` 的 jq bug → 查不到任何 term

如果写完后立刻跑一遍完整流程（加一个 `scripts/test-pipeline.sh`），这些 bug 会在提交前暴露。

## 4. 无保护的文件覆写

`auto-fix.sh` 的 python fallback 直接写入源文件。如果修复过程中断或 python 脚本有 bug，数据文件可能损坏。

**教训**：所有修复操作应该先写临时文件，验证合法性后再覆盖。

## 5. 改进方向

| 问题 | 方案 |
|------|------|
| JSON 自修复 | 去掉。改由 validate.sh 报错 → AI 手动修 |
| jq 流坑 | 任何 jq 表达式涉及 `//` 时，先用 `|` 限域 |
| 端到端测试 | 加 `scripts/test-pipeline.sh`，完整跑一遍所有脚本 |
| 文件保护 | 所有写操作经临时文件 + 合法性验证 |

## 6. auto-fix.sh 明知故犯

第 5 条的改进方向明确写了"JSON 自修复去掉"，但 `auto-fix.sh` 仍保留原逻辑未改动。`retrospective.md` 记录了教训却没推动修复，说明文档写了不等于改了。

**根因**：记录和修复之间缺少驱动机制。文档只记录了"应该做什么"却没触发"谁什么时候做"。

**教训**：复盘发现的问题应附带 actionable 的跟进标记（如 TODO / 已修 / 搁置），否则复盘文档本身也会过时。

## 7. find-undefined-terms.sh bash 版本兼容性

`find-undefined-terms.sh` 使用 `declare -A`（关联数组），这是 bash 4.0+ 的特性。macOS 默认 bash 3.2 不支持，执行会报错。

**根因**：脚本假设运行环境为 Linux，未考虑 macOS 或其他 POSIX shell。

**教训**：如果脚本需要跨平台运行，应避免 bash 4+ 特有语法，改用 `printf` + `grep` 管道或兼容 POSIX sh 的方案。

## 8. fusion-check.sh 的引用检测有副作用的 stub 创建

`fusion-check.sh` 在引用检测中发现断裂时，会自动在 `sample/` 目录创建 stub 文件：

```bash
cat > "$SAMPLE_DIR/$expected_file" << STUB
```

这违反了 `responsibility-matrix.md` 定义的"脚本只暴露信号，不代人做决定"原则。stub 创建更适合由 AI 在解读检测结果时按需生成，而不是脚本运行时直接写文件。

**根因**：脚本越界做了本应由智能体做的事。

**教训**：规则引擎的输出应保持纯信号（stderr/stdout），写文件操作留给 AI 或人类处理。

## 9. detect-domain.sh grep 模式未转义

`detect-domain.sh` 的词汇匹配使用：

```bash
count=$(grep -o "$term" "$FILE" | wc -l)
```

`$term` 直接作为 grep 正则模式。如果词汇表中包含正则特殊字符（如 `.`、`*`、`[`），匹配行为会偏离预期。

**根因**：词汇匹配应使用固定字符串匹配而非正则匹配。

**教训**：grep 变量参数用于模式匹配时，如无正则需求须加 `-F`。

## 10. 脚本缺少运行环境声明

各脚本头部没有声明依赖（bash 版本、jq、python3）。`auto-fix.sh` 依赖 python3 但未做可用性检查，在无 python3 的环境中会静默失败。

**根因**：脚本的"运行契约"不透明。

**教训**：每个脚本应在头部注释中声明运行环境和外部依赖。
