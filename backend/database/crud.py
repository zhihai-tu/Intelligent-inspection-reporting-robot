"""数据库CRUD操作"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from .models import (
    Video, ReportLog, TaskLog, Statistics,
    VideoStatusEnum, RiskLevelEnum, PlatformEnum
)


class VideoCRUD:
    """视频数据操作"""
    
    @staticmethod
    def create(db: Session, video_data: Dict[str, Any]) -> Video:
        """创建视频记录"""
        video = Video(**video_data)
        db.add(video)
        db.commit()
        db.refresh(video)
        return video
    
    @staticmethod
    def get_by_video_id(db: Session, video_id: str) -> Optional[Video]:
        """根据视频ID获取记录"""
        return db.query(Video).filter(Video.video_id == video_id).first()
    
    @staticmethod
    def get_pending_analysis(db: Session, limit: int = 100) -> List[Video]:
        """获取待分析的视频"""
        return db.query(Video).filter(
            Video.status.in_([VideoStatusEnum.DETECTED])
        ).limit(limit).all()
    
    @staticmethod
    def get_pending_report(db: Session, limit: int = 100) -> List[Video]:
        """获取待举报的视频"""
        return db.query(Video).filter(
            and_(
                Video.status == VideoStatusEnum.PENDING_REPORT,
                Video.risk_level == RiskLevelEnum.HIGH
            )
        ).limit(limit).all()
    
    @staticmethod
    def get_need_check_takedown(db: Session, limit: int = 100) -> List[Video]:
        """获取需要检查下架状态的视频"""
        # 已举报但未下架，且检查次数未超限的视频
        return db.query(Video).filter(
            and_(
                Video.status == VideoStatusEnum.REPORTED,
                Video.is_takedown == False,
                Video.check_count < 48  # 最多检查48次
            )
        ).limit(limit).all()
    
    @staticmethod
    def update_status(db: Session, video_id: str, status: VideoStatusEnum) -> Optional[Video]:
        """更新视频状态"""
        video = VideoCRUD.get_by_video_id(db, video_id)
        if video:
            video.status = status
            video.updated_at = datetime.now()
            db.commit()
            db.refresh(video)
        return video
    
    @staticmethod
    def update_analysis(db: Session, video_id: str, analysis_data: Dict[str, Any]) -> Optional[Video]:
        """更新分析结果"""
        video = VideoCRUD.get_by_video_id(db, video_id)
        if video:
            video.risk_level = analysis_data.get('risk_level')
            video.risk_score = analysis_data.get('risk_score')
            video.ai_analysis = analysis_data.get('ai_analysis')
            video.ocr_text = analysis_data.get('ocr_text')
            video.analyzed_time = datetime.now()
            
            # 根据风险等级更新状态
            if video.risk_level == RiskLevelEnum.HIGH:
                video.status = VideoStatusEnum.PENDING_REPORT
            else:
                video.status = VideoStatusEnum.ANALYZED
            
            video.updated_at = datetime.now()
            db.commit()
            db.refresh(video)
        return video
    
    @staticmethod
    def update_report(db: Session, video_id: str, report_data: Dict[str, Any]) -> Optional[Video]:
        """更新举报信息"""
        video = VideoCRUD.get_by_video_id(db, video_id)
        if video:
            video.reported_time = datetime.now()
            video.report_reason = report_data.get('report_reason')
            video.report_result = report_data.get('report_result')
            video.status = VideoStatusEnum.REPORTED
            video.updated_at = datetime.now()
            db.commit()
            db.refresh(video)
        return video
    
    @staticmethod
    def update_takedown(db: Session, video_id: str, is_takedown: bool) -> Optional[Video]:
        """更新下架状态"""
        video = VideoCRUD.get_by_video_id(db, video_id)
        if video:
            video.check_count += 1
            video.last_check_time = datetime.now()
            
            if is_takedown and not video.is_takedown:
                video.is_takedown = True
                video.takedown_time = datetime.now()
                video.status = VideoStatusEnum.TAKEDOWN
            
            video.updated_at = datetime.now()
            db.commit()
            db.refresh(video)
        return video
    
    @staticmethod
    def get_statistics(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取统计数据"""
        videos = db.query(Video).filter(
            and_(
                Video.detected_time >= start_date,
                Video.detected_time <= end_date
            )
        ).all()
        
        stats = {
            'total': len(videos),
            'high_risk': sum(1 for v in videos if v.risk_level == RiskLevelEnum.HIGH),
            'medium_risk': sum(1 for v in videos if v.risk_level == RiskLevelEnum.MEDIUM),
            'low_risk': sum(1 for v in videos if v.risk_level == RiskLevelEnum.LOW),
            'reported': sum(1 for v in videos if v.status == VideoStatusEnum.REPORTED),
            'takedown': sum(1 for v in videos if v.is_takedown),
            'platforms': {}
        }
        
        # 按平台统计
        for platform in PlatformEnum:
            platform_videos = [v for v in videos if v.platform == platform]
            stats['platforms'][platform.value] = len(platform_videos)
        
        return stats


class ReportLogCRUD:
    """举报日志操作"""
    
    @staticmethod
    def create(db: Session, log_data: Dict[str, Any]) -> ReportLog:
        """创建举报日志"""
        log = ReportLog(**log_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_by_video(db: Session, video_id: str) -> List[ReportLog]:
        """获取视频的所有举报日志"""
        return db.query(ReportLog).filter(ReportLog.video_id == video_id).all()


class TaskLogCRUD:
    """任务日志操作"""
    
    @staticmethod
    def create(db: Session, task_name: str) -> TaskLog:
        """创建任务日志"""
        log = TaskLog(task_name=task_name, start_time=datetime.now())
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def complete(db: Session, log_id: int, success: bool, items_processed: int = 0, 
                 error_message: str = None, result_data: Dict = None):
        """完成任务日志"""
        log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
        if log:
            log.end_time = datetime.now()
            log.duration = (log.end_time - log.start_time).total_seconds()
            log.success = success
            log.items_processed = items_processed
            log.error_message = error_message
            log.result_data = result_data
            db.commit()
            db.refresh(log)
        return log


class StatisticsCRUD:
    """统计数据操作"""
    
    @staticmethod
    def get_or_create(db: Session, date: str) -> Statistics:
        """获取或创建统计记录"""
        stat = db.query(Statistics).filter(Statistics.date == date).first()
        if not stat:
            stat = Statistics(date=date)
            db.add(stat)
            db.commit()
            db.refresh(stat)
        return stat
    
    @staticmethod
    def update_daily(db: Session, date: str):
        """更新每日统计"""
        stat = StatisticsCRUD.get_or_create(db, date)
        
        # 查询当天的数据
        start_time = datetime.strptime(date, '%Y-%m-%d')
        end_time = start_time + timedelta(days=1)
        
        videos = db.query(Video).filter(
            and_(
                Video.detected_time >= start_time,
                Video.detected_time < end_time
            )
        ).all()
        
        # 更新统计
        stat.videos_detected = len(videos)
        stat.videos_high_risk = sum(1 for v in videos if v.risk_level == RiskLevelEnum.HIGH)
        stat.videos_medium_risk = sum(1 for v in videos if v.risk_level == RiskLevelEnum.MEDIUM)
        stat.videos_low_risk = sum(1 for v in videos if v.risk_level == RiskLevelEnum.LOW)
        stat.videos_reported = sum(1 for v in videos if v.status == VideoStatusEnum.REPORTED)
        stat.videos_takedown = sum(1 for v in videos if v.is_takedown)
        
        # 计算平均下架时长
        takedown_videos = [v for v in videos if v.is_takedown and v.takedown_time and v.reported_time]
        if takedown_videos:
            avg_hours = sum(
                (v.takedown_time - v.reported_time).total_seconds() / 3600 
                for v in takedown_videos
            ) / len(takedown_videos)
            stat.avg_takedown_hours = round(avg_hours, 2)
        
        # 平台统计
        platform_stats = {}
        for platform in PlatformEnum:
            platform_videos = [v for v in videos if v.platform == platform]
            platform_stats[platform.value] = {
                'total': len(platform_videos),
                'reported': sum(1 for v in platform_videos if v.status == VideoStatusEnum.REPORTED),
                'takedown': sum(1 for v in platform_videos if v.is_takedown)
            }
        stat.platform_stats = platform_stats
        
        stat.updated_at = datetime.now()
        db.commit()
        db.refresh(stat)
        
        return stat
