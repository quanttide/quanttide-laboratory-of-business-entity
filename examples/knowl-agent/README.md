# 知识工程智能体 — 原始知识库质量反向检测

## 目录结构

```
knowl-agent/
├── AGENTS.md           # 智能体自描述：定位与工作纪律
├── ROADMAP.md          # 执行方案
├── CHANGELOG.md        # 变更记录
├── STATUS.md           # 当前状态报告
├── CONTRIBUTING.md     # 工作方法：如何新增/修改检测维度
├── README.md           # 本文件：项目概览
├── docs/               # 文档（权责清单、工作流、报告）
│   ├── contract.md
│   ├── workflow.md
│   └── report.md              # 最近一次执行报告
├── src/                # Python 工具链
│   ├── cli.py          # 统一 CLI 入口
│   ├── models.py       # 数据模型
│   ├── loader.py       # 数据加载
│   ├── reporters/      # 报告生成
│   ├── validators/     # 验证检测
│   └── detectors/      # 领域操作
├── tests/
│   ├── fixtures/       # 测试数据
│   │   ├── output/     # 领域建模产出（按领域划分）
│   │   │   ├── org-gov/
│   │   │   ├── hr/
│   │   │   ├── doc-std/
│   │   │   └── biz-ops/
│   │   └── input/      # 原始知识库文件
│   │       ├── basic-charter.md
│   │       ├── company-representative.md
│   │       ├── connect-index.md
│   │       ├── docs-format.md
│   │       ├── human-resignation.md
│   │       ├── qtdata-index.md
│   │       ├── qtdata-org.md
│   │       ├── rank-index.md
│   │       ├── secretary.md
│   │       └── write-bylaw.md
│   └── test_*.py       # 单元测试
```

## 快速开始

1. 阅读 `AGENTS.md` 了解智能体定位
2. 阅读 `docs/workflow.md` 了解完整执行流程
3. 阅读 `docs/contract.md` 了解人机分工
4. 阅读 `docs/workflow.md` 了解完整执行流程

## 文件分工

| 文件 | 角色 | 使用者 |
|------|------|--------|
| AGENTS.md | 元认知文件 | 初次了解项目定位 |
| ROADMAP.md | 执行方案 | 了解检测维度与阶段 |
| CONTRIBUTING.md | 贡献指南 | 扩展检测维度时查阅 |
| docs/contract.md | 权责清单 | 判断分工边界 |
| docs/workflow.md | 操作手册 | 执行流程时查阅 |
| src/ | 工具链 | 自动执行检测 |
| tests/fixtures/input/ | 检测对象 | 执行检测时作为输入 |
| tests/fixtures/output/ | 检测产出 | 领域建模结果 |
