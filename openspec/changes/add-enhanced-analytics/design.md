# Design: Enhanced Analytics Features

## 架构决策

### 1. 日期范围参数设计

**方案选择：命令行参数 + 环境变量**

| 方案 | 优点 | 缺点 |
|------|------|------|
| 仅命令行参数 | 灵活，一次性使用 | 自动化任务需要脚本传参 |
| 仅环境变量 | 配置持久化 | 修改不便 |
| **两者结合** | 命令行优先，环境变量作为默认值 | 略复杂 |

**决策：两者结合**
- 命令行参数优先，覆盖环境变量
- 不指定时，默认使用过去 7 天

**参数格式：**
```
--start-date YYYY-MM-DD   # 开始日期
--end-date YYYY-MM-DD     # 结束日期
--period [last-week|last-month|last-quarter|custom]
```

### 2. 时间段传递机制

**数据流：**
```
main.py (解析日期参数)
    ↓
Fetcher.__init__(start_date, end_date)
    ↓
Fetcher._get_date_ranges() → 使用传入的日期而非计算
    ↓
Analyzer.analyze(ga4_data, gsc_data, date_range)
    ↓
生成报告时包含时间段
```

### 3. Google Ads 集成架构

**API 选择：Google Ads API v14**

**认证方式：**
- 使用 OAuth 2.0 客户端凭据（推荐用于自动化）
- 需要：Developer Token, Client ID, Customer ID

**数据获取范围：**
```python
# 主要指标
- 广告支出 (cost_micros)
- 点击数 (clicks)
- 展示数 (impressions)
- 转化数 (conversions)
- 转化价值 (conversions_value)

# 维度
- 按日期
- 按广告系列
- 按设备类型
```

**与现有数据整合：**
```python
data = {
    'ga4': ga4_data,
    'gsc': gsc_data,
    'ads': google_ads_data,  # 新增
}
```

### 4. 可选性设计

Google Ads 数据设为**可选**：
- 如果未配置 Google Ads 凭据，程序正常运行
- 报告中自动跳过广告分析部分
- 不影响现有功能

## 配置项设计

**.env 新增：**
```
# Google Ads Configuration (Optional)
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=
```

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 日期格式错误 | 明确报错，提示正确格式 |
| 结束日期早于开始日期 | 报错 |
| Google Ads 未配置 | 跳过广告数据，正常生成报告 |
| Google Ads API 失败 | 警告并继续，报告标注数据缺失 |
