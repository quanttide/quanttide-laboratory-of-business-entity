# 飞书群联系人搜索与通知

搜索群并通知指定成员的流程：

```bash
# 一键发送（按群名和姓名搜索）
./send_notice.sh --chat "量潮科技" --at "刘婧怡" --msg "通知内容"

# 或直接指定 ID 跳过搜索
./send_notice.sh --chat oc_xxx --at ou_xxx --msg "通知内容"
```
