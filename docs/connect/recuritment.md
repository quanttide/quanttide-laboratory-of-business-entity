# 招聘邮箱操作经验

基于 `lark-cli mail` 操作 HR 邮箱（hr@quanttide.com）的经验总结。

## 邮箱身份确认

操作前先确认当前身份对应的邮箱：

```bash
lark-cli mail user_mailboxes profile --params '{"user_mailbox_id":"me"}'
```

操作 HR 邮箱时指定 `--mailbox hr@quanttide.com`。

## 招聘日报生成

```bash
qtadmin qtrecurit status
```

通过读取 HR 邮箱全量邮件，按主题关键词匹配岗位分类，输出投递总量、岗位分布和投递趋势。

## 笔试题提交者识别

笔试流程通常为：HR 发送笔试题 → 申请人回复提交答案。

### 搜索方法

```bash
# 搜索含关键词的邮件
lark-cli mail +triage --mailbox hr@quanttide.com --query "笔试题" --max 100
lark-cli mail +triage --mailbox hr@quanttide.com --query "笔试答案" --max 100
lark-cli mail +triage --mailbox hr@quanttide.com --query "作答" --max 100
```

### 完整识别流程

1. **查已发送**：搜索 SENT 文件夹中 HR 发出的笔试题邮件，获取收件人地址
   ```bash
   lark-cli mail +triage --mailbox hr@quanttide.com --filter '{"folder":"SENT"}' --query "笔试题" --max 100
   ```

2. **看具体邮件**：查看某封邮件的收件人
   ```bash
   lark-cli mail +message --mailbox hr@quanttide.com --message-id <id>
   ```

3. **查回复**：搜索 INBOX 中该收件人是否有回复
   ```bash
   lark-cli mail +triage --mailbox hr@quanttide.com --query "<邮箱地址>" --max 20
   ```

### 邮件模式

笔试题相关邮件常见模式：

| 模式 | 说明 | 示例主题 |
|------|------|---------|
| HR 主动发送 | HR 第一次发送笔试题 | `量潮科技数据工程师笔试题` |
| 申请人回复 | 申请人在同一线程回复答案 | `回复：量潮科技数据工程师笔试题` |
| 申请人主动提交 | 申请人直接发邮件提交 | `笔试题提交，提交人：XXX` |
| 附件标注 | 主题中标注附件内容 | `PM实习生 XXX 笔试答案（附件）` |

### 关键经验

- **不要只搜关键词**：许多申请人在回复链中提交答案，主题不含"笔试题"关键词，需通过 SENT 文件夹追溯到 HR 发出的邮件，再核查回复
- **查 SENT 文件夹**：HR 发出的原始笔试题只在 SENT 中可见，要点是找到"谁收到了笔试题"
- **回查 INBOX**：找到收件人后，在 INBOX 中搜索其邮箱地址，看是否有后续回复
- **连招示例**：`--mailbox hr@quanttide.com` + `--filter '{"folder":"SENT"}'` 是查看已发送邮件的标准组合

## 候选人考核进度核查

查看某岗位的招聘进度：

```bash
# 搜岗位关键词
lark-cli mail +triage --mailbox hr@quanttide.com --query "<岗位>" --max 100

# 看某封申请邮件的正文（含附件）  
lark-cli mail +message --mailbox hr@quanttide.com --message-id <id>

# 查 HR 回复了什么
lark-cli mail +triage --mailbox hr@quanttide.com --filter '{"folder":"SENT"}' --query "<申请人关键词>" --max 20
```

### 考核阶段判断

| 阶段 | 标志 | 判断方法 |
|------|------|---------|
| 已投递 | 申请人发来简历邮件 | INBOX 中搜申请人 |
| HR 已回复 | HR 发送了回复邮件 | SENT 中搜申请人 |
| 已发送笔试题 | HR 回复中含有笔试题目 | 查看 HR 回复的正文 |
| 已提交笔试 | 申请人回复笔试答案 | INBOX 中申请人有含答案的回复 |
| 已录取 | HR 发送了录取通知 | SENT 中 HR 发送了 offer 相关邮件 |

## 消息撤回

发错消息时可按 message_id 撤回：

```bash
lark-cli im messages delete --params '{"message_id":"<id>"}' --yes
```
