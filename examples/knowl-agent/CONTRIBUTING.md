# 工作方法

## 如何贡献

### 新增检测维度

1. 在 `scripts/` 下新建 shell 脚本，遵循统一的输入输出约定：
   - 输入：`sample/` 目录下的原始知识库文件
   - 输出：结构化文本结果，打印到标准输出
2. 在 `docs/workflow.md` 中补充对应的检测子流程
3. 如需将检测结果持久化，输出到 `data/` 目录下的 JSON 文件

### 新增领域

`data/<domain>/domain.json` 结构：

```json
{
  "id": "<domain-id>",
  "name": "<领域名称>",
  "perspective": "<视角声明>",
  "files": ["sample/<file>.md"],
  "vocabulary": ["术语1", "术语2"]
}
```

1. 运行 `scripts/init-domain.sh <domain-id>` 创建骨架
2. 编辑 `domain.json`：填写名称、视角声明、文件列表、词汇表
3. 编辑 `ontologies.json`：发现该视角下的本体模式
4. 编辑 `instances.json`：将文件内容映射到本体
5. 编辑 `relations.json`：描述跨本体或跨实例的连接
6. 运行 `scripts/validate.sh` 验证 JSON 合法性

### 修改检测逻辑

- 脚本的输入始终是 `sample/` 下的原始知识库文本，输出是打印到标准输出的检测结果
- 每个问题项应包含：**位置**（文件路径）、**描述**、**建议**
- 不得在检测逻辑中修改原始知识库

### 脚本规范

- 使用 bash 脚本，放在 `scripts/` 目录
- 运行时依赖声明在脚本开头的注释中
- 遵循 `docs/responsibility-matrix.md` 的分工：有确定规则的操作归脚本，需要判断的归智能体

### 测试要求

- 每个检测脚本至少有一个正例（应触发的）和一个反例（不应触发的）
- 测试数据放在 `sample/` 目录下

## 提交规范

- commit message 格式：`<type>(<scope>): <description>`
  - type: `feat`（新增维度/领域）、`fix`（修复误报/漏报）、`refactor`（重构检测逻辑）、`docs`（文档更新）
  - scope: `modeling`（建模）、`fusion`（融合）、`scripts`（脚本）、`docs`（文档）
