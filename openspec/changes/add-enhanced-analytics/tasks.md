# Tasks: Add Enhanced Analytics Features

## Phase 1: 自定义时间段 ✅

- [x] 1.1 在 `main.py` 中添加 `--start-date` 和 `--end-date` 参数
- [x] 1.2 添加 `--period` 预设选项（last-week, last-month, last-quarter）
- [x] 1.3 实现日期验证逻辑（格式、范围合理性）
- [x] 1.4 修改 `GA4Fetcher` 支持外部传入日期范围
- [x] 1.5 修改 `GSCFetcher` 支持外部传入日期范围

## Phase 2: 报告中显示时间段 ✅

- [x] 2.1 在 `_format_data_as_tables()` 顶部添加时间段显示
- [x] 2.2 修改 Notion 发布，页面标题包含日期范围

## Phase 3: Google Ads 集成 ⏸️ 暂时跳过

> 用户暂无 Google Ads API 凭据，后续有需要时可继续实施

## 验证 ✅

- [x] 测试 `--period last-month` 
- [x] 测试 `--start-date 2024-12-01 --end-date 2024-12-15`
- [x] 验证报告中包含时间段信息
