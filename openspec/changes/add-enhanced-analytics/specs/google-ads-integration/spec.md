# Google Ads Integration Capability

## ADDED Requirements

### Requirement: Google Ads Data Fetching

系统应当（SHOULD）支持获取 Google Ads 数据用于交叉验证分析。

#### Scenario: Ads data fetch when configured
- **WHEN** Google Ads credentials are configured in .env
- **AND** the report generation is run
- **THEN** the system SHALL fetch Google Ads data including:
  - 广告支出 (cost)
  - 点击数 (clicks)
  - 展示数 (impressions)
  - 转化数 (conversions)
  - 广告系列明细

#### Scenario: Graceful degradation when not configured
- **WHEN** Google Ads credentials are NOT configured
- **THEN** the system SHALL skip Ads data fetching
- **AND** SHALL NOT display any error
- **AND** SHALL generate the report without Ads analysis section

#### Scenario: Error handling for API failures
- **WHEN** Google Ads API returns an error
- **THEN** the system SHALL log a warning
- **AND** SHALL continue with the report generation
- **AND** SHALL note in the report that Ads data is unavailable

---

### Requirement: Cross-Channel Analysis

当 Google Ads 数据可用时，报告应当（SHOULD）包含付费流量与自然流量的对比分析。

#### Scenario: Paid vs Organic comparison
- **WHEN** both GA4 and Google Ads data are available
- **THEN** the report SHOULD include:
  - 付费流量占比分析
  - CTR 对比（广告 vs 自然搜索）
  - 转化路径分析
  - 广告效果与 SEO 协同建议

#### Scenario: Campaign performance analysis
- **WHEN** Google Ads campaign data is available
- **THEN** the report SHOULD highlight:
  - TOP 表现广告系列
  - 需要优化的低效广告
  - 预算分配建议
