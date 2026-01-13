"""API路由定义"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..database.models import get_db, Video, TaskLog, Statistics
from ..database.crud import VideoCRUD, TaskLogCRUD, StatisticsCRUD
from ..core.scheduler import task_scheduler
from ..core.ai_analyzer import ai_analyzer
from ..core.reporter import video_reporter
from .schemas import (
    VideoResponse, VideoListResponse, StatisticsResponse,
    DailyStatisticsResponse, TaskResponse, TaskLogResponse,
    ManualAnalyzeRequest, ManualReportRequest, ApiResponse
)
from ..utils.logger import app_logger

# 创建路由器
router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def root():
    """根路径"""
    return ApiResponse(
        code=200,
        message="智能巡检举报下架机器人 API",
        data={"version": "1.0.0", "status": "running"}
    )


@router.get("/health", response_model=ApiResponse)
async def health_check():
    """健康检查"""
    return ApiResponse(
        code=200,
        message="healthy",
        data={"status": "ok", "timestamp": datetime.now().isoformat()}
    )


# ========== 视频管理接口 ==========

@router.get("/videos", response_model=VideoListResponse)
async def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    platform: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取视频列表"""
    query = db.query(Video)
    
    # 过滤条件
    if platform:
        query = query.filter(Video.platform == platform)
    if risk_level:
        query = query.filter(Video.risk_level == risk_level)
    if status:
        query = query.filter(Video.status == status)
    
    # 统计总数
    total = query.count()
    
    # 分页查询
    videos = query.order_by(Video.detected_time.desc()).offset(skip).limit(limit).all()
    
    return VideoListResponse(
        total=total,
        items=[VideoResponse.model_validate(v) for v in videos]
    )


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, db: Session = Depends(get_db)):
    """获取视频详情"""
    video = VideoCRUD.get_by_video_id(db, video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    return VideoResponse.model_validate(video)


@router.post("/videos/analyze", response_model=ApiResponse)
async def manual_analyze(request: ManualAnalyzeRequest, db: Session = Depends(get_db)):
    """手动分析视频"""
    video = VideoCRUD.get_by_video_id(db, request.video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    try:
        # 执行AI分析
        video_data = {
            'video_id': video.video_id,
            'title': video.title,
            'description': video.description,
            'author': video.author,
            'cover_url': video.cover_url
        }
        
        analysis_result = ai_analyzer.analyze_video(video_data)
        
        # 更新数据库
        VideoCRUD.update_analysis(db, video.video_id, analysis_result)
        
        return ApiResponse(
            code=200,
            message="分析完成",
            data=analysis_result
        )
        
    except Exception as e:
        app_logger.error(f"手动分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/report", response_model=ApiResponse)
async def manual_report(request: ManualReportRequest, db: Session = Depends(get_db)):
    """手动举报视频"""
    video = VideoCRUD.get_by_video_id(db, request.video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    try:
        # 执行举报
        video_data = {
            'video_id': video.video_id,
            'video_url': video.video_url,
            'platform': video.platform.value,
            'title': video.title
        }
        
        report_result = await video_reporter.report_video(video_data)
        
        # 更新数据库
        if report_result.get('success'):
            VideoCRUD.update_report(db, video.video_id, {
                'report_reason': request.report_reason or report_result.get('report_reason'),
                'report_result': 'success'
            })
        
        return ApiResponse(
            code=200 if report_result.get('success') else 500,
            message="举报成功" if report_result.get('success') else "举报失败",
            data=report_result
        )
        
    except Exception as e:
        app_logger.error(f"手动举报失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 统计分析接口 ==========

@router.get("/statistics/overview", response_model=StatisticsResponse)
async def get_statistics_overview(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """获取统计概览"""
    # 计算时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 获取统计数据
    stats = VideoCRUD.get_statistics(db, start_date, end_date)
    
    return StatisticsResponse(
        total_videos=stats['total'],
        high_risk_videos=stats['high_risk'],
        medium_risk_videos=stats['medium_risk'],
        low_risk_videos=stats['low_risk'],
        reported_videos=stats['reported'],
        takedown_videos=stats['takedown'],
        platforms=stats['platforms']
    )


@router.get("/statistics/daily", response_model=List[DailyStatisticsResponse])
async def get_daily_statistics(
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """获取每日统计数据"""
    # 查询最近N天的统计
    start_date = datetime.now() - timedelta(days=days)
    
    stats = db.query(Statistics).filter(
        Statistics.date >= start_date.strftime('%Y-%m-%d')
    ).order_by(Statistics.date.desc()).all()
    
    return [DailyStatisticsResponse.model_validate(s) for s in stats]


# ========== 任务管理接口 ==========

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks():
    """获取所有定时任务"""
    jobs = task_scheduler.get_jobs()
    return [TaskResponse(**job) for job in jobs]


@router.get("/tasks/logs", response_model=List[TaskLogResponse])
async def get_task_logs(
    task_name: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取任务执行日志"""
    query = db.query(TaskLog)
    
    if task_name:
        query = query.filter(TaskLog.task_name == task_name)
    
    logs = query.order_by(TaskLog.start_time.desc()).limit(limit).all()
    
    return [TaskLogResponse.model_validate(log) for log in logs]


@router.post("/tasks/{task_name}/run", response_model=ApiResponse)
async def run_task_manually(task_name: str):
    """手动触发任务执行"""
    try:
        task_func = task_scheduler._get_task_function(task_name)
        
        if not task_func:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 在后台执行任务
        import asyncio
        asyncio.create_task(task_func())
        
        return ApiResponse(
            code=200,
            message=f"任务 {task_name} 已开始执行",
            data={"task_name": task_name}
        )
        
    except Exception as e:
        app_logger.error(f"手动执行任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 系统管理接口 ==========

@router.get("/system/info", response_model=ApiResponse)
async def get_system_info(db: Session = Depends(get_db)):
    """获取系统信息"""
    # 统计总数
    total_videos = db.query(Video).count()
    pending_analysis = db.query(Video).filter(Video.status == 'detected').count()
    pending_report = db.query(Video).filter(Video.status == 'pending_report').count()
    reported = db.query(Video).filter(Video.status == 'reported').count()
    takedown = db.query(Video).filter(Video.is_takedown == True).count()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            'total_videos': total_videos,
            'pending_analysis': pending_analysis,
            'pending_report': pending_report,
            'reported': reported,
            'takedown': takedown,
            'tasks_count': len(task_scheduler.get_jobs())
        }
    )
