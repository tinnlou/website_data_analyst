# Tasks: LLM Data Accuracy Enhancement

## 1. Prompt 模板增强

- [x] 1.1 在 `templates/analysis_prompt.md` 中添加数据分段边界标记说明
- [x] 1.2 添加数据引用标注的 few-shot 示例
- [x] 1.3 添加明确的"禁止混淆"指令段落
- [x] 1.4 更新数据展示格式说明（推荐使用表格）

## 2. 数据格式化模块

- [x] 2.1 在 `gemini_analyzer.py` 中创建 `_format_data_as_table()` 方法
- [x] 2.2 为每条数据记录添加唯一标识符（ID 列）
- [x] 2.3 实现数据边界标记插入逻辑
- [x] 2.4 更新 `analyze()` 方法使用新格式

## 3. 数据验证增强

- [x] 3.1 增强 `_generate_verification_footer()` 方法，添加更多关键指标
- [x] 3.2 在 footer 中生成数据摘要表供人工比对

## 4. 测试与验证

- [x] 4.1 Python 语法验证通过
- [ ] 4.2 用户进行实际运行测试（可选）
