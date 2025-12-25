# Change: Improve Report Quality

## Why

分析生成的报告后，发现以下问题影响报告质量：

### 数据字段映射问题（完整排查结果）

**GA4 数据问题：**

| 数据类型 | Fetcher 返回的 Key | Analyzer 查找的 Key | 状态 |
|----------|-------------------|-------------------|------|
| 设备分布 | `devices` | `device_breakdown` | ❌ 不匹配 |
| 地区分布 | `geo` | 未处理 | ❌ 缺失 |
| 热门页面 | `pageViews` | `screenPageViews` | ❌ 字段名不同 |
| 热门页面 | `avgSessionDuration` | `averageSessionDuration` | ❌ 字段名不同 |
| 流量来源 | `users` | `activeUsers` | ❌ 字段名不同 |

**GSC 数据问题：**

| 数据类型 | Fetcher 返回的 Key | Analyzer 查找的 Key | 状态 |
|----------|-------------------|-------------------|------|
| 设备分布 | `devices` | 未处理 | ❌ 缺失 |
| 国家分布 | `countries` | 未处理 | ❌ 缺失 |
| CTR优化机会 | `opportunities` | `opportunities.queries` | ❌ 结构不对 |

**数据格式问题：**
1. 跳出率显示为原始小数（如 `0.218`）而非百分比（`21.8%`）
2. 表格被代码块包裹，在 Notion 中渲染不佳

### 分析维度不足（运营总监视角）
1. 缺少转化漏斗分析
2. 缺少用户分群分析（新用户 vs 回访用户）
3. 缺少时间维度分析（流量趋势、高峰期识别）
4. 缺少出口页分析
5. 缺少页面深度分析

## What Changes

### 1. 修复 GA4 数据字段映射
- `devices` 改为正确读取（非 `device_breakdown`）
- 添加 `geo` 地区数据处理
- 修正 `top_pages` 字段名：`pageViews` → `screenPageViews`
- 修正 `traffic_sources` 字段名：`users` → `activeUsers`

### 2. 修复 GSC 数据字段映射
- 添加 GSC `devices` 设备分布处理
- 添加 GSC `countries` 国家分布处理
- 修正 `opportunities` 结构为 `opportunities`（非 `opportunities.queries`）

### 3. 数据格式标准化
- 将跳出率乘以 100 转换为百分比格式
- 统一数值精度为 2 位小数

### 4. 扩展数据获取（GA4 增强）
- 添加新用户/回访用户维度
- 添加按日期的流量趋势
- 添加参与度指标

### 5. 增强分析 Prompt
- 添加转化漏斗分析指导
- 强化表格格式要求
- 强调只使用已展示的 ID

## Impact

- **Affected code**: 
  - `src/analyzers/gemini_analyzer.py` - 修复所有字段映射
  - `src/fetchers/ga4_fetcher.py` - 添加新数据维度
  - `templates/analysis_prompt.md` - 增强分析指导
