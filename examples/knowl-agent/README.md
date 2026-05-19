# 知识工程智能体 — 原始知识库质量反向检测

## 目录结构

```
knowl-agent/
├── AGENTS.md           # 智能体自描述：定位与工作纪律
├── ROADMAP.md          # 执行方案：检测维度、阶段流程与质量报告
├── CONTRIBUTING.md     # 工作方法：如何新增/修改检测维度
├── README.md           # 本文件：项目概览
├── docs/               # 文档（权责清单、工作流、报告）
│   ├── responsibility-matrix.md
│   ├── workflow.md
│   └── report.md              # 最近一次执行报告
├── scripts/            # 规则引擎脚本
│   ├── validate.sh
│   ├── summary.sh
│   ├── fusion-check.sh
│   ├── detect-domain.sh
│   ├── init-domain.sh
│   ├── find-undefined-terms.sh
│   └── auto-fix.sh
├── data/               # 领域数据（按领域划分）
│   ├── org-gov/
│   ├── hr/
│   ├── doc-std/
│   └── biz-ops/
└── sample/             # 样本知识库：用于检测的原始知识文件
    ├── basic-charter.md            # 基本章程
    ├── company-representative.md   # 公司代表章程
    ├── connect-index.md            # 沟通管理章程
    ├── docs-format.md              # 文档格式章程
    ├── human-resignation.md        # 离职工作章程
    ├── qtdata-index.md             # 量潮数据工作章程
    ├── qtdata-org.md               # 量潮数据组织管理章程
    ├── rank-index.md               # 职级管理章程
    ├── secretary.md                # 公司秘书章程
    └── write-bylaw.md              # 工作章程写作章程
```

## 快速开始

1. 阅读 `AGENTS.md` 了解智能体定位
2. 阅读 `docs/workflow.md` 了解完整执行流程
3. 阅读 `docs/responsibility-matrix.md` 了解人机分工
4. 阅读 `docs/report.md` 查看最近一次执行结果

## 文件分工

| 文件 | 角色 | 使用者 |
|------|------|--------|
| AGENTS.md | 元认知文件 | 初次了解项目定位 |
| ROADMAP.md | 执行方案 | 了解检测维度与阶段 |
| CONTRIBUTING.md | 贡献指南 | 扩展检测维度时查阅 |
| docs/workflow.md | 操作手册 | 执行流程时查阅 |
| docs/responsibility-matrix.md | 权责清单 | 判断分工边界 |
| docs/report.md | 执行报告 | 查看最近一次结果 |
| scripts/ | 规则引擎 | 自动执行检测 |
| sample/ | 检测对象 | 执行检测时作为输入 |
| data/ | 检测产出 | 领域建模结果 |
