# Change: Add LLM Data Accuracy Enhancement

## Why

当处理大量数据时，LLM 容易出现"张冠李戴"问题——将某个实体的属性错误地归结到另一个实体上。例如：
- 将某个关键词的点击数误报到另一个关键词
- 混淆不同页面的跳出率
- 将上周数据和本周数据混淆

这会严重影响分析报告的准确性和可信度。

## What Changes

### 1. 数据上下文标记增强
- 为每个数据块添加明确的边界标记（如 `<!-- GA4-OVERVIEW-START -->` 和 `<!-- GA4-OVERVIEW-END -->`）
- 在数据表格中为每行添加唯一标识符

### 2. 分段处理架构
- 将大数据集拆分成独立的小批次进行分析
- 每个批次只关注单一维度（如关键词分析、页面分析）
- 避免一次性将所有数据发送给 LLM

### 3. 数据校验与引用机制
- 要求 LLM 在每个结论后标注数据源引用（如 `[GA4-KW-001]`）
- 在生成报告后进行自动化校验，验证引用的数据是否匹配

### 4. Prompt 工程优化
- 使用表格格式而非 JSON 展示数据（更易于 LLM 理解行列关系）
- 添加明确的数据隔离指令
- 使用 few-shot 示例展示正确的数据引用方式

## Impact

- **Affected specs**: 新增 `llm-data-accuracy` 能力规范
- **Affected code**: 
  - `src/analyzers/gemini_analyzer.py` - 修改数据处理和分析逻辑
  - `templates/analysis_prompt.md` - 增强 prompt 模板
  - 可能新增 `src/analyzers/data_validator.py` - 数据校验模块
