# Custom Date Range Capability

## ADDED Requirements

### Requirement: Custom Date Range Selection

用户必须（SHALL）能够通过命令行参数指定分析的时间范围。

#### Scenario: Explicit date range via command line
- **WHEN** user runs the command with `--start-date 2024-12-01 --end-date 2024-12-15`
- **THEN** the system SHALL fetch data for the specified date range
- **AND** SHALL display an error if dates are invalid or end-date is before start-date

#### Scenario: Preset period shortcuts
- **WHEN** user runs the command with `--period last-month`
- **THEN** the system SHALL calculate the appropriate date range
- **AND** SHALL support `last-week`, `last-month`, `last-quarter` options

#### Scenario: Default behavior unchanged
- **WHEN** user runs the command without date parameters
- **THEN** the system SHALL default to the last 7 days (current behavior)

---

### Requirement: Date Range Display in Reports

生成的报告必须（SHALL）清晰显示分析数据的时间范围。

#### Scenario: Report header includes date range
- **WHEN** a report is generated
- **THEN** the report header SHALL include the analysis period (e.g., "分析周期: 2024-12-01 至 2024-12-15")

#### Scenario: Notion page title includes date
- **WHEN** a report is published to Notion
- **THEN** the page title SHALL include the date range (e.g., "周报 2024-12-01 ~ 2024-12-15")

#### Scenario: Data verification section shows timestamps
- **WHEN** the data verification section is generated
- **THEN** it SHALL display the exact data fetch timestamp and date ranges
