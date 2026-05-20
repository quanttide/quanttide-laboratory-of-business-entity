# ROADMAP

## 现状

五个阶段全部完成。工具链已从 shell 脚本统一为 Python CLI，原始知识库和领域数据整理为 tests/fixtures/input 和 output，loader 层剥离了硬编码路径假设。

待解决的问题集中在检测精度和测试质量上。

## 待办

### 修复检测精度

- find-undefined-terms 对模板术语（`第X条 定义`）的误报过滤
- fusion-check 中 "交接" 跨领域重叠需人确认
- fusion-check 中 qtdata-index.md 引用断裂需人确认

### 增强测试

- 现有测试仅验证返回值，未验证输出内容
- 为每个检测模块补充正例和反例断言

### 代码质量

- 无阻塞问题
