# 📊 Website Data Analyst

AI驱动的自动化网站运营分析系统。每周自动从 Google Analytics 4 和 Search Console 获取数据，通过 Gemini AI 生成专业分析报告，并发布到 Notion。

## ✨ 功能特点

- 🔄 **全自动化**：通过 GitHub Actions 每周自动运行
- 📈 **双数据源**：同时分析 GA4 流量数据和 Search Console SEO 数据
- 🤖 **AI 分析**：使用 Gemini AI 生成专业、可落地的分析报告
- 📝 **Notion 集成**：报告自动发布到 Notion，方便团队查阅
- ✅ **数据准确**：所有分析基于真实 API 数据，报告包含数据来源验证

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo>
cd 05_website_data_analyst
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下配置：

| 变量名 | 说明 |
|--------|------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Service Account JSON 路径 |
| `GA4_PROPERTY_ID` | GA4 Property ID |
| `GSC_SITE_URL` | Search Console 网站 URL |
| `GEMINI_API_KEY` | Gemini API 密钥 |
| `NOTION_TOKEN` | Notion Integration Token |
| `NOTION_PARENT_PAGE_ID` | Notion 父页面 ID |

### 5. 配置 API 权限

详细步骤请参考下方 [API 配置指南](#api-配置指南)。

### 6. 测试运行

```bash
# 测试 API 连接
python src/main.py --test-connections

# 干运行（不发布到 Notion）
python src/main.py --dry-run

# 完整运行
python src/main.py
```

## 📖 API 配置指南

### Google Cloud 配置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用以下 API：
   - Google Analytics Data API
   - Google Search Console API
4. 创建 Service Account 并下载 JSON 密钥
5. 将 JSON 文件保存到 `credentials/google_service_account.json`

### GA4 权限配置

1. 进入 [Google Analytics](https://analytics.google.com/)
2. Admin > Property > Property Access Management
3. 添加 Service Account 邮箱，授予 Viewer 权限
4. 记录 Property ID

### Search Console 权限配置

1. 进入 [Google Search Console](https://search.google.com/search-console)
2. Settings > Users and permissions
3. 添加 Service Account 邮箱

### Gemini API 配置

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建 API Key

### Notion 配置

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 创建新 Integration
3. 在目标页面添加 Integration 连接
4. 复制页面 ID（URL 中的 32 位字符串）

## 🔧 命令行选项

```bash
python src/main.py [OPTIONS]

Options:
  --test-connections  测试所有 API 连接
  --dry-run           获取数据并生成分析，但不发布
  --save-data         保存原始数据到 JSON 文件
  --check-config      检查配置状态
```

## ⚙️ GitHub Actions 自动化

项目已配置 GitHub Actions，每周一早上 9:00（北京时间）自动运行。

### 配置 Secrets

在 GitHub 仓库 Settings > Secrets and variables > Actions 中添加：

- `GOOGLE_SERVICE_ACCOUNT_JSON`：Service Account JSON 内容
- `GA4_PROPERTY_ID`
- `GSC_SITE_URL`
- `GEMINI_API_KEY`
- `NOTION_TOKEN`
- `NOTION_PARENT_PAGE_ID`

### 手动触发

在 Actions 页面可以手动触发 workflow。

## 📁 项目结构

```
05_website_data_analyst/
├── .github/workflows/     # GitHub Actions
├── credentials/           # API 凭证（不提交）
├── src/
│   ├── config.py         # 配置管理
│   ├── main.py           # 主入口
│   ├── fetchers/         # 数据获取
│   │   ├── ga4_fetcher.py
│   │   └── gsc_fetcher.py
│   ├── analyzers/        # AI 分析
│   │   └── gemini_analyzer.py
│   └── publishers/       # 报告发布
│       └── notion_publisher.py
├── templates/            # 提示模板
├── .env.example          # 环境变量模板
└── requirements.txt      # 依赖
```

## 📊 报告内容

每周报告包含：

1. **执行摘要**：关键指标概览和变化
2. **流量分析**：用户、会话、来源、设备
3. **SEO 分析**：关键词、排名、CTR
4. **页面分析**：热门页面、问题页面
5. **问题诊断**：自动识别的问题
6. **优化建议**：具体可执行的行动项
7. **数据验证**：原始数据引用

## 🔒 安全说明

- 所有凭证通过环境变量或 GitHub Secrets 管理
- `credentials/` 目录已在 `.gitignore` 中
- 敏感文件不会提交到仓库

## 📝 License

MIT
