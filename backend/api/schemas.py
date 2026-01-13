"""API数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlatformEnum(str, Enum):
    """平台枚举"""
    DOUYIN = "douyin"
    KUAISHOU = "kuaishou"
    XIAOHONGSHU = "xiaohongshu"


class RiskLevelEnum(str, Enum):
    """风险等级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


class VideoStatusEnum(str, Enum):
    """视频状态枚举"""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    PENDING_REPORT = "pending_report"
    REPORTED = "reported"
    TAKEDOWN = "takedown"
    IGNORED = "ignored"


class VideoCreate(BaseModel):
    """创建视频请求"""
    video_id: str
    platform: PlatformEnum
    title: Optional[str] = None
    description: Optional[str] = None
    video_url: Optional[str] = None


class VideoResponse(BaseModel):
    """视频响应"""
    id: int
    video_id: str
    platform: str
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    video_url: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    status: str
    is_takedown: bool
    detected_time: datetime
    reported_time: Optional[datetime] = None
    takedown_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """视频列表响应"""
    total: int
    items: List[VideoResponse]


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    total_videos: int
    high_risk_videos: int
    medium_risk_videos: int
    low_risk_videos: int
    reported_videos: int
    takedown_videos: int
    platforms: Dict[str, int]


class DailyStatisticsResponse(BaseModel):
    """每日统计响应"""
    date: str
    videos_detected: int
    videos_high_risk: int
    videos_medium_risk: int
    videos_low_risk: int
    videos_reported: int
    videos_takedown: int
    avg_takedown_hours: Optional[float] = None
    platform_stats: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    name: str
    next_run_time: Optional[str] = None
    trigger: str


class TaskLogResponse(BaseModel):
    """任务日志响应"""
    id: int
    task_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool
    items_processed: int
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ManualAnalyzeRequest(BaseModel):
    """手动分析请求"""
    video_id: str


class ManualReportRequest(BaseModel):
    """手动举报请求"""
    video_id: str
    report_reason: Optional[str] = None


class ApiResponse(BaseModel):
    """通用API响应"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None
