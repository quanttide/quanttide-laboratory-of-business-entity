# QtCloud HR — 招聘系统 MVP

基于 FastAPI + SQLite 的招聘申请者管道管理。

岗位定义来自 **QtCloud Org** 系统（`../qtadmin-org`）。HR 系统通过 `Requisition`（招聘需求）引用 Org 的 `Position`（岗位定义）。

## 快速开始

需要同时启动 Org 和 HR 两个服务：

```bash
# 终端 1：启动 Org 系统
cd ../qtadmin-org
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# 终端 2：启动 HR 系统
cd ../qtadmin-hr
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

HR 访问 http://127.0.0.1:8000/docs，Org 访问 http://127.0.0.1:8001/docs。

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/candidates` | GET/POST | 列出（支持 q/school/source/degree/tag/date 过滤）/创建 |
| `/candidates/{id}` | GET/PATCH/DELETE | 详情/更新/删除 |
| `/requisitions` | GET/POST | 列出/创建招聘需求（需先有 Org Position） |
| `/requisitions/{id}` | GET/PATCH/DELETE | 详情/更新/删除 |
| `/applications` | GET/POST | 列出（支持 stage/candidate/requisition/assigned_to/date 过滤）/创建 |
| `/applications/quick` | POST | 按姓名+邮箱+Org 岗位名称直接创建 |
| `/applications/import-csv` | POST | 上传 CSV 批量导入（岗位名自动查询 Org） |
| `/applications/stats` | GET | 各阶段人数统计 |
| `/applications/{id}` | GET/PATCH/DELETE | 详情/更新/删除 |
| `/applications/{id}/transition` | POST | 推进阶段状态 |
| `/pipeline` | GET | 看板视图（含 summary） |

## 状态流转

```
new → contacted → exam_sent → exam_received → evaluating → interview → offer → closed
```

## CSV 导入格式

```csv
name,email,school,major,position,stage
张三,zhangsan@test.com,某理工大学,计算机,技术实习生,contacted
```

`position` 列是 Org 系统中的岗位名称。列名支持中文。

## 数据模型

```
Org:   Position (1) ── 岗位定义
                      │
HR:    Requisition (N) ── 招聘需求
                      │
       Application (N) ── 申请流程
                      │
       Candidate (1)  ── 候选人
```
