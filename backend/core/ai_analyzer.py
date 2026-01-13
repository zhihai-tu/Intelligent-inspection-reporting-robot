"""AI内容分析模块 - 基于大模型的黑灰产识别"""
import re
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from ..utils.config import config
from ..utils.logger import app_logger
from ..database.models import RiskLevelEnum


class AIAnalyzer:
    """AI内容分析器"""
    
    def __init__(self):
        """初始化AI分析器"""
        self.ai_config = config.ai
        self.client = None
        self._init_client()
        
        # 黑灰产关键词列表
        self.blacklist_keywords = self.ai_config.get('blacklist_keywords', [])
        
        # 风险阈值
        thresholds = self.ai_config.get('risk_threshold', {})
        self.threshold_high = thresholds.get('high', 0.8)
        self.threshold_medium = thresholds.get('medium', 0.5)
        self.threshold_low = thresholds.get('low', 0.3)
    
    def _init_client(self):
        """初始化OpenAI客户端"""
        api_key = self.ai_config.get('api_key')
        base_url = self.ai_config.get('base_url')
        
        if not api_key:
            app_logger.warning("未配置AI API密钥，内容分析功能将受限")
            return
        
        try:
            if base_url:
                self.client = OpenAI(api_key=api_key, base_url=base_url)
            else:
                self.client = OpenAI(api_key=api_key)
            app_logger.info("AI客户端初始化成功")
        except Exception as e:
            app_logger.error(f"AI客户端初始化失败: {str(e)}")
    
    def analyze_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析视频内容
        
        Args:
            video_data: 视频数据，包含title, description, cover_url等
        
        Returns:
            分析结果，包含risk_level, risk_score, ai_analysis等
        """
        try:
            # 1. 基础关键词匹配
            keyword_score = self._check_keywords(video_data)
            
            # 2. 规则引擎分析
            rule_score = self._rule_based_analysis(video_data)
            
            # 3. AI深度分析（如果配置了AI）
            ai_score = 0.0
            ai_reason = ""
            
            if self.client:
                ai_result = self._ai_deep_analysis(video_data)
                ai_score = ai_result.get('score', 0.0)
                ai_reason = ai_result.get('reason', '')
            
            # 4. 综合评分（加权平均）
            final_score = (keyword_score * 0.3 + rule_score * 0.3 + ai_score * 0.4)
            
            # 5. 确定风险等级
            risk_level = self._determine_risk_level(final_score)
            
            # 6. 组装分析结果
            analysis_result = {
                'risk_level': risk_level,
                'risk_score': round(final_score, 3),
                'ai_analysis': {
                    'keyword_score': round(keyword_score, 3),
                    'rule_score': round(rule_score, 3),
                    'ai_score': round(ai_score, 3),
                    'ai_reason': ai_reason,
                    'matched_keywords': self._extract_matched_keywords(video_data),
                    'risk_factors': self._extract_risk_factors(video_data)
                }
            }
            
            app_logger.info(f"视频分析完成: {video_data.get('video_id')} - 风险等级: {risk_level}, 评分: {final_score:.3f}")
            
            return analysis_result
            
        except Exception as e:
            app_logger.error(f"视频分析失败: {str(e)}")
            return {
                'risk_level': RiskLevelEnum.LOW,
                'risk_score': 0.0,
                'ai_analysis': {'error': str(e)}
            }
    
    def _check_keywords(self, video_data: Dict[str, Any]) -> float:
        """关键词匹配检查"""
        text = f"{video_data.get('title', '')} {video_data.get('description', '')}"
        
        matched_count = 0
        for keyword in self.blacklist_keywords:
            if keyword in text:
                matched_count += 1
        
        # 匹配关键词数量越多，分数越高
        if matched_count == 0:
            return 0.0
        elif matched_count == 1:
            return 0.3
        elif matched_count == 2:
            return 0.6
        else:
            return 0.9
    
    def _rule_based_analysis(self, video_data: Dict[str, Any]) -> float:
        """基于规则的分析"""
        score = 0.0
        text = f"{video_data.get('title', '')} {video_data.get('description', '')}"
        
        # 规则1: 包含联系方式（微信、QQ、电话）
        if re.search(r'微信|wx|WeChat|VX|vx', text, re.IGNORECASE):
            score += 0.3
        if re.search(r'QQ|qq|企鹅', text):
            score += 0.3
        if re.search(r'\d{11}|1[3-9]\d{9}', text):  # 手机号
            score += 0.3
        
        # 规则2: 包含诱导性词汇
        lure_words = ['免费', '赚钱', '日入', '月入', '兼职', '轻松', '躺赚', '返现', '优惠券']
        for word in lure_words:
            if word in text:
                score += 0.1
        
        # 规则3: 包含金融风险词汇
        finance_words = ['贷款', '借款', '额度', '下款', '征信', '网贷', '高利贷']
        for word in finance_words:
            if word in text:
                score += 0.15
        
        # 规则4: 描述过短或过长（异常特征）
        if len(text) < 10 or len(text) > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    def _ai_deep_analysis(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI深度分析"""
        if not self.client:
            return {'score': 0.0, 'reason': '未配置AI'}
        
        try:
            title = video_data.get('title', '')
            description = video_data.get('description', '')
            author = video_data.get('author', '')
            
            # 构建分析提示词
            prompt = f"""你是一个专业的内容审核专家，请分析以下视频内容是否涉及黑灰产引流、诈骗等违规行为。

视频信息：
标题：{title}
描述：{description}
作者：{author}

请从以下维度分析：
1. 是否包含诱导添加微信、QQ等联系方式的内容
2. 是否涉及非法贷款、刷单、兼职诈骗等黑灰产业
3. 是否存在虚假宣传、夸大收益等欺骗性内容
4. 内容的整体可信度和合规性

请返回JSON格式的分析结果：
{{
    "is_violation": true/false,
    "risk_score": 0.0-1.0的风险评分,
    "violation_type": "违规类型",
    "reason": "详细分析理由",
    "key_evidence": ["关键证据1", "关键证据2"]
}}"""
            
            # 调用AI模型
            response = self.client.chat.completions.create(
                model=self.ai_config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "你是一个专业的内容审核AI助手，擅长识别黑灰产和违规内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # 解析AI响应
            ai_response = response.choices[0].message.content
            
            # 尝试提取JSON
            try:
                # 查找JSON部分
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        'score': result.get('risk_score', 0.0),
                        'reason': result.get('reason', ''),
                        'is_violation': result.get('is_violation', False),
                        'violation_type': result.get('violation_type', ''),
                        'key_evidence': result.get('key_evidence', [])
                    }
            except json.JSONDecodeError:
                pass
            
            # 如果无法解析JSON，做简单的文本分析
            score = 0.0
            if '违规' in ai_response or '风险' in ai_response or '诈骗' in ai_response:
                score = 0.7
            elif '可疑' in ai_response or '需要关注' in ai_response:
                score = 0.5
            
            return {
                'score': score,
                'reason': ai_response[:500],  # 截取前500字符
                'is_violation': score > 0.5
            }
            
        except Exception as e:
            app_logger.error(f"AI深度分析失败: {str(e)}")
            return {'score': 0.0, 'reason': f'分析失败: {str(e)}'}
    
    def _determine_risk_level(self, score: float) -> RiskLevelEnum:
        """确定风险等级"""
        if score >= self.threshold_high:
            return RiskLevelEnum.HIGH
        elif score >= self.threshold_medium:
            return RiskLevelEnum.MEDIUM
        elif score >= self.threshold_low:
            return RiskLevelEnum.LOW
        else:
            return RiskLevelEnum.SAFE
    
    def _extract_matched_keywords(self, video_data: Dict[str, Any]) -> List[str]:
        """提取匹配的关键词"""
        text = f"{video_data.get('title', '')} {video_data.get('description', '')}"
        matched = []
        
        for keyword in self.blacklist_keywords:
            if keyword in text:
                matched.append(keyword)
        
        return matched
    
    def _extract_risk_factors(self, video_data: Dict[str, Any]) -> List[str]:
        """提取风险因素"""
        factors = []
        text = f"{video_data.get('title', '')} {video_data.get('description', '')}"
        
        # 检查各种风险因素
        if re.search(r'微信|wx|WeChat', text, re.IGNORECASE):
            factors.append('包含微信联系方式')
        
        if re.search(r'QQ|qq', text):
            factors.append('包含QQ联系方式')
        
        if re.search(r'\d{11}', text):
            factors.append('包含手机号码')
        
        if any(word in text for word in ['免费', '赚钱', '日入']):
            factors.append('包含诱导性词汇')
        
        if any(word in text for word in ['贷款', '借款', '网贷']):
            factors.append('涉及金融风险')
        
        return factors
    
    def batch_analyze(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分析视频"""
        results = []
        
        for video in videos:
            result = self.analyze_video(video)
            result['video_id'] = video.get('video_id')
            results.append(result)
        
        app_logger.info(f"批量分析完成，共分析 {len(results)} 个视频")
        
        return results


# 全局AI分析器实例
ai_analyzer = AIAnalyzer()
