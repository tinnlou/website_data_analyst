# Tasks: Improve Report Quality

## 1. 修复 GA4 字段映射（紧急）✅

- [x] 1.1 修正设备分布：`device_breakdown` → `devices`
- [x] 1.2 修正设备字段：`deviceCategory` → `device`, `activeUsers` → `users`
- [x] 1.3 添加地区分布 `geo` → `countries` 表格格式化
- [x] 1.4 修正热门页面字段：`screenPageViews` → `pageViews`
- [x] 1.5 修正流量来源字段：`activeUsers` → `users`

## 2. 修复 GSC 字段映射 ✅

- [x] 2.1 添加 GSC 设备分布 `devices` 表格格式化
- [x] 2.2 添加 GSC 国家分布 `countries` 表格格式化
- [x] 2.3 修正 CTR 优化机会：`opportunities.queries` → `opportunities.opportunities`

## 3. 数据格式标准化 ✅

- [x] 3.1 将跳出率转换为百分比格式（×100）
- [x] 3.2 统一数值精度：保留 2 位小数

## 4. 扩展 GA4 数据展示 ✅

- [x] 4.1 添加新用户数据（newUsers）
- [x] 4.2 添加互动率数据（engagementRate）

## 5. 增强分析 Prompt ✅

- [x] 5.1 添加用户分群分析章节
- [x] 5.2 添加表格格式规则（禁止代码块）
- [x] 5.3 添加 ID 引用规则（只用已展示 ID）

## 6. 验证 ✅

- [x] 6.1 Python 语法检查通过
- [x] 6.2 运行 dry-run 验证所有数据板块展示
- [x] 6.3 确认设备和地区数据正确显示
- [x] 6.4 确认新用户数据正确显示
