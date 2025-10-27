"""
配置加载器
用于加载和管理检测规则配置
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """配置加载器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置加载器"""
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_path: Optional[str] = None):
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，默认使用内置配置
        """
        if config_path is None:
            # 使用默认配置文件
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "resources" / "rules" / "detection_rules.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            print(f"✓ 配置文件加载成功: {config_path}")
        except FileNotFoundError:
            print(f"⚠️  配置文件不存在: {config_path}，使用默认配置")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}，使用默认配置")
            self._config = self._get_default_config()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号路径）
        
        Args:
            key_path: 配置键路径，如 "image_rules.resolution.min_width"
            default: 默认值
            
        Returns:
            配置值
        """
        if self._config is None:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_structure_rules(self) -> Dict:
        """获取结构检查规则"""
        return self.get("structure_rules", {})
    
    def get_image_rules(self) -> Dict:
        """获取图像检查规则"""
        return self.get("image_rules", {})
    
    def get_marker_rules(self) -> Dict:
        """获取标号检查规则"""
        return self.get("marker_rules", {})
    
    def get_alignment_rules(self) -> Dict:
        """获取对齐检查规则"""
        return self.get("alignment_rules", {})
    
    def get_abstract_rules(self) -> Dict:
        """获取摘要检查规则"""
        return self.get("abstract_rules", {})
    
    def get_report_rules(self) -> Dict:
        """获取报告生成规则"""
        return self.get("report_rules", {})
    
    def get_performance_settings(self) -> Dict:
        """获取性能设置"""
        return self.get("performance", {})
    
    def get_logging_settings(self) -> Dict:
        """获取日志设置"""
        return self.get("logging", {})
    
    def _get_default_config(self) -> Dict:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "version": "1.0",
            "structure_rules": {
                "required_sections": [
                    "技术领域",
                    "背景技术",
                    "发明内容",
                    "附图说明",
                    "具体实施方式"
                ]
            },
            "image_rules": {
                "resolution": {
                    "min_width": 800,
                    "min_height": 600,
                    "min_dpi": 150
                },
                "quality": {
                    "check_color_pixels": True,
                    "max_color_pixel_ratio": 0.01
                }
            },
            "marker_rules": {
                "detection": {
                    "use_ocr": True,
                    "use_hough_circle": True
                }
            },
            "report_rules": {
                "output": {
                    "default_format": "pdf",
                    "include_summary": True
                }
            }
        }
    
    def reload(self, config_path: Optional[str] = None):
        """
        重新加载配置
        
        Args:
            config_path: 配置文件路径
        """
        self._config = None
        self.load_config(config_path)
    
    @property
    def config(self) -> Dict:
        """获取完整配置"""
        return self._config or {}


# 全局配置实例
config = ConfigLoader()
