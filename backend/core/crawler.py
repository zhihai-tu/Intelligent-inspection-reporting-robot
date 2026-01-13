"""视频爬取模块 - 抖音平台爬虫"""
import time
import random
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
from ..utils.config import config
from ..utils.logger import app_logger


class DouyinCrawler:
    """抖音平台爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        self.config = config.crawler.get('douyin', {})
        self.search_keywords = self.config.get('search_keywords', [])
        self.max_videos = self.config.get('max_videos_per_keyword', 50)
        self.user_agent = config.crawler.get('user_agent', '')
        self.timeout = config.crawler.get('timeout', 30) * 1000  # 转换为毫秒
        self.delay_range = config.crawler.get('delay_range', [2, 5])
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def init_browser(self):
        """初始化浏览器"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # 创建上下文，设置User-Agent
            context = await self.browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.page = await context.new_page()
            app_logger.info("浏览器初始化成功")
            
        except Exception as e:
            app_logger.error(f"浏览器初始化失败: {str(e)}")
            raise
    
    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            app_logger.info("浏览器已关闭")
    
    async def search_videos(self, keyword: str, max_count: int = None) -> List[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            keyword: 搜索关键词
            max_count: 最大获取数量
        
        Returns:
            视频列表
        """
        if not max_count:
            max_count = self.max_videos
        
        videos = []
        
        try:
            # 注意：抖音搜索需要登录，这里提供模拟数据生成器
            # 实际使用时需要：
            # 1. 使用cookie登录
            # 2. 或使用抖音开放平台API
            # 3. 或使用第三方数据服务
            
            app_logger.info(f"开始搜索关键词: {keyword}")
            
            # 模拟搜索结果（实际项目中需要替换为真实爬取逻辑）
            videos = await self._simulate_search(keyword, max_count)
            
            app_logger.info(f"关键词 '{keyword}' 搜索完成，获取 {len(videos)} 个视频")
            
        except Exception as e:
            app_logger.error(f"搜索视频失败: {str(e)}")
        
        return videos
    
    async def _simulate_search(self, keyword: str, max_count: int) -> List[Dict[str, Any]]:
        """
        模拟搜索结果（用于演示）
        实际项目中需要替换为真实的爬取逻辑
        """
        videos = []
        
        # 模拟数据
        for i in range(min(max_count, 10)):  # 模拟返回10条数据
            video = {
                'video_id': f'douyin_{keyword}_{int(time.time())}_{i}',
                'platform': 'douyin',
                'title': f'{keyword}相关视频标题{i+1} - 添加微信免费领取',
                'description': f'这是关于{keyword}的视频描述，包含引流信息，加微信xxxxx获取更多信息',
                'author': f'用户{random.randint(1000, 9999)}',
                'author_id': f'author_{random.randint(100000, 999999)}',
                'channel': keyword,
                'video_url': f'https://www.douyin.com/video/{random.randint(7000000000000000000, 7999999999999999999)}',
                'cover_url': 'https://example.com/cover.jpg',
                'view_count': random.randint(1000, 100000),
                'like_count': random.randint(100, 10000),
                'comment_count': random.randint(10, 1000),
                'share_count': random.randint(5, 500),
                'detected_time': datetime.now(),
                'keywords_matched': [keyword]
            }
            videos.append(video)
            
            # 随机延迟
            await asyncio.sleep(random.uniform(*self.delay_range))
        
        return videos
    
    async def get_video_detail(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        获取视频详情
        
        Args:
            video_url: 视频链接
        
        Returns:
            视频详情
        """
        try:
            if not self.page:
                await self.init_browser()
            
            # 访问视频页面
            await self.page.goto(video_url, timeout=self.timeout)
            await asyncio.sleep(random.uniform(*self.delay_range))
            
            # 提取视频信息（需要根据实际页面结构调整）
            # 这里仅为示例代码
            video_data = {
                'video_url': video_url,
                'title': await self._safe_extract(self.page, '.video-title'),
                'description': await self._safe_extract(self.page, '.video-description'),
                'author': await self._safe_extract(self.page, '.author-name'),
                # 更多字段...
            }
            
            return video_data
            
        except Exception as e:
            app_logger.error(f"获取视频详情失败: {str(e)}")
            return None
    
    async def _safe_extract(self, page: Page, selector: str) -> str:
        """安全提取元素文本"""
        try:
            element = await page.query_selector(selector)
            if element:
                return await element.inner_text()
        except:
            pass
        return ""
    
    async def check_video_status(self, video_url: str) -> bool:
        """
        检查视频是否已下架
        
        Args:
            video_url: 视频链接
        
        Returns:
            True表示已下架，False表示仍在线
        """
        try:
            if not self.page:
                await self.init_browser()
            
            response = await self.page.goto(video_url, timeout=self.timeout)
            
            # 检查是否返回404或其他错误状态
            if response.status >= 400:
                return True
            
            # 检查页面是否包含"视频已下架"等提示
            content = await self.page.content()
            if any(keyword in content for keyword in ['已下架', '不存在', '已删除', '违规']):
                return True
            
            return False
            
        except Exception as e:
            app_logger.error(f"检查视频状态失败: {str(e)}")
            return False
    
    async def crawl_all_keywords(self) -> List[Dict[str, Any]]:
        """爬取所有配置的关键词"""
        all_videos = []
        
        try:
            await self.init_browser()
            
            for keyword in self.search_keywords:
                videos = await self.search_videos(keyword)
                all_videos.extend(videos)
                
                # 随机延迟，避免被封
                await asyncio.sleep(random.uniform(5, 10))
            
            app_logger.info(f"所有关键词爬取完成，共获取 {len(all_videos)} 个视频")
            
        except Exception as e:
            app_logger.error(f"爬取失败: {str(e)}")
        
        finally:
            await self.close_browser()
        
        return all_videos


class VideoCrawler:
    """视频爬虫管理器"""
    
    def __init__(self):
        """初始化爬虫管理器"""
        self.crawlers = {
            'douyin': DouyinCrawler()
        }
    
    async def crawl_platform(self, platform: str) -> List[Dict[str, Any]]:
        """
        爬取指定平台
        
        Args:
            platform: 平台名称 (douyin, kuaishou, xiaohongshu)
        
        Returns:
            视频列表
        """
        crawler = self.crawlers.get(platform)
        
        if not crawler:
            app_logger.warning(f"未找到平台 {platform} 的爬虫")
            return []
        
        try:
            videos = await crawler.crawl_all_keywords()
            
            # 添加平台标识
            for video in videos:
                video['platform'] = platform
            
            return videos
            
        except Exception as e:
            app_logger.error(f"爬取平台 {platform} 失败: {str(e)}")
            return []
    
    async def crawl_all(self) -> List[Dict[str, Any]]:
        """爬取所有启用的平台"""
        all_videos = []
        
        crawler_config = config.crawler
        
        # 检查各平台配置
        if crawler_config.get('douyin', {}).get('enabled', False):
            videos = await self.crawl_platform('douyin')
            all_videos.extend(videos)
        
        if crawler_config.get('kuaishou', {}).get('enabled', False):
            videos = await self.crawl_platform('kuaishou')
            all_videos.extend(videos)
        
        if crawler_config.get('xiaohongshu', {}).get('enabled', False):
            videos = await self.crawl_platform('xiaohongshu')
            all_videos.extend(videos)
        
        app_logger.info(f"所有平台爬取完成，共获取 {len(all_videos)} 个视频")
        
        return all_videos
    
    async def check_video_takedown(self, video_url: str, platform: str) -> bool:
        """
        检查视频是否已下架
        
        Args:
            video_url: 视频链接
            platform: 平台名称
        
        Returns:
            True表示已下架
        """
        crawler = self.crawlers.get(platform)
        
        if not crawler:
            return False
        
        return await crawler.check_video_status(video_url)


# 全局爬虫实例
video_crawler = VideoCrawler()
