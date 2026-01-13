"""FastAPI应用主入口"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .utils.config import config
from .utils.logger import app_logger
from .database.models import init_db
from .core.scheduler import task_scheduler
from .api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    app_logger.info("=" * 50)
    app_logger.info("智能巡检举报下架机器人启动中...")
    app_logger.info("=" * 50)
    
    # 初始化数据库
    try:
        init_db()
        app_logger.info("✓ 数据库初始化完成")
    except Exception as e:
        app_logger.error(f"✗ 数据库初始化失败: {str(e)}")
    
    # 启动任务调度器
    try:
        task_scheduler.start()
        app_logger.info("✓ 任务调度器启动成功")
    except Exception as e:
        app_logger.error(f"✗ 任务调度器启动失败: {str(e)}")
    
    app_logger.info("=" * 50)
    app_logger.info("系统启动完成！")
    app_logger.info(f"API地址: http://{config.app['host']}:{config.app['port']}")
    app_logger.info(f"API文档: http://{config.app['host']}:{config.app['port']}/docs")
    app_logger.info("=" * 50)
    
    yield
    
    # 关闭时执行
    app_logger.info("系统正在关闭...")
    
    # 关闭任务调度器
    try:
        task_scheduler.shutdown()
        app_logger.info("✓ 任务调度器已关闭")
    except Exception as e:
        app_logger.error(f"✗ 任务调度器关闭失败: {str(e)}")
    
    app_logger.info("系统已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=config.app.get('name', '智能巡检举报机器人'),
    version=config.app.get('version', '1.0.0'),
    description="""
    ## 智能巡检举报下架机器人 API
    
    ### 功能特性：
    - 🔍 **自动巡检**: 7x24小时自动监测抖音、快手、小红书等平台违规视频
    - 🤖 **AI分析**: 基于大模型的智能内容审核，识别黑灰产引流内容
    - 📢 **自动举报**: 自动化举报流程，提升处置效率
    - 📊 **数据统计**: 全面的数据统计和可视化报表
    - 🎯 **精准识别**: 多维度风险评估，减少误报和漏报
    
    ### 核心模块：
    - **视频管理**: 视频检测、分析、举报全流程管理
    - **统计分析**: 实时统计数据和历史趋势分析
    - **任务调度**: 灵活的定时任务配置和执行
    - **系统监控**: 系统运行状态和性能监控
    """,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["API"])


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": config.app.get('name'),
        "version": config.app.get('version'),
        "status": "running",
        "docs_url": "/docs",
        "api_prefix": "/api/v1"
    }


def main():
    """主函数"""
    # 获取配置
    host = config.app.get('host', '0.0.0.0')
    port = config.app.get('port', 8000)
    debug = config.app.get('debug', False)
    
    # 启动服务
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
