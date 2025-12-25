# Report Quality Capability

## ADDED Requirements

### Requirement: Complete Data Field Mapping

系统必须（SHALL）正确映射 GA4 数据字段，确保所有获取的数据都能传递给分析模块。

#### Scenario: Device data correctly passed
- **WHEN** GA4 data contains device breakdown in `devices` field
- **THEN** the analyzer SHALL read from the correct field name
- **AND** SHALL format and display the device data in the report

#### Scenario: Geographic data correctly passed
- **WHEN** GA4 data contains geographic breakdown in `geo` field
- **THEN** the analyzer SHALL read and format this data
- **AND** SHALL display country/region distribution in the report

### Requirement: Data Format Standardization

报告中的数值必须（SHALL）使用统一的格式标准。

#### Scenario: Bounce rate as percentage
- **WHEN** bounce rate data is formatted
- **THEN** it SHALL be converted from decimal to percentage (multiply by 100)
- **AND** SHALL display with "%" suffix (e.g., "21.83%")

#### Scenario: Numeric precision
- **WHEN** numeric values are displayed
- **THEN** they SHALL be rounded to 2 decimal places

### Requirement: Table Format Compliance

报告中的表格必须（SHALL）使用标准 Markdown 格式，不使用代码块。

#### Scenario: Plain Markdown tables
- **WHEN** the AI generates tables in the analysis
- **THEN** it SHALL NOT wrap tables in code block fences (```)
- **AND** tables SHALL use standard Markdown syntax directly

### Requirement: Data ID Reference Integrity

分析报告必须（SHALL）只引用原始数据中实际存在的 ID。

#### Scenario: Valid ID references only
- **WHEN** the AI references data points by ID
- **THEN** the ID SHALL exist in the provided data tables
- **AND** SHALL NOT fabricate or assume additional IDs

## MODIFIED Requirements

### Requirement: Enhanced Analysis Dimensions

分析报告应当（SHOULD）包含更丰富的运营分析维度。

#### Scenario: User segmentation analysis
- **WHEN** new vs returning user data is available
- **THEN** the report SHOULD include behavioral differences between segments

#### Scenario: Conversion funnel insights
- **WHEN** page path data shows user journey
- **THEN** the report SHOULD identify drop-off points in the conversion funnel

#### Scenario: Time-based patterns
- **WHEN** traffic data is available by date
- **THEN** the report SHOULD identify peak traffic periods and trends

#### Scenario: Exit page analysis
- **WHEN** page performance data is available
- **THEN** the report SHOULD identify pages with high exit rates as optimization opportunities
