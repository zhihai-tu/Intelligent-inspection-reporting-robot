"""数据库模型定义"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    Enum, Boolean, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class PlatformEnum(str, PyEnum):
    """平台枚举"""
    DOUYIN = "douyin"
    KUAISHOU = "kuaishou"
    XIAOHONGSHU = "xiaohongshu"


class RiskLevelEnum(str, PyEnum):
    """风险等级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


class VideoStatusEnum(str, PyEnum):
    """视频状态枚举"""
    DETECTED = "detected"        # 已检测
    ANALYZING = "analyzing"      # 分析中
    ANALYZED = "analyzed"        # 已分析
    PENDING_REPORT = "pending_report"  # 待举报
    REPORTED = "reported"        # 已举报
    TAKEDOWN = "takedown"        # 已下架
    IGNORED = "ignored"          # 已忽略


class Video(Base):
    """视频信息表"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(100), unique=True, index=True, nullable=False, comment="视频ID")
    platform = Column(Enum(PlatformEnum), nullable=False, comment="平台")
    
    # 视频基本信息
    title = Column(String(500), comment="视频标题")
    description = Column(Text, comment="视频描述")
    author = Column(String(200), comment="作者名称")
    author_id = Column(String(100), comment="作者ID")
    channel = Column(String(200), comment="频道/分类")
    
    # 视频链接和资源
    video_url = Column(String(500), comment="视频链接")
    cover_url = Column(String(500), comment="封面图片链接")
    
    # 视频统计数据
    view_count = Column(Integer, default=0, comment="播放量")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    share_count = Column(Integer, default=0, comment="分享数")
    
    # 检测和分析
    detected_time = Column(DateTime, default=datetime.now, comment="检测时间")
    keywords_matched = Column(JSON, comment="匹配的关键词")
    
    # AI分析结果
    risk_level = Column(Enum(RiskLevelEnum), comment="风险等级")
    risk_score = Column(Float, comment="风险评分 0-1")
    ai_analysis = Column(JSON, comment="AI分析结果")
    ocr_text = Column(Text, comment="OCR提取的文字")
    analyzed_time = Column(DateTime, comment="分析时间")
    
    # 举报信息
    status = Column(Enum(VideoStatusEnum), default=VideoStatusEnum.DETECTED, comment="处理状态")
    reported_time = Column(DateTime, comment="举报时间")
    report_reason = Column(String(500), comment="举报原因")
    report_result = Column(String(200), comment="举报结果")
    
    # 下架信息
    is_takedown = Column(Boolean, default=False, comment="是否已下架")
    takedown_time = Column(DateTime, comment="下架时间")
    check_count = Column(Integer, default=0, comment="检查次数")
    last_check_time = Column(DateTime, comment="最后检查时间")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    extra_data = Column(JSON, comment="额外数据")


class ReportLog(Base):
    """举报日志表"""
    __tablename__ = "report_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(100), index=True, nullable=False, comment="视频ID")
    platform = Column(Enum(PlatformEnum), nullable=False, comment="平台")
    
    # 举报信息
    report_time = Column(DateTime, default=datetime.now, comment="举报时间")
    report_reason = Column(String(500), comment="举报原因")
    report_type = Column(String(100), comment="举报类型")
    
    # 处理结果
    success = Column(Boolean, default=False, comment="是否成功")
    error_message = Column(Text, comment="错误信息")
    response_data = Column(JSON, comment="响应数据")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class TaskLog(Base):
    """任务执行日志表"""
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), index=True, nullable=False, comment="任务名称")
    
    # 执行信息
    start_time = Column(DateTime, default=datetime.now, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(Float, comment="执行时长（秒）")
    
    # 执行结果
    success = Column(Boolean, default=False, comment="是否成功")
    items_processed = Column(Integer, default=0, comment="处理项目数")
    error_message = Column(Text, comment="错误信息")
    result_data = Column(JSON, comment="结果数据")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class Statistics(Base):
    """统计数据表"""
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), unique=True, index=True, nullable=False, comment="日期 YYYY-MM-DD")
    
    # 检测统计
    videos_detected = Column(Integer, default=0, comment="检测视频数")
    videos_high_risk = Column(Integer, default=0, comment="高风险视频数")
    videos_medium_risk = Column(Integer, default=0, comment="中风险视频数")
    videos_low_risk = Column(Integer, default=0, comment="低风险视频数")
    
    # 举报统计
    videos_reported = Column(Integer, default=0, comment="举报视频数")
    reports_success = Column(Integer, default=0, comment="举报成功数")
    reports_failed = Column(Integer, default=0, comment="举报失败数")
    
    # 下架统计
    videos_takedown = Column(Integer, default=0, comment="下架视频数")
    avg_takedown_hours = Column(Float, comment="平均下架时长（小时）")
    
    # 平台统计
    platform_stats = Column(JSON, comment="各平台统计")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


# 数据库引擎和会话
from ..utils.config import config

engine = create_engine(
    config.database.get('url', 'sqlite:///./data/database.db'),
    echo=config.database.get('echo', False),
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
