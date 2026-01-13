"""配置管理模块"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置类"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        # 替换环境变量
        self._replace_env_vars(self._config)
    
    def _replace_env_vars(self, config: Dict[str, Any]):
        """递归替换配置中的环境变量"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, "")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        支持点号分隔的嵌套键，如 'app.name'
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    @property
    def app(self) -> Dict[str, Any]:
        """应用配置"""
        return self._config.get('app', {})
    
    @property
    def database(self) -> Dict[str, Any]:
        """数据库配置"""
        return self._config.get('database', {})
    
    @property
    def ai(self) -> Dict[str, Any]:
        """AI配置"""
        return self._config.get('ai', {})
    
    @property
    def crawler(self) -> Dict[str, Any]:
        """爬虫配置"""
        return self._config.get('crawler', {})
    
    @property
    def reporter(self) -> Dict[str, Any]:
        """举报配置"""
        return self._config.get('reporter', {})
    
    @property
    def scheduler(self) -> Dict[str, Any]:
        """调度器配置"""
        return self._config.get('scheduler', {})
    
    @property
    def logging(self) -> Dict[str, Any]:
        """日志配置"""
        return self._config.get('logging', {})
    
    @property
    def report(self) -> Dict[str, Any]:
        """报表配置"""
        return self._config.get('report', {})


# 全局配置实例
config = Config()
