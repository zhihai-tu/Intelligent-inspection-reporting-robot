# 智能巡检举报下架机器人 - 使用指南

## 🎯 快速开始（5分钟）

### 第一步：安装依赖

```bash
# 1. 进入项目目录
cd /home/user/webapp

# 2. 安装Python依赖
pip install -r backend/requirements.txt

# 3. 安装Playwright浏览器（用于爬虫）
playwright install chromium
```

### 第二步：配置环境变量

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑.env文件
nano .env

# 3. 填入你的OpenAI API Key
OPENAI_API_KEY=sk-your-key-here
```

### 第三步：运行测试

```bash
# 运行系统测试，验证各模块功能
python tests/test_system.py
```

### 第四步：启动服务

```bash
# 使用启动脚本
./start.sh

# 或手动启动
python -m backend.main
```

### 第五步：访问系统

- **API文档**: http://localhost:8000/docs
- **后端API**: http://localhost:8000/api/v1
- **前端Dashboard**: http://localhost:3000 (需要单独启动)

---

## 📖 详细使用说明

### 1. 配置系统参数

编辑 `config/config.yaml` 文件：

#### 1.1 配置监测关键词

```yaml
crawler:
  douyin:
    search_keywords:
      - "贷款"
      - "刷单兼职"
      - "免费领取"
      - "加微信"
      # 添加更多关键词...
```

#### 1.2 配置黑灰产关键词库

```yaml
ai:
  blacklist_keywords:
    - "加微信"
    - "私聊"
    - "导流"
    - "贷款"
    - "刷单"
    # 添加更多关键词...
```

#### 1.3 调整定时任务

```yaml
scheduler:
  tasks:
    - name: "video_crawl_task"
      cron: "0 */2 * * *"  # 每2小时爬取一次
      enabled: true
    
    - name: "ai_analysis_task"
      cron: "*/30 * * * *"  # 每30分钟分析一次
      enabled: true
```

### 2. API使用示例

#### 2.1 获取视频列表

```bash
curl -X GET "http://localhost:8000/api/v1/videos?limit=10&risk_level=high"
```

#### 2.2 手动分析视频

```bash
curl -X POST "http://localhost:8000/api/v1/videos/analyze" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "your_video_id"}'
```

#### 2.3 手动举报视频

```bash
curl -X POST "http://localhost:8000/api/v1/videos/report" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "your_video_id", "report_reason": "涉嫌诈骗引流"}'
```

#### 2.4 获取统计数据

```bash
curl -X GET "http://localhost:8000/api/v1/statistics/overview?days=7"
```

#### 2.5 查看任务列表

```bash
curl -X GET "http://localhost:8000/api/v1/tasks"
```

#### 2.6 手动触发任务

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/video_crawl_task/run"
```

### 3. 启动前端Dashboard（可选）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 4. 查看日志

```bash
# 实时查看日志
tail -f data/logs/app.log

# 查看最近100行
tail -n 100 data/logs/app.log

# 搜索错误日志
grep "ERROR" data/logs/app.log
```

### 5. 数据库管理

```bash
# 使用SQLite命令行工具
sqlite3 data/database.db

# 查看视频表
sqlite> SELECT * FROM videos LIMIT 10;

# 查看统计数据
sqlite> SELECT * FROM statistics ORDER BY date DESC;

# 退出
sqlite> .quit
```

---

## 🔧 高级配置

### 1. 使用其他AI模型

#### 1.1 使用Claude (Anthropic)

```yaml
ai:
  provider: "anthropic"
  model: "claude-3-sonnet-20240229"
  api_key: "${ANTHROPIC_API_KEY}"
```

#### 1.2 使用国内兼容API

```yaml
ai:
  provider: "openai"
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
  base_url: "https://your-api-endpoint.com/v1"  # 自定义端点
```

### 2. 更换数据库

#### 2.1 使用PostgreSQL

```yaml
database:
  url: "postgresql://user:password@localhost:5432/patrol_robot"
```

#### 2.2 使用MySQL

```yaml
database:
  url: "mysql+pymysql://user:password@localhost:3306/patrol_robot"
```

### 3. 配置多平台

```yaml
crawler:
  # 抖音
  douyin:
    enabled: true
    search_keywords: ["贷款", "刷单"]
  
  # 快手
  kuaishou:
    enabled: true
    search_keywords: ["贷款", "兼职"]
  
  # 小红书
  xiaohongshu:
    enabled: true
    search_keywords: ["免费领取"]
```

---

## 🚀 生产环境部署

### 1. 使用Supervisor管理进程

```bash
# 安装supervisor
pip install supervisor

# 创建配置文件
cat > supervisord.conf << 'EOF'
[supervisord]
nodaemon=false

[program:patrol-robot]
command=python -m backend.main
directory=/home/user/webapp
autostart=true
autorestart=true
stdout_logfile=/home/user/webapp/data/logs/supervisor.log
EOF

# 启动
supervisord -c supervisord.conf
```

### 2. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;  # 前端
    }
}
```

### 3. 使用Docker部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

EXPOSE 8000

CMD ["python", "-m", "backend.main"]
```

---

## 🐛 常见问题

### Q1: API Key未配置

**问题**: 启动时提示 "未配置AI API密钥"

**解决**: 
1. 确保已创建 `.env` 文件
2. 填入有效的 `OPENAI_API_KEY`
3. 重启服务

### Q2: 爬虫无法获取数据

**问题**: 爬虫任务运行但没有数据

**解决**: 
- 当前版本使用模拟数据
- 实际使用需要实现真实爬虫逻辑
- 或使用平台官方API

### Q3: 数据库连接错误

**问题**: 启动时数据库初始化失败

**解决**:
```bash
# 确保data目录存在
mkdir -p data/logs

# 删除旧数据库重新初始化
rm data/database.db
python -m backend.main
```

### Q4: 前端无法连接后端

**问题**: 前端API请求失败

**解决**:
1. 确保后端已启动（http://localhost:8000）
2. 检查 `vite.config.js` 中的代理配置
3. 查看浏览器控制台错误信息

### Q5: Playwright浏览器安装失败

**问题**: `playwright install` 失败

**解决**:
```bash
# 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/

# 重新安装
playwright install chromium
```

---

## 📊 性能优化建议

### 1. 数据库优化
- 定期清理过期数据（保留近3个月）
- 为常用查询字段添加索引
- 考虑升级到PostgreSQL

### 2. 爬虫优化
- 使用代理IP池避免封禁
- 合理设置爬取频率
- 实现增量爬取

### 3. AI分析优化
- 批量调用API减少请求次数
- 缓存分析结果
- 使用更快的模型（如gpt-3.5-turbo）

### 4. 任务调度优化
- 根据业务需求调整任务频率
- 错峰执行不同任务
- 实现任务队列

---

## 🔒 安全建议

1. **API Key管理**: 使用环境变量，不要硬编码
2. **数据库安全**: 生产环境使用PostgreSQL并设置强密码
3. **访问控制**: 为API添加身份验证
4. **日志脱敏**: 敏感信息不记录到日志
5. **HTTPS**: 生产环境使用HTTPS协议

---

## 📞 技术支持

- 查看日志: `data/logs/app.log`
- 提交Issue: GitHub Issues
- 邮件联系: support@example.com

---

**祝使用愉快！** 🎉
