# 智能巡检举报下架机器人

## 📋 项目简介

针对抖音、快手、小红书等平台上的黑灰产引流视频，构建**7x24小时自动化监测与举报下架机制**，并形成统计报表。替代人工操作，提升处置效率与覆盖范围，减少人力投入与漏报风险。

## ✨ 核心功能

### 1. 🔍 智能监测
- **多平台支持**: 支持抖音、快手、小红书等主流短视频平台
- **关键词搜索**: 基于黑灰产关键词自动搜索可疑视频
- **实时采集**: 自动采集视频元数据、评论等信息

### 2. 🤖 AI内容分析
- **多模态分析**: 结合标题、描述、封面图进行综合分析
- **关键词匹配**: 基于黑灰产特征词库快速过滤
- **规则引擎**: 多维度规则判断（联系方式、诱导性词汇等）
- **AI深度分析**: 调用大模型进行智能内容审核
- **风险评分**: 0-1分值评估，自动分级（高/中/低/安全）

### 3. 📢 自动举报
- **模拟举报**: 模拟真实用户举报操作
- **批量处理**: 支持批量举报，提升效率
- **速率控制**: 智能控制举报频率，避免被识别为机器人
- **结果追踪**: 自动记录举报结果

### 4. 🎯 下架监控
- **定时检查**: 定期检查被举报视频的下架状态
- **状态更新**: 实时更新视频在线/下架状态
- **时效统计**: 计算从举报到下架的处理时长

### 5. 📊 数据统计与报表
- **多维度统计**: 
  - 视频名称、渠道、举报时间、下架时间
  - 风险等级分布、处理成功率
  - 平台数据对比、时间趋势分析
- **可视化展示**: Dashboard实时展示关键指标
- **报表导出**: 支持Excel、CSV等格式导出

### 6. ⏰ 7x24小时调度
- **定时任务**: 灵活配置各类定时任务
  - 视频爬取任务（每2小时）
  - AI分析任务（每30分钟）
  - 自动举报任务（每15分钟）
  - 状态检查任务（每小时）
  - 日报生成任务（每天9点）
- **失败重试**: 自动重试失败任务
- **性能监控**: 记录任务执行日志

## 🏗️ 技术架构

### 后端技术栈
- **Web框架**: FastAPI（高性能异步框架）
- **数据库**: SQLite（可升级到PostgreSQL/MySQL）
- **ORM**: SQLAlchemy
- **任务调度**: APScheduler
- **爬虫**: Playwright（模拟浏览器）
- **AI模型**: OpenAI API（支持兼容接口）
- **日志**: Loguru

### 前端技术栈（可选）
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **图表**: ECharts
- **HTTP客户端**: Axios

## 📦 项目结构

```
intelligent-patrol-robot/
├── backend/                    # 后端服务
│   ├── api/                   # API接口
│   │   ├── routes.py          # 路由定义
│   │   └── schemas.py         # 数据模型
│   ├── core/                  # 核心业务逻辑
│   │   ├── crawler.py         # 视频爬取模块
│   │   ├── ai_analyzer.py     # AI内容分析
│   │   ├── reporter.py        # 自动举报模块
│   │   └── scheduler.py       # 定时任务调度
│   ├── database/              # 数据库相关
│   │   ├── models.py          # 数据模型
│   │   └── crud.py            # 数据库操作
│   ├── utils/                 # 工具函数
│   │   ├── logger.py          # 日志工具
│   │   └── config.py          # 配置管理
│   ├── main.py                # FastAPI应用入口
│   └── requirements.txt       # Python依赖
├── frontend/                  # 前端Dashboard（可选）
├── data/                      # 数据存储
│   ├── database.db            # SQLite数据库
│   └── logs/                  # 日志文件
├── config/                    # 配置文件
│   └── config.yaml            # 主配置文件
└── README.md
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- pip 或 conda

### 2. 安装依赖

```bash
# 进入项目目录
cd /home/user/webapp

# 安装Python依赖
pip install -r backend/requirements.txt

# 安装Playwright浏览器（用于爬虫）
playwright install chromium
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的配置
# 主要配置OpenAI API Key用于AI内容分析
vim .env
```

### 4. 配置系统参数

编辑 `config/config.yaml` 文件，根据需要调整：
- AI模型配置
- 爬虫关键词列表
- 举报频率限制
- 定时任务时间表

### 5. 启动服务

```bash
# 方式1: 直接运行
cd /home/user/webapp
python -m backend.main

# 方式2: 使用uvicorn
cd /home/user/webapp
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 访问API文档
# http://localhost:8000/docs
```

## 📖 API文档

启动服务后，访问以下地址查看完整API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要API接口

#### 视频管理
- `GET /api/v1/videos` - 获取视频列表
- `GET /api/v1/videos/{video_id}` - 获取视频详情
- `POST /api/v1/videos/analyze` - 手动分析视频
- `POST /api/v1/videos/report` - 手动举报视频

#### 统计分析
- `GET /api/v1/statistics/overview` - 获取统计概览
- `GET /api/v1/statistics/daily` - 获取每日统计

#### 任务管理
- `GET /api/v1/tasks` - 获取所有定时任务
- `GET /api/v1/tasks/logs` - 获取任务执行日志
- `POST /api/v1/tasks/{task_name}/run` - 手动触发任务

#### 系统监控
- `GET /api/v1/system/info` - 获取系统信息
- `GET /api/v1/health` - 健康检查

## 🔧 配置说明

### AI模型配置

在 `config/config.yaml` 中配置AI服务：

```yaml
ai:
  provider: "openai"  # 或 anthropic
  model: "gpt-4-vision-preview"  # 或其他模型
  api_key: "${OPENAI_API_KEY}"  # 从环境变量读取
  base_url: ""  # 自定义API端点（可选）
```

### 黑灰产关键词配置

```yaml
ai:
  blacklist_keywords:
    - "加微信"
    - "私聊"
    - "导流"
    - "贷款"
    - "刷单"
    # ... 更多关键词
```

### 爬虫配置

```yaml
crawler:
  douyin:
    enabled: true
    search_keywords:
      - "贷款"
      - "刷单兼职"
      # ... 更多搜索词
    max_videos_per_keyword: 50
    crawl_interval: 3600  # 秒
```

### 定时任务配置

```yaml
scheduler:
  tasks:
    - name: "video_crawl_task"
      cron: "0 */2 * * *"  # 每2小时执行
      enabled: true
```

## 📊 数据表结构

### videos - 视频信息表
- 视频基本信息（ID、标题、描述、作者等）
- AI分析结果（风险等级、评分、分析详情）
- 举报信息（举报时间、原因、结果）
- 下架状态（是否下架、下架时间、检查次数）

### report_logs - 举报日志表
- 记录每次举报操作的详细信息

### task_logs - 任务执行日志表
- 记录定时任务的执行情况

### statistics - 统计数据表
- 每日汇总统计数据

## 🎯 使用场景

### 场景1: 金融风险监控
监测和举报涉及非法贷款、P2P、高利贷等金融诈骗内容。

### 场景2: 刷单诈骗打击
识别和下架刷单兼职、薅羊毛、返现等诈骗引流视频。

### 场景3: 品牌保护
监控品牌相关的假冒伪劣、侵权引流内容。

### 场景4: 内容合规
确保平台内容符合监管要求，及时清理违规内容。

## ⚠️ 重要说明

### 1. 爬虫合规性
- 本项目中的爬虫代码仅为**演示目的**
- 实际使用时需要：
  - 遵守各平台的robots.txt和服务条款
  - 使用官方开放API（如有）
  - 或使用第三方合法数据服务
  - 注意频率控制，避免对平台造成压力

### 2. 举报功能说明
- 举报模块提供的是**模拟实现**
- 真实场景需要：
  - 获取合法的平台举报权限
  - 实现真实的举报流程
  - 遵守平台举报规则

### 3. AI模型使用
- 需要配置有效的OpenAI API Key
- 或使用兼容OpenAI接口的第三方服务
- 注意控制API调用成本

### 4. 数据隐私
- 妥善保管采集的数据
- 遵守数据保护相关法律法规
- 定期清理过期数据

## 🔄 开发路线图

- [x] 基础框架搭建
- [x] AI内容分析模块
- [x] 视频爬取模块（演示版）
- [x] 自动举报模块（演示版）
- [x] 定时任务调度系统
- [x] RESTful API接口
- [ ] 前端Dashboard开发
- [ ] 真实平台爬虫实现
- [ ] 真实举报流程实现
- [ ] 更多平台支持（快手、小红书）
- [ ] 数据导出和报表生成
- [ ] 微信/邮件通知
- [ ] Docker容器化部署
- [ ] 分布式爬取支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👥 联系方式

如有问题或建议，请提交Issue或联系开发团队。

---

**免责声明**: 本项目仅供学习和研究使用，使用者需自行承担使用本项目可能产生的法律责任。请确保在使用过程中遵守相关法律法规和平台规则。
