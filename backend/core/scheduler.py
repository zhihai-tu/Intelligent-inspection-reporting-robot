"""任务调度系统"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ..utils.config import config
from ..utils.logger import app_logger
from ..database.models import SessionLocal, init_db
from ..database.crud import VideoCRUD, TaskLogCRUD, StatisticsCRUD
from .crawler import video_crawler
from .ai_analyzer import ai_analyzer
from .reporter import video_reporter


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = AsyncIOScheduler()
        self.tasks_config = config.scheduler.get('tasks', [])
        self.db: Session = None
    
    def init_tasks(self):
        """初始化定时任务"""
        app_logger.info("开始初始化定时任务...")
        
        # 确保数据库已初始化
        init_db()
        
        for task_config in self.tasks_config:
            if not task_config.get('enabled', True):
                continue
            
            task_name = task_config['name']
            cron_expr = task_config['cron']
            
            # 根据任务名称映射到对应的函数
            task_func = self._get_task_function(task_name)
            
            if task_func:
                # 添加定时任务
                self.scheduler.add_job(
                    task_func,
                    CronTrigger.from_crontab(cron_expr),
                    id=task_name,
                    name=task_name,
                    replace_existing=True
                )
                app_logger.info(f"任务已添加: {task_name} - {cron_expr}")
            else:
                app_logger.warning(f"未找到任务函数: {task_name}")
    
    def _get_task_function(self, task_name: str):
        """获取任务对应的函数"""
        task_map = {
            'video_crawl_task': self.video_crawl_task,
            'ai_analysis_task': self.ai_analysis_task,
            'auto_report_task': self.auto_report_task,
            'status_check_task': self.status_check_task,
            'daily_report_task': self.daily_report_task
        }
        return task_map.get(task_name)
    
    async def video_crawl_task(self):
        """视频爬取任务"""
        db = SessionLocal()
        task_log = TaskLogCRUD.create(db, 'video_crawl_task')
        
        try:
            app_logger.info("开始执行视频爬取任务...")
            
            # 爬取所有平台视频
            videos = await video_crawler.crawl_all()
            
            # 保存到数据库
            saved_count = 0
            for video_data in videos:
                # 检查是否已存在
                existing = VideoCRUD.get_by_video_id(db, video_data['video_id'])
                if not existing:
                    VideoCRUD.create(db, video_data)
                    saved_count += 1
            
            app_logger.info(f"视频爬取任务完成: 获取 {len(videos)} 个，新增 {saved_count} 个")
            
            # 完成任务日志
            TaskLogCRUD.complete(
                db, task_log.id, 
                success=True, 
                items_processed=saved_count,
                result_data={'total': len(videos), 'new': saved_count}
            )
            
        except Exception as e:
            app_logger.error(f"视频爬取任务失败: {str(e)}")
            TaskLogCRUD.complete(db, task_log.id, success=False, error_message=str(e))
        
        finally:
            db.close()
    
    async def ai_analysis_task(self):
        """AI分析任务"""
        db = SessionLocal()
        task_log = TaskLogCRUD.create(db, 'ai_analysis_task')
        
        try:
            app_logger.info("开始执行AI分析任务...")
            
            # 获取待分析的视频
            videos = VideoCRUD.get_pending_analysis(db, limit=100)
            
            if not videos:
                app_logger.info("没有待分析的视频")
                TaskLogCRUD.complete(db, task_log.id, success=True, items_processed=0)
                return
            
            # 批量分析
            analyzed_count = 0
            for video in videos:
                video_data = {
                    'video_id': video.video_id,
                    'title': video.title,
                    'description': video.description,
                    'author': video.author,
                    'cover_url': video.cover_url
                }
                
                # AI分析
                analysis_result = ai_analyzer.analyze_video(video_data)
                
                # 更新数据库
                VideoCRUD.update_analysis(db, video.video_id, analysis_result)
                analyzed_count += 1
            
            app_logger.info(f"AI分析任务完成: 分析 {analyzed_count} 个视频")
            
            # 完成任务日志
            TaskLogCRUD.complete(
                db, task_log.id,
                success=True,
                items_processed=analyzed_count
            )
            
        except Exception as e:
            app_logger.error(f"AI分析任务失败: {str(e)}")
            TaskLogCRUD.complete(db, task_log.id, success=False, error_message=str(e))
        
        finally:
            db.close()
    
    async def auto_report_task(self):
        """自动举报任务"""
        db = SessionLocal()
        task_log = TaskLogCRUD.create(db, 'auto_report_task')
        
        try:
            app_logger.info("开始执行自动举报任务...")
            
            # 获取待举报的视频
            videos = VideoCRUD.get_pending_report(db, limit=50)
            
            if not videos:
                app_logger.info("没有待举报的视频")
                TaskLogCRUD.complete(db, task_log.id, success=True, items_processed=0)
                return
            
            # 批量举报
            reported_count = 0
            for video in videos:
                video_data = {
                    'video_id': video.video_id,
                    'video_url': video.video_url,
                    'platform': video.platform.value,
                    'title': video.title
                }
                
                # 执行举报
                report_result = await video_reporter.report_video(video_data)
                
                # 更新数据库
                if report_result.get('success'):
                    VideoCRUD.update_report(db, video.video_id, {
                        'report_reason': report_result.get('report_reason'),
                        'report_result': 'success'
                    })
                    reported_count += 1
            
            app_logger.info(f"自动举报任务完成: 举报 {reported_count} 个视频")
            
            # 完成任务日志
            TaskLogCRUD.complete(
                db, task_log.id,
                success=True,
                items_processed=reported_count
            )
            
        except Exception as e:
            app_logger.error(f"自动举报任务失败: {str(e)}")
            TaskLogCRUD.complete(db, task_log.id, success=False, error_message=str(e))
        
        finally:
            db.close()
    
    async def status_check_task(self):
        """下架状态检查任务"""
        db = SessionLocal()
        task_log = TaskLogCRUD.create(db, 'status_check_task')
        
        try:
            app_logger.info("开始执行下架状态检查任务...")
            
            # 获取需要检查的视频
            videos = VideoCRUD.get_need_check_takedown(db, limit=100)
            
            if not videos:
                app_logger.info("没有需要检查的视频")
                TaskLogCRUD.complete(db, task_log.id, success=True, items_processed=0)
                return
            
            # 检查下架状态
            checked_count = 0
            takedown_count = 0
            
            for video in videos:
                # 检查视频是否已下架
                is_takedown = await video_crawler.check_video_takedown(
                    video.video_url, 
                    video.platform.value
                )
                
                # 更新状态
                VideoCRUD.update_takedown(db, video.video_id, is_takedown)
                
                checked_count += 1
                if is_takedown:
                    takedown_count += 1
            
            app_logger.info(f"下架状态检查任务完成: 检查 {checked_count} 个，发现下架 {takedown_count} 个")
            
            # 完成任务日志
            TaskLogCRUD.complete(
                db, task_log.id,
                success=True,
                items_processed=checked_count,
                result_data={'checked': checked_count, 'takedown': takedown_count}
            )
            
        except Exception as e:
            app_logger.error(f"下架状态检查任务失败: {str(e)}")
            TaskLogCRUD.complete(db, task_log.id, success=False, error_message=str(e))
        
        finally:
            db.close()
    
    async def daily_report_task(self):
        """每日报表生成任务"""
        db = SessionLocal()
        task_log = TaskLogCRUD.create(db, 'daily_report_task')
        
        try:
            app_logger.info("开始执行每日报表生成任务...")
            
            # 获取昨天的日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 更新统计数据
            stat = StatisticsCRUD.update_daily(db, today)
            
            app_logger.info(f"每日报表生成完成: {today}")
            app_logger.info(f"统计数据 - 检测: {stat.videos_detected}, 举报: {stat.videos_reported}, 下架: {stat.videos_takedown}")
            
            # 完成任务日志
            TaskLogCRUD.complete(
                db, task_log.id,
                success=True,
                items_processed=1,
                result_data={
                    'date': today,
                    'videos_detected': stat.videos_detected,
                    'videos_reported': stat.videos_reported,
                    'videos_takedown': stat.videos_takedown
                }
            )
            
        except Exception as e:
            app_logger.error(f"每日报表生成任务失败: {str(e)}")
            TaskLogCRUD.complete(db, task_log.id, success=False, error_message=str(e))
        
        finally:
            db.close()
    
    def start(self):
        """启动调度器"""
        self.init_tasks()
        self.scheduler.start()
        app_logger.info("任务调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        app_logger.info("任务调度器已关闭")
    
    def get_jobs(self) -> List[Dict[str, Any]]:
        """获取所有任务信息"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': str(job.next_run_time) if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs


# 全局调度器实例
task_scheduler = TaskScheduler()
