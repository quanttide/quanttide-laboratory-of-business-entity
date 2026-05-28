# QtCloud HR — 招聘系统 MVP

基于 FastAPI + SQLite 的招聘申请者管道管理。

## 快速开始

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs 查看交互式 API 文档。

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/candidates` | GET/POST | 列出（支持 q/school/source/degree/tag/date 过滤）/创建 |
| `/candidates/{id}` | GET/PATCH/DELETE | 详情/更新/删除 |
| `/positions` | GET/POST | 列出（支持 q/type/active 过滤）/创建 |
| `/positions/{id}` | GET/PATCH/DELETE | 详情/更新/删除 |
| `/applications` | GET/POST | 列出（支持 stage/candidate/position/assigned_to/date 过滤）/创建 |
| `/applications/quick` | POST | 按姓名+邮箱+岗位名称直接创建（自动解析/创建候选人） |
| `/applications/import-csv` | POST | 上传 CSV 批量导入（支持中英文列名，可选指定阶段） |
| `/applications/stats` | GET | 各阶段人数统计 |
| `/applications/{id}` | GET/PATCH/DELETE | 详情/更新/删除 |
| `/applications/{id}/transition` | POST | 推进阶段状态 |
| `/pipeline` | GET | 看板视图（含 summary：总数/各阶段分布/待处理数） |

## 状态流转

```
new → contacted → exam_sent → exam_received → evaluating → interview → offer → closed
```

每个阶段只能前进到特定后续阶段（`STAGE_TRANSITIONS` 控制），不可跳跃或倒退。

## CSV 导入格式

```csv
name,email,school,major,position,stage
张三,zhangsan@test.com,某理工大学,计算机,技术实习生,contacted
李四,lisi@test.com,某大学,,新媒体运营,new
```

`stage` 列可选，不填默认 `new`。列名支持中文（`姓名`/`邮箱`/`学校`/`岗位`/`阶段`）。重复 email 自动匹配已有候选人。

## 数据模型

```
Candidate (1) ──── (N) Application (N) ──── (1) Position
```
