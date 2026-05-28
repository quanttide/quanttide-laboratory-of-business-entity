# QtCloud HR 用户手册

> 写给 HR 同事的操作指南。系统将 hr@quanttide.com 邮件中的招聘流程，变成可视化的看板和可追踪的记录。

---

## 一、核心概念

```
候选人 ──→ 申请 ──→ 岗位
         (一条管道)
```

- **候选人**：投递者（一个候选人可以投递多个岗位）
- **岗位**：招聘职位（如"技术实习生""新媒体运营"）
- **申请**：候选人在某个岗位上的进度记录，包含当前阶段和流转历史

---

## 二、快速上手

### 启动系统

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/docs 查看所有可用功能。

### 第一次使用：先创建岗位

你需要先录入当前正在招聘的岗位，然后才能把候选人关联到对应的岗位上。

```bash
curl -X POST http://127.0.0.1:8000/positions \
  -H 'Content-Type: application/json' \
  -d '{"name":"技术实习生","type":"技术","headcount":5}'
```

其他岗位同理：

```bash
curl -X POST ... -d '{"name":"新媒体运营","type":"运营","headcount":2}'
curl -X POST ... -d '{"name":"PM实习生","type":"产品","headcount":1}'
```

### 录入候选人：两种方式

**方式一：单个录入（从邮件中看到一封处理一封）**

```bash
curl -X POST http://127.0.0.1:8000/applications/quick \
  -H 'Content-Type: application/json' \
  -d '{
    "candidate_name": "陈忠洋",
    "candidate_email": "czy@test.com",
    "candidate_school": "东南大学",
    "position_name": "技术实习生"
  }'
```

系统会自动创建候选人并关联到指定岗位。`position_name` 必须是已在系统中创建的岗位名称。

**方式二：批量导入（整理完一批邮件后一次性导入）**

把邮件整理成 CSV 文件：

```csv
name,email,school,major,position,stage
陈忠洋,czy@test.com,东南大学,计算机,技术实习生,new
孙雨馨,syx@test.com,山东大学,新闻,新媒体运营,contacted
赵娅兰,zyl@test.com,西安交通大学,软件工程,技术实习生,exam_sent
```

然后上传：

```bash
curl -X POST http://127.0.0.1:8000/applications/import-csv \
  -F "file=@applicants.csv"
```

`stage` 列可选，不填默认为 `new`。如果候选人邮箱已存在，系统会自动匹配已有记录，不会重复创建。列名支持中文：

```csv
姓名,邮箱,学校,专业,岗位,阶段
```

---

## 三、看板（Pipeline）

看板是系统的核心视图，用来一眼看清所有申请的状态分布。

```bash
curl http://127.0.0.1:8000/pipeline
```

返回示例：

```json
{
  "stages": {
    "new": [ ... ],
    "contacted": [ ... ],
    "exam_sent": [ ... ]
  },
  "summary": {
    "total": 24,
    "by_stage": { "new": 12, "contacted": 5, "exam_sent": 3, ... },
    "need_attention": 4
  }
}
```

- `stages`：每个阶段下的申请列表，按更新时间倒序
- `summary.total`：当前所有申请总数
- `summary.by_stage`：各阶段分布
- `summary.need_attention`：**需要你优先处理的申请数**（= exam_received + evaluating 阶段总数）

---

## 四、阶段流转

每个申请的生命周期如下。只能按箭头方向前进，不能跳跃或倒退。

```
new → contacted → exam_sent → exam_received → evaluating → interview → offer → closed
```

各阶段含义：

| 阶段 | 含义 | HR 在该阶段的操作 |
|------|------|-----------------|
| `new` | 新投递，未处理 | 查看简历，决定是否联系 |
| `contacted` | 已联系候选人 | 记录联系方式，发笔试 |
| `exam_sent` | 笔试已发送 | 记录发送时间，设置截止日期 |
| `exam_received` | 笔试已回收 | 下载附件，转发给评估人 |
| `evaluating` | 评估中 | 跟进评估人进度 |
| `interview` | 面试阶段 | 安排面试时间/形式/面试官 |
| `offer` | 已发 Offer | 跟进确认结果 |
| `closed` | 已关闭（入职/拒绝/放弃） | — |

推进阶段：

```bash
curl -X POST http://127.0.0.1:8000/applications/1/transition \
  -H 'Content-Type: application/json' \
  -d '{"stage": "contacted"}'
```

每次流转都会被记录到 `stage_history` 中，可以在申请详情里追溯。

---

## 五、候选人管理

### 搜索候选人

```bash
# 全文搜索（姓名/邮箱/学校/专业）
curl "http://127.0.0.1:8000/candidates?q=陈"

# 按学校筛选
curl "http://127.0.0.1:8000/candidates?school=东南大学"

# 按来源筛选
curl "http://127.0.0.1:8000/candidates?source=email"

# 按时间范围
curl "http://127.0.0.1:8000/candidates?date_from=2026-05-01T00:00:00&date_to=2026-05-31T00:00:00"
```

### 查看候选人详情

```bash
curl http://127.0.0.1:8000/candidates/1
```

### 更新候选人信息

```bash
curl -X PATCH http://127.0.0.1:8000/candidates/1 \
  -H 'Content-Type: application/json' \
  -d '{"tags": "IMPORTANT,REPLIED"}'
```

`tags` 字段支持自由标签，对标邮件中的 `IMPORTANT`、`REPLIED`、`FLAGGED`。

---

## 六、岗位管理

```bash
# 列出所有岗位
curl http://127.0.0.1:8000/positions

# 按类型筛选
curl "http://127.0.0.1:8000/positions?type=技术"

# 只看活跃岗位
curl "http://127.0.0.1:8000/positions?active=true"
```

---

## 七、统计

```bash
# 各阶段人数统计
curl http://127.0.0.1:8000/applications/stats
```

返回示例：

```json
[
  {"stage": "new", "count": 12},
  {"stage": "contacted", "count": 5},
  {"stage": "exam_sent", "count": 3}
]
```

---

## 八、日常使用建议

**建议每天早上先看 Pipeline：**

```bash
curl http://127.0.0.1:8000/pipeline | python3 -c "
import sys, json
d = json.load(sys.stdin)
s = d['summary']
print(f'共 {s[\"total\"]} 位申请者')
print(f'待处理: {s[\"need_attention\"]}')
for st, cnt in s['by_stage'].items():
    if cnt > 0:
        print(f'  {st}: {cnt}')
"
```

**对应邮件中的标签习惯：**

| 邮件标签 | 系统操作 |
|---------|---------|
| IMPORTANT | 在候选人 tags 中添加 "IMPORTANT" |
| REPLIED | 推进到对应阶段即可，stage_history 自动记录 |
| FORWARD | 在 assigned_to 中标注转发给了谁 |
| FLAGGED | 在候选人 tags 中添加 "FLAGGED" |

---

## 九、常见问题

**Q: 候选人已经在系统里了，但我想把他调到另一个岗位？**

目前需要创建一条新的申请记录（通过 quick 接口），系统会复用已有的候选人信息。后续版本会支持一键转岗。

**Q: 发错了阶段，想回退？**

当前版本不允许回退。如果操作失误，可以直接关闭当前申请（`closed`），然后重新创建一条。

**Q: CSV 导入时说岗位不存在？**

需要先通过 `POST /positions` 创建岗位，CSV 中的岗位名称必须与系统中创建的完全一致。
