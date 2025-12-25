"""
Gemini AI Analyzer Module.
Uses Google Gemini to analyze website data and generate actionable insights.
"""

import json
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL, PROJECT_ROOT


# Load analysis prompt template
PROMPT_TEMPLATE_PATH = PROJECT_ROOT / 'templates' / 'analysis_prompt.md'


class GeminiAnalyzer:
    """Analyzes website data using Gemini AI."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the Gemini Analyzer.
        
        Args:
            api_key: Gemini API key
            model: Model name to use (default: gemini-1.5-pro)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model or GEMINI_MODEL
        
        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)
    
    def _load_prompt_template(self) -> str:
        """Load the analysis prompt template."""
        if PROMPT_TEMPLATE_PATH.exists():
            return PROMPT_TEMPLATE_PATH.read_text(encoding='utf-8')
        else:
            return self._get_default_prompt_template()
    
    def _get_default_prompt_template(self) -> str:
        """Get the default analysis prompt template."""
        return """# 网站运营分析报告

你是一位资深的网站运营总监，拥有10年以上的数字营销和SEO经验。你的任务是分析提供的Google Analytics 4和Search Console数据，生成一份专业、详尽、可落地的周报分析。

## 重要规则

1. **数据准确性**：你只能基于下方"原始数据"部分提供的真实数据进行分析。禁止编造任何数据或假设不存在的数据。
2. **结论追溯**：每个分析结论必须引用具体的数据来源（如"根据GA4数据，会话数为X"）。
3. **可落地建议**：所有优化建议必须具体、可执行，包含明确的操作步骤。

## 分析框架

请按以下结构生成分析报告：

### 1. 执行摘要
- 本周核心数据概览（3-5个关键指标）
- 与上周对比的主要变化
- 最需要关注的1-2个问题

### 2. 流量分析
- 整体流量趋势分析
- 流量来源结构分析
- 新用户vs回访用户分析
- 设备和地区分布

### 3. SEO表现分析
- 搜索可见性变化（展示量、点击量、平均排名）
- 关键词表现分析：
  - 上升关键词
  - 下降关键词
  - 新增关键词
- 页面表现分析
- CTR优化机会识别

### 4. 用户行为分析
- 跳出率和互动率分析
- 热门页面分析
- 用户路径和转化漏斗（如有数据）

### 5. 问题诊断
识别并分析以下类型的问题：
- 流量异常波动
- 高跳出率页面
- 关键词排名下降
- CTR低于预期的查询
- 设备或地区差异过大

### 6. 优化建议
针对发现的每个问题，提供：
- **问题描述**：清晰说明问题是什么
- **影响评估**：该问题对业务的潜在影响
- **具体行动**：2-3个可立即执行的优化步骤
- **预期效果**：优化后的预期改善

### 7. 下周关注重点
- 需要持续监控的指标
- 建议执行的优化任务（按优先级排序）

---

## 原始数据

{data}

---

请基于以上数据生成详尽的分析报告。确保所有结论都有数据支撑，不要假设或编造任何未提供的信息。
"""
    
    def analyze(self, ga4_data: dict, gsc_data: dict) -> str:
        """
        Analyze the combined GA4 and Search Console data.
        
        Args:
            ga4_data: Dictionary containing GA4 data
            gsc_data: Dictionary containing Search Console data
            
        Returns:
            Markdown formatted analysis report
        """
        print("🤖 Generating AI analysis with Gemini...")
        
        # Format data as structured tables with unique IDs
        formatted_data = self._format_data_as_tables(ga4_data, gsc_data)
        
        # Load and format prompt
        prompt_template = self._load_prompt_template()
        full_prompt = prompt_template.format(data=formatted_data)
        
        # Generate analysis using new API
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,  # Lower temperature for more factual output
                top_p=0.8,
                max_output_tokens=8000,
            )
        )
        
        analysis = response.text
        
        # Add data verification footer
        analysis += self._generate_verification_footer(ga4_data, gsc_data)
        
        print("✅ Analysis generated successfully!")
        return analysis
    
    def _format_data_as_tables(self, ga4_data: dict, gsc_data: dict) -> str:
        """
        Format data as structured Markdown tables with unique IDs.
        
        This reduces LLM confusion by:
        1. Using table format instead of nested JSON
        2. Adding unique IDs to each data record
        3. Using boundary markers for data sections
        """
        output = []
        
        # Display analysis period prominently
        ga4_period = ga4_data.get('overview', {}).get('period', {}).get('current', {})
        if ga4_period:
            output.append(f"## 📅 分析时间段\n")
            output.append(f"**当前周期**: {ga4_period.get('start', 'N/A')} 至 {ga4_period.get('end', 'N/A')}")
            prev_period = ga4_data.get('overview', {}).get('period', {}).get('previous', {})
            if prev_period:
                output.append(f"**对比周期**: {prev_period.get('start', 'N/A')} 至 {prev_period.get('end', 'N/A')}")
            output.append("")
        
        output.append(f"报告生成时间: {datetime.now().isoformat()}\n")
        
        # GA4 Overview Section
        output.append("<!-- GA4-OVERVIEW-START -->")
        output.append("## GA4 数据总览\n")
        if 'overview' in ga4_data:
            overview = ga4_data['overview']
            if 'current' in overview and 'previous' in overview:
                output.append("| 指标 | 本周 | 上周 | 变化 | 数据ID |")
                output.append("|------|------|------|------|--------|")
                current = overview.get('current', {})
                previous = overview.get('previous', {})
                changes = overview.get('changes', {})
                
                metrics = [
                    ('activeUsers', '活跃用户', 'GA4-OV01', False),
                    ('newUsers', '新用户', 'GA4-OV02', False),
                    ('sessions', '会话数', 'GA4-OV03', False),
                    ('bounceRate', '跳出率(%)', 'GA4-OV04', True),  # needs percentage conversion
                    ('engagementRate', '互动率(%)', 'GA4-OV05', True),  # needs percentage conversion
                    ('screenPageViews', '页面浏览', 'GA4-OV06', False),
                    ('averageSessionDuration', '平均会话时长(秒)', 'GA4-OV07', False),
                ]
                for key, label, data_id, is_rate in metrics:
                    curr_val = current.get(key, 'N/A')
                    prev_val = previous.get(key, 'N/A')
                    change = changes.get(key, 'N/A')
                    # Convert rates from decimal to percentage
                    if is_rate and isinstance(curr_val, (int, float)):
                        curr_val = round(curr_val * 100, 2)
                    if is_rate and isinstance(prev_val, (int, float)):
                        prev_val = round(prev_val * 100, 2)
                    output.append(f"| {label} | {curr_val} | {prev_val} | {change}% | {data_id} |")
        output.append("<!-- GA4-OVERVIEW-END -->\n")
        
        # GA4 Traffic Sources
        output.append("<!-- GA4-SOURCES-START -->")
        output.append("## GA4 流量来源\n")
        if 'traffic_sources' in ga4_data:
            sources = ga4_data['traffic_sources'].get('sources', [])
            if sources:
                output.append("| ID | 来源/媒介 | 用户数 | 会话数 | 跳出率(%) |")
                output.append("|-----|-----------|--------|--------|-----------|")
                for i, source in enumerate(sources[:15], 1):
                    src_id = f"SRC{i:03d}"
                    name = source.get('source', 'N/A')
                    users = source.get('users', 'N/A')
                    sessions = source.get('sessions', 'N/A')
                    bounce_raw = source.get('bounceRate', 0)
                    bounce = round(bounce_raw * 100, 2) if isinstance(bounce_raw, (int, float)) else 'N/A'
                    output.append(f"| {src_id} | {name} | {users} | {sessions} | {bounce} |")
        output.append("<!-- GA4-SOURCES-END -->\n")
        
        # GA4 Top Pages
        output.append("<!-- GA4-PAGES-START -->")
        output.append("## GA4 热门页面\n")
        if 'top_pages' in ga4_data:
            pages = ga4_data['top_pages'].get('pages', [])
            if pages:
                output.append("| ID | 页面路径 | 浏览量 | 跳出率(%) | 平均停留时长 |")
                output.append("|-----|----------|--------|-----------|--------------|")
                for i, page in enumerate(pages[:15], 1):
                    page_id = f"PAGE{i:03d}"
                    path = page.get('pagePath', 'N/A')[:50]
                    views = page.get('pageViews', 'N/A')
                    bounce_raw = page.get('bounceRate', 0)
                    bounce = round(bounce_raw * 100, 2) if isinstance(bounce_raw, (int, float)) else 'N/A'
                    duration_sec = page.get('avgEngagementTime', 0)
                    # Format duration as mm:ss for readability
                    if isinstance(duration_sec, (int, float)):
                        mins = int(duration_sec // 60)
                        secs = int(duration_sec % 60)
                        duration = f"{mins}:{secs:02d}"
                    else:
                        duration = 'N/A'
                    output.append(f"| {page_id} | {path} | {views} | {bounce} | {duration} |")
        output.append("<!-- GA4-PAGES-END -->\n")
        
        # GA4 Device Breakdown
        output.append("<!-- GA4-DEVICES-START -->")
        output.append("## GA4 设备分布\n")
        if 'devices' in ga4_data:
            devices = ga4_data['devices'].get('devices', [])
            if devices:
                output.append("| ID | 设备类型 | 用户数 | 会话数 | 占比(%) | 跳出率(%) |")
                output.append("|-----|----------|--------|--------|--------|-----------|")
                for i, device in enumerate(devices, 1):
                    dev_id = f"DEV{i:03d}"
                    category = device.get('device', 'N/A')
                    users = device.get('users', 'N/A')
                    sessions = device.get('sessions', 'N/A')
                    pct = device.get('percentage', 'N/A')
                    bounce_raw = device.get('bounceRate', 0)
                    bounce = round(bounce_raw * 100, 2) if isinstance(bounce_raw, (int, float)) else 'N/A'
                    output.append(f"| {dev_id} | {category} | {users} | {sessions} | {pct} | {bounce} |")
        output.append("<!-- GA4-DEVICES-END -->\n")
        
        # GA4 Geo Breakdown
        output.append("<!-- GA4-GEO-START -->")
        output.append("## GA4 地区分布\n")
        if 'geo' in ga4_data:
            countries = ga4_data['geo'].get('countries', [])
            if countries:
                output.append("| ID | 国家/地区 | 用户数 | 会话数 | 占比(%) |")
                output.append("|-----|-----------|--------|--------|--------|")
                for i, country in enumerate(countries[:10], 1):
                    geo_id = f"GEO{i:03d}"
                    name = country.get('country', 'N/A')
                    users = country.get('users', 'N/A')
                    sessions = country.get('sessions', 'N/A')
                    pct = country.get('percentage', 'N/A')
                    output.append(f"| {geo_id} | {name} | {users} | {sessions} | {pct} |")
        output.append("<!-- GA4-GEO-END -->\n")
        
        # Search Console Overview
        output.append("<!-- GSC-OVERVIEW-START -->")
        output.append("## Search Console 数据总览\n")
        if 'overview' in gsc_data:
            overview = gsc_data['overview']
            if 'current' in overview and 'previous' in overview:
                output.append("| 指标 | 本周 | 上周 | 变化 | 数据ID |")
                output.append("|------|------|------|------|--------|")
                current = overview.get('current', {})
                previous = overview.get('previous', {})
                changes = overview.get('changes', {})
                
                metrics = [
                    ('clicks', '点击数', 'GSC-OV01'),
                    ('impressions', '展示数', 'GSC-OV02'),
                    ('ctr', 'CTR(%)', 'GSC-OV03'),
                    ('position', '平均排名', 'GSC-OV04'),
                ]
                for key, label, data_id in metrics:
                    curr_val = current.get(key, 'N/A')
                    prev_val = previous.get(key, 'N/A')
                    change = changes.get(key, 'N/A')
                    output.append(f"| {label} | {curr_val} | {prev_val} | {change}% | {data_id} |")
        output.append("<!-- GSC-OVERVIEW-END -->\n")
        
        # Search Console Top Queries
        output.append("<!-- GSC-QUERIES-START -->")
        output.append("## Search Console 关键词\n")
        if 'top_queries' in gsc_data:
            queries = gsc_data['top_queries'].get('queries', [])
            if queries:
                output.append("| ID | 关键词 | 点击 | 展示 | CTR(%) | 平均排名 |")
                output.append("|-----|--------|------|------|--------|----------|")
                for i, query in enumerate(queries[:20], 1):
                    kw_id = f"KW{i:03d}"
                    keyword = query.get('query', 'N/A')[:40]
                    clicks = query.get('clicks', 'N/A')
                    impressions = query.get('impressions', 'N/A')
                    ctr = query.get('ctr', 'N/A')
                    position = query.get('position', 'N/A')
                    output.append(f"| {kw_id} | {keyword} | {clicks} | {impressions} | {ctr} | {position} |")
        output.append("<!-- GSC-QUERIES-END -->\n")
        
        # Search Console Top Pages
        output.append("<!-- GSC-PAGES-START -->")
        output.append("## Search Console 页面表现\n")
        if 'top_pages' in gsc_data:
            pages = gsc_data['top_pages'].get('pages', [])
            if pages:
                output.append("| ID | 页面URL | 点击 | 展示 | CTR(%) | 平均排名 |")
                output.append("|-----|---------|------|------|--------|----------|")
                for i, page in enumerate(pages[:15], 1):
                    page_id = f"GSCPG{i:03d}"
                    url = page.get('page', 'N/A')[:50]
                    clicks = page.get('clicks', 'N/A')
                    impressions = page.get('impressions', 'N/A')
                    ctr = page.get('ctr', 'N/A')
                    position = page.get('position', 'N/A')
                    output.append(f"| {page_id} | {url} | {clicks} | {impressions} | {ctr} | {position} |")
        output.append("<!-- GSC-PAGES-END -->\n")
        
        # GSC Device Breakdown
        output.append("<!-- GSC-DEVICES-START -->")
        output.append("## Search Console 设备分布\n")
        if 'devices' in gsc_data:
            devices = gsc_data['devices'].get('devices', [])
            if devices:
                output.append("| ID | 设备类型 | 点击 | 展示 | CTR(%) | 占比(%) |")
                output.append("|-----|----------|------|------|--------|--------|")
                for i, device in enumerate(devices, 1):
                    dev_id = f"GSCDEV{i:03d}"
                    category = device.get('device', 'N/A')
                    clicks = device.get('clicks', 'N/A')
                    impressions = device.get('impressions', 'N/A')
                    ctr = device.get('ctr', 'N/A')
                    pct = device.get('percentage', 'N/A')
                    output.append(f"| {dev_id} | {category} | {clicks} | {impressions} | {ctr} | {pct} |")
        output.append("<!-- GSC-DEVICES-END -->\n")
        
        # GSC Country Breakdown
        output.append("<!-- GSC-COUNTRIES-START -->")
        output.append("## Search Console 国家分布\n")
        if 'countries' in gsc_data:
            countries = gsc_data['countries'].get('countries', [])
            if countries:
                output.append("| ID | 国家 | 点击 | 展示 | CTR(%) | 占比(%) |")
                output.append("|-----|------|------|------|--------|--------|")
                for i, country in enumerate(countries[:10], 1):
                    country_id = f"GSCC{i:03d}"
                    name = country.get('country', 'N/A')
                    clicks = country.get('clicks', 'N/A')
                    impressions = country.get('impressions', 'N/A')
                    ctr = country.get('ctr', 'N/A')
                    pct = country.get('percentage', 'N/A')
                    output.append(f"| {country_id} | {name} | {clicks} | {impressions} | {ctr} | {pct} |")
        output.append("<!-- GSC-COUNTRIES-END -->\n")
        
        # CTR Opportunities
        output.append("<!-- GSC-OPPORTUNITIES-START -->")
        output.append("## CTR 优化机会（高展示低CTR）\n")
        if 'opportunities' in gsc_data:
            opps = gsc_data['opportunities'].get('opportunities', [])
            if opps:
                output.append("| ID | 关键词 | 点击 | 展示 | CTR(%) | 排名 | 优化潜力 |")
                output.append("|-----|--------|------|------|--------|------|----------|")
                for i, opp in enumerate(opps[:10], 1):
                    opp_id = f"OPP{i:03d}"
                    keyword = opp.get('query', 'N/A')[:40]
                    clicks = opp.get('clicks', 'N/A')
                    impressions = opp.get('impressions', 'N/A')
                    ctr = opp.get('ctr', 'N/A')
                    position = opp.get('position', 'N/A')
                    potential = opp.get('potentialClicks', 'N/A')
                    output.append(f"| {opp_id} | {keyword} | {clicks} | {impressions} | {ctr} | {position} | +{potential} |")
        output.append("<!-- GSC-OPPORTUNITIES-END -->\n")
        
        return "\n".join(output)
    
    def _generate_verification_footer(self, ga4_data: dict, gsc_data: dict) -> str:
        """Generate a verification footer with key data points for reference."""
        footer = "\n\n---\n\n## 数据来源验证\n\n"
        footer += "> 以下为原始数据摘要，供人工核对分析结论准确性\n\n"
        
        # GA4 Overview Comparison
        footer += "### GA4 核心指标\n\n"
        footer += "| 数据ID | 指标 | 当前周期 | 对比周期 | 变化 |\n"
        footer += "|--------|------|----------|----------|------|\n"
        
        if 'overview' in ga4_data:
            overview = ga4_data['overview']
            current = overview.get('current', {})
            previous = overview.get('previous', {})
            changes = overview.get('changes', {})
            
            metrics = [
                ('activeUsers', '活跃用户', 'GA4-OV01', False),
                ('sessions', '会话数', 'GA4-OV02', False),
                ('bounceRate', '跳出率(%)', 'GA4-OV03', True),
            ]
            for key, label, data_id, is_rate in metrics:
                curr = current.get(key, 'N/A')
                prev = previous.get(key, 'N/A')
                change = changes.get(key, 'N/A')
                # Convert bounce rate to percentage
                if is_rate and isinstance(curr, (int, float)):
                    curr = f"{round(curr * 100, 2)}%"
                if is_rate and isinstance(prev, (int, float)):
                    prev = f"{round(prev * 100, 2)}%"
                footer += f"| {data_id} | {label} | {curr} | {prev} | {change}% |\n"
        
        # GSC Overview Comparison
        footer += "\n### Search Console 核心指标\n\n"
        footer += "| 数据ID | 指标 | 当前周期 | 对比周期 | 变化 |\n"
        footer += "|--------|------|----------|----------|------|\n"
        
        if 'overview' in gsc_data:
            overview = gsc_data['overview']
            current = overview.get('current', {})
            previous = overview.get('previous', {})
            changes = overview.get('changes', {})
            
            metrics = [
                ('clicks', '点击数', 'GSC-OV01'),
                ('impressions', '展示数', 'GSC-OV02'),
                ('ctr', 'CTR(%)', 'GSC-OV03'),
                ('position', '平均排名', 'GSC-OV04'),
            ]
            for key, label, data_id in metrics:
                curr = current.get(key, 'N/A')
                prev = previous.get(key, 'N/A')
                change = changes.get(key, 'N/A')
                footer += f"| {data_id} | {label} | {curr} | {prev} | {change}% |\n"
        
        # Top 5 Keywords Quick Reference
        footer += "\n### TOP 5 关键词速查\n\n"
        if 'top_queries' in gsc_data:
            queries = gsc_data['top_queries'].get('queries', [])[:5]
            if queries:
                footer += "| ID | 关键词 | 点击 | 展示 |\n"
                footer += "|----|--------|------|------|\n"
                for i, q in enumerate(queries, 1):
                    footer += f"| KW{i:03d} | {q.get('query', 'N/A')[:30]} | {q.get('clicks', 'N/A')} | {q.get('impressions', 'N/A')} |\n"
        
        footer += f"\n*数据获取时间: {ga4_data.get('fetched_at', 'N/A')}*\n"
        
        return footer


def test_connection() -> bool:
    """Test Gemini API connection."""
    try:
        analyzer = GeminiAnalyzer()
        # Simple test
        response = analyzer.client.models.generate_content(
            model=analyzer.model_name,
            contents="Say 'OK' if you can hear me."
        )
        return 'OK' in response.text or 'ok' in response.text.lower()
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False


if __name__ == '__main__':
    # Test the analyzer with sample data
    test_ga4 = {
        'overview': {
            'current': {'activeUsers': 1000, 'sessions': 1500, 'bounceRate': 45.5},
            'previous': {'activeUsers': 900, 'sessions': 1400, 'bounceRate': 48.0}
        }
    }
    test_gsc = {
        'overview': {
            'current': {'clicks': 500, 'impressions': 10000, 'ctr': 5.0, 'position': 15.2},
            'previous': {'clicks': 450, 'impressions': 9500, 'ctr': 4.7, 'position': 16.0}
        }
    }
    
    analyzer = GeminiAnalyzer()
    result = analyzer.analyze(test_ga4, test_gsc)
    print(result)
