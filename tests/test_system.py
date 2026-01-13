"""系统测试脚本"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
from backend.utils.config import config
from backend.utils.logger import app_logger
from backend.database.models import init_db, SessionLocal
from backend.database.crud import VideoCRUD
from backend.core.ai_analyzer import ai_analyzer
from backend.core.crawler import video_crawler
from backend.core.reporter import video_reporter


async def test_database():
    """测试数据库"""
    print("\n" + "="*50)
    print("测试1: 数据库初始化")
    print("="*50)
    
    try:
        init_db()
        app_logger.info("✓ 数据库初始化成功")
        return True
    except Exception as e:
        app_logger.error(f"✗ 数据库初始化失败: {str(e)}")
        return False


async def test_ai_analyzer():
    """测试AI分析器"""
    print("\n" + "="*50)
    print("测试2: AI内容分析")
    print("="*50)
    
    # 测试视频数据
    test_video = {
        'video_id': 'test_001',
        'title': '加微信免费领取贷款额度，日入过万',
        'description': '想要赚钱的朋友加我微信xxxxx，免费帮你办理大额贷款',
        'author': '测试用户',
        'cover_url': 'https://example.com/cover.jpg'
    }
    
    try:
        result = ai_analyzer.analyze_video(test_video)
        app_logger.info(f"✓ AI分析成功")
        app_logger.info(f"  - 风险等级: {result['risk_level']}")
        app_logger.info(f"  - 风险评分: {result['risk_score']}")
        app_logger.info(f"  - 匹配关键词: {result['ai_analysis'].get('matched_keywords', [])}")
        return True
    except Exception as e:
        app_logger.error(f"✗ AI分析失败: {str(e)}")
        return False


async def test_crawler():
    """测试爬虫"""
    print("\n" + "="*50)
    print("测试3: 视频爬取（模拟）")
    print("="*50)
    
    try:
        videos = await video_crawler.crawl_platform('douyin')
        app_logger.info(f"✓ 爬取成功，获取 {len(videos)} 个视频")
        
        # 保存到数据库
        db = SessionLocal()
        saved_count = 0
        for video_data in videos[:5]:  # 只保存前5个测试
            existing = VideoCRUD.get_by_video_id(db, video_data['video_id'])
            if not existing:
                VideoCRUD.create(db, video_data)
                saved_count += 1
        db.close()
        
        app_logger.info(f"  - 保存到数据库: {saved_count} 个")
        return True
    except Exception as e:
        app_logger.error(f"✗ 爬取失败: {str(e)}")
        return False


async def test_analysis_workflow():
    """测试分析工作流"""
    print("\n" + "="*50)
    print("测试4: 完整分析流程")
    print("="*50)
    
    try:
        db = SessionLocal()
        
        # 获取待分析的视频
        videos = VideoCRUD.get_pending_analysis(db, limit=5)
        app_logger.info(f"待分析视频数量: {len(videos)}")
        
        if videos:
            # 分析第一个视频
            video = videos[0]
            video_data = {
                'video_id': video.video_id,
                'title': video.title,
                'description': video.description,
                'author': video.author,
                'cover_url': video.cover_url
            }
            
            # 执行分析
            analysis_result = ai_analyzer.analyze_video(video_data)
            
            # 更新数据库
            VideoCRUD.update_analysis(db, video.video_id, analysis_result)
            
            app_logger.info(f"✓ 分析工作流测试成功")
            app_logger.info(f"  - 视频ID: {video.video_id}")
            app_logger.info(f"  - 风险等级: {analysis_result['risk_level']}")
        else:
            app_logger.info("没有待分析的视频，跳过此测试")
        
        db.close()
        return True
    except Exception as e:
        app_logger.error(f"✗ 分析工作流测试失败: {str(e)}")
        return False


async def test_reporter():
    """测试举报功能"""
    print("\n" + "="*50)
    print("测试5: 自动举报（模拟）")
    print("="*50)
    
    test_video = {
        'video_id': 'test_report_001',
        'video_url': 'https://www.douyin.com/video/test',
        'platform': 'douyin',
        'title': '测试视频'
    }
    
    try:
        result = await video_reporter.report_video(test_video)
        app_logger.info(f"✓ 举报测试完成")
        app_logger.info(f"  - 成功: {result['success']}")
        app_logger.info(f"  - 原因: {result.get('report_reason', 'N/A')}")
        return True
    except Exception as e:
        app_logger.error(f"✗ 举报测试失败: {str(e)}")
        return False


async def test_statistics():
    """测试统计功能"""
    print("\n" + "="*50)
    print("测试6: 数据统计")
    print("="*50)
    
    try:
        db = SessionLocal()
        
        from datetime import timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        stats = VideoCRUD.get_statistics(db, start_date, end_date)
        
        app_logger.info(f"✓ 统计数据获取成功")
        app_logger.info(f"  - 总视频数: {stats['total']}")
        app_logger.info(f"  - 高风险: {stats['high_risk']}")
        app_logger.info(f"  - 已举报: {stats['reported']}")
        app_logger.info(f"  - 已下架: {stats['takedown']}")
        
        db.close()
        return True
    except Exception as e:
        app_logger.error(f"✗ 统计测试失败: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("智能巡检举报下架机器人 - 系统测试")
    print("="*70)
    
    results = []
    
    # 运行所有测试
    results.append(await test_database())
    results.append(await test_ai_analyzer())
    results.append(await test_crawler())
    results.append(await test_analysis_workflow())
    results.append(await test_reporter())
    results.append(await test_statistics())
    
    # 汇总结果
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"总测试数: {total}")
    print(f"✓ 通过: {passed}")
    print(f"✗ 失败: {failed}")
    print(f"通过率: {(passed/total*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！系统运行正常。")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查日志。")
    
    print("="*70 + "\n")
    
    # 清理资源
    await video_reporter.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
