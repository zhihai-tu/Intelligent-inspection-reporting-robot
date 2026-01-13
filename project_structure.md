# 智能巡检举报下架机器人 - 项目结构

## 目录结构
```
intelligent-patrol-robot/
├── backend/                    # 后端服务
│   ├── api/                   # API接口
│   │   ├── __init__.py
│   │   ├── routes.py          # 路由定义
│   │   └── schemas.py         # 数据模型
│   ├── core/                  # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── crawler.py         # 视频爬取模块
│   │   ├── ai_analyzer.py     # AI内容分析
│   │   ├── reporter.py        # 自动举报模块
│   │   └── scheduler.py       # 定时任务调度
│   ├── database/              # 数据库相关
│   │   ├── __init__.py
│   │   ├── models.py          # 数据模型
│   │   └── crud.py            # 数据库操作
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py          # 日志工具
│   │   └── config.py          # 配置管理
│   ├── main.py                # FastAPI应用入口
│   └── requirements.txt       # Python依赖
├── frontend/                  # 前端Dashboard
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面视图
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── data/                      # 数据存储
│   ├── database.db            # SQLite数据库
│   └── logs/                  # 日志文件
├── config/                    # 配置文件
│   └── config.yaml
├── tests/                     # 测试文件
└── README.md
```

## 核心功能模块

### 1. 视频爬取模块 (crawler.py)
- 抖音平台关键词搜索
- 视频元数据采集
- 评论区数据抓取
- 反爬虫策略处理

### 2. AI内容分析模块 (ai_analyzer.py)
- 视频内容理解（多模态分析）
- OCR文字提取
- 黑灰产特征识别
- 风险等级评估

### 3. 自动举报模块 (reporter.py)
- 模拟用户举报操作
- 多平台适配
- 举报结果追踪
- 下架状态监测

### 4. 调度系统 (scheduler.py)
- 7x24小时定时任务
- 任务优先级管理
- 失败重试机制
- 性能监控

### 5. 数据统计报表
- 视频名称、渠道、举报时间
- 下架时间、处理状态
- 统计图表展示
- 导出Excel报表
