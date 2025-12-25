# Change: Add Enhanced Analytics Features

## Why

当前系统存在以下限制：

1. **固定时间范围** - 只能分析过去 7 天的数据，无法自定义时间段
2. **时间段不透明** - 生成的报告中没有清晰标注分析的具体时间段
3. **数据来源单一** - 只有 GA4 和 GSC 数据，缺少付费广告数据交叉验证

用户作为运营总监，需要：
- 灵活选择分析周期（如：促销活动期间、季度对比）
- 报告中清晰看到数据的时间范围
- 将 Google Ads 数据与自然流量对比，深入分析问题根因

## What Changes

### 功能 1：自定义时间段

**命令行参数扩展：**
```bash
# 指定日期范围
python src/main.py --start-date 2024-12-01 --end-date 2024-12-15

# 预设周期
python src/main.py --period last-week
python src/main.py --period last-month
python src/main.py --period last-quarter
```

**影响范围：**
- `src/main.py` - 添加日期参数解析
- `src/fetchers/ga4_fetcher.py` - 支持外部传入日期范围
- `src/fetchers/gsc_fetcher.py` - 支持外部传入日期范围

### 功能 2：报告中显示分析时间段

**报告增强：**
- 在报告头部添加明确的时间段标注
- 在数据验证区域显示数据采集时间
- 在 Notion 页面标题中包含日期范围

**影响范围：**
- `src/analyzers/gemini_analyzer.py` - 数据格式化时添加时间段信息
- `templates/analysis_prompt.md` - Prompt 中包含时间段
- `src/publishers/notion_publisher.py` - 页面标题包含日期

### 功能 3：Google Ads 数据集成

**新增数据源：**
- 新建 `src/fetchers/google_ads_fetcher.py`
- 获取广告支出、点击、转化数据
- 与自然流量数据进行对比分析

**分析增强：**
- 付费流量 vs 自然流量对比
- CTR 和 CPC 趋势分析
- 广告效果与 SEO 协同分析

**影响范围：**
- 新增 `src/fetchers/google_ads_fetcher.py`
- `requirements.txt` - 添加 `google-ads` 依赖
- `.env.example` - 添加 Google Ads 配置项
- `src/main.py` - 集成 Google Ads 数据获取
- `src/analyzers/gemini_analyzer.py` - 处理 Ads 数据
- `templates/analysis_prompt.md` - 添加广告分析框架

## Impact

- **New dependencies**: `google-ads` Python SDK
- **New config**: Google Ads 开发者令牌、客户 ID
- **Affected specs**: 新增 `custom-date-range` 和 `google-ads-integration` 能力规范
