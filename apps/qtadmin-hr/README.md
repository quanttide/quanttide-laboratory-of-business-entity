# QtCloud HR — 招聘系统 MVP

基于 FastAPI + SQLite 的招聘管理系统。

岗位定义来自 **QtCloud Org** 系统（`../qtadmin-org`）。

## 数据模型

```
Org:   Position ── 岗位定义

HR:    Plan ── 招聘计划（headcount, period, status）
         │
         Recruitment ── 招聘活动（recruiter, target_date, status）
           │
           Applicant ── 申请者（stage, school, email, assigned_to）
```

- **Plan**：聚合根，针对一个 Org Position 的招聘计划
- **Recruitment**：聚合根，一次具体的招聘活动
- **Applicant**：子实体，属于 Recruitment，记录申请者信息和进度

## 快速开始

```bash
# 终端 1：Org
cd ../qtadmin-org
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# 终端 2：HR
cd ../qtadmin-hr
QTCLOUD_HR_ORG_API_URL=http://127.0.0.1:8001 uvicorn app.main:app --reload --port 8000
```

## API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/plans` | GET/POST | 计划列表/创建 |
| `/plans/{id}` | GET/PATCH/DELETE | 计划详情/更新/删除 |
| `/recruitments` | GET/POST | 活动列表/创建 |
| `/recruitments/{id}` | GET/PATCH/DELETE | 活动详情/更新/删除 |
| `/recruitments/{id}/applicants` | GET/POST | 活动的申请者列表/创建 |
| `/recruitments/{id}/applicants/{aid}` | GET/PATCH/DELETE | 申请者详情/更新/删除 |
| `/recruitments/{id}/applicants/{aid}/transition` | POST | 推进阶段 |
| `/pipeline` | GET | 看板（按 Applicant.stage 聚合） |

## 状态流转

```
new → contacted → exam_sent → exam_received → evaluating → interview → offer → closed
```

## 一站式创建

```bash
# 1. Org 创建岗位
curl -X POST http://127.0.0.1:8001/positions -d '{"name":"技术实习生","department":"技术部"}'

# 2. HR 创建计划
curl -X POST http://127.0.0.1:8000/plans -d '{"org_position_id":1,"headcount":3,"period":"2026 Q2"}'

# 3. HR 创建招聘活动
curl -X POST http://127.0.0.1:8000/recruitments -d '{"plan_id":1,"name":"5月招聘","recruiter":"刘婧怡"}'

# 4. 添加申请者
curl -X POST http://127.0.0.1:8000/recruitments/1/talents -d '{"real_name":"张三","email":"zs@test.com","school":"某大学"}'
```
