# 工作方法

## 如何贡献

### 新增检测维度

1. 在 `ROADMAP.md` 的检测维度表中新增一行，说明检测内容、检测方式和反馈形式
2. 在工作流程第二步中补充对应的检测子流程
3. 确保该维度的输出符合质量报告的统一结构（通过/警告/违规）

### 修改检测逻辑

- 检测器的输入始终是原始知识库文本，输出是结构化的问题项列表
- 每个问题项包含：**位置**（文件路径+行号）、**严重级别**（通过/警告/违规）、**描述**、**修改建议**
- 不得在检测逻辑中修改原始知识库

### 测试要求

- 每个检测维度至少有一个正例（应触发的）和一个反例（不应触发的）
- 测试数据放在 `tests/fixtures/` 目录下

### 代码规范

- 检测器命名：`<dimension>_detector.py`（如 `knowledge_modeling_detector.py`）
- 报告输出格式：JSON，遵循统一 schema

## 提交规范

- commit message 格式：`<type>(<scope>): <description>`
  - type: `feat`（新增维度）、`fix`（修复误报/漏报）、`refactor`（重构检测逻辑）
  - scope: `modeling` / `fusion` / `consistency` / `compliance` / `completeness`
