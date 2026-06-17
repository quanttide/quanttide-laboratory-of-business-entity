# 飞书群联系人搜索与通知

搜索群并通知指定成员的流程：

```bash
# 1. 按名称搜索群
lark-cli im +chat-search --query "全员" --as user

# 2. 名称搜索无结果时，列出所有群查找
lark-cli im +chat-list --as user

# 3. 按姓名搜索成员，获取 open_id
lark-cli contact +search-user --query "刘" --as user

# 4. 发送消息并 @ 指定成员
lark-cli im +messages-send \
  --chat-id oc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --markdown "<at user_id=\"ou_xxx\">姓名</at>\n\n消息内容" \
  --as user
```
