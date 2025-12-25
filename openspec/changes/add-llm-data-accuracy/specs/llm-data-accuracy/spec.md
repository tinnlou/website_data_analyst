# LLM Data Accuracy Capability

## ADDED Requirements

### Requirement: Structured Data Presentation

系统在向 LLM 提交分析数据时，必须（SHALL）使用结构化格式展示数据，以减少数据混淆风险。

#### Scenario: Data presented in table format
- **WHEN** GA4 or Search Console data is prepared for LLM analysis
- **THEN** the data SHALL be formatted as Markdown tables with:
  - Unique row identifiers (e.g., KW001, PAGE001)
  - Clear column headers
  - One data type per table

#### Scenario: Data sections clearly bounded
- **WHEN** multiple data types are included in a single prompt
- **THEN** each data section SHALL be wrapped with distinct boundary markers (e.g., HTML comments)

### Requirement: Data Reference Requirement

Prompt 模板必须（SHALL）要求 LLM 在报告中明确引用数据来源。

#### Scenario: Reference instruction in prompt
- **WHEN** the analysis prompt is constructed
- **THEN** it SHALL include explicit instructions requiring data source references for each analytical conclusion

#### Scenario: Few-shot examples provided
- **WHEN** reference format is specified
- **THEN** at least one example of correct reference format SHALL be provided in the prompt

### Requirement: Data Isolation Instructions

Prompt 必须（SHALL）包含明确的数据隔离指令，防止不同数据源或不同时间段的数据混淆。

#### Scenario: Time period isolation
- **WHEN** current week and previous week data are presented
- **THEN** prompt SHALL include explicit instructions to distinguish between time periods

#### Scenario: Data source isolation
- **WHEN** GA4 and Search Console data are presented together
- **THEN** prompt SHALL include instructions to attribute metrics to correct data source

### Requirement: Verification Footer

生成的分析报告必须（SHALL）包含数据验证摘要，便于人工核对。

#### Scenario: Key metrics summary
- **WHEN** analysis report is generated
- **THEN** a verification footer SHALL be appended containing:
  - Key metrics from original data
  - Data source attribution
  - Report generation timestamp
