# 工作方法

## 如何贡献

### 新增检测维度

1. 在 `src/` 下新建 Python 模块，遵循统一的输入输出约定：
    - 输入：`tests/fixtures/input/` 目录下的原始知识库文件
    - 输出：结构化文本结果，打印到标准输出
2. 在 `src/cli.py` 中注册新命令
3. 在 `docs/workflow.md` 中补充对应的检测子流程
4. 如需将检测结果持久化，输出到 `tests/fixtures/output/` 目录下的 JSON 文件

### 新增领域

`tests/fixtures/output/<domain>/domain.json` 结构：

```json
{
  "id": "<domain-id>",
  "name": "<领域名称>",
  "perspective": "<视角声明>",
  "files": ["tests/fixtures/input/<file>.md"],
  "vocabulary": ["术语1", "术语2"]
}
```

1. 运行 `python -m src.cli init-domain <domain-id>` 创建骨架
2. 编辑 `domain.json`：填写名称、视角声明、文件列表、词汇表
3. 编辑 `ontologies.json`：发现该视角下的本体模式
4. 编辑 `instances.json`：将文件内容映射到本体
5. 编辑 `relations.json`：描述跨本体或跨实例的连接
6. 运行 `python -m src.cli validate` 验证 JSON 合法性

### 修改检测逻辑

- 脚本的输入始终是 `tests/fixtures/input/` 下的原始知识库文本，输出是打印到标准输出的检测结果
- 每个问题项应包含：**位置**（文件路径）、**描述**、**建议**
- 不得在检测逻辑中修改原始知识库

### 模块规范

- 使用 Python 模块，放在 `src/` 目录下对应的子包中
- 遵循 `docs/contract.md` 的分工：有确定规则的操作归脚本，需要判断的归智能体
- 每个模块应提供 `run()` 函数作为入口，接受参数并返回退出码
- 模块可直接通过 `python -m src.cli <command>` 调用

### `src/` 目录结构

```
src/
├── cli.py              # 统一 CLI 入口
├── models.py            # 数据模型
├── loader.py            # 数据加载与持久化
├── reporters/           # 报告生成
│   ├── summary.py
│   ├── abstraction.py
│   └── cross_domain.py
├── validators/          # 验证与检测
│   ├── validate.py
│   ├── auto_fix.py
│   ├── fusion_check.py
│   └── find_undefined.py
├── detectors/           # 领域检测与初始化
│   ├── detect_domain.py
│   └── init_domain.py
└── reviewers/           # 交互式评审
    ├── ui.py
    ├── ontology_review.py
    ├── instance_review.py
    └── relation_review.py
```

### 测试要求

- 每个检测模块至少有一个正例（应触发的）和一个反例（不应触发的）
- 测试放在 `tests/` 目录下，使用 `pytest`
- 测试数据放在 `tests/fixtures/input/` 目录下

## 提交规范

- commit message 格式：`<type>(<scope>): <description>`
  - type: `feat`（新增维度/领域）、`fix`（修复误报/漏报）、`refactor`（重构检测逻辑）、`docs`（文档更新）
  - scope: `modeling`（建模）、`fusion`（融合）、`scripts`（脚本）、`docs`（文档）
