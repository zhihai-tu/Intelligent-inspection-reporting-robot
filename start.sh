#!/bin/bash

echo "=================================="
echo "智能巡检举报下架机器人 - 快速启动"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo "✓ Python3已安装"

# 检查是否已安装依赖
if [ ! -d "backend/__pycache__" ]; then
    echo "📦 正在安装Python依赖..."
    pip install -r backend/requirements.txt
    
    echo "📦 正在安装Playwright浏览器..."
    playwright install chromium
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件，正在创建..."
    cp .env.example .env
    echo "📝 请编辑.env文件，填入你的OpenAI API Key"
    echo "   执行: nano .env"
    exit 0
fi

# 确保数据目录存在
mkdir -p data/logs

echo "=================================="
echo "🚀 启动后端服务..."
echo "=================================="

# 启动FastAPI服务
cd /home/user/webapp
export PYTHONPATH=/home/user/webapp:$PYTHONPATH
python3 -m backend.main

echo "=================================="
echo "✅ 服务已启动"
echo "API文档: http://localhost:8000/docs"
echo "=================================="
