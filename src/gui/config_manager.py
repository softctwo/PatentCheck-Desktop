"""
配置管理模块
"""
import json
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".patentcheck"
        self.config_file = self.config_dir / "config.json"
        self.history_file = self.config_dir / "history.json"
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 默认配置
        self.default_config = {
            "auto_save_report": True,
            "default_output_format": "pdf",
            "max_history": 20,
            "theme": "light",
            "show_hints": True,
            "last_folder": ""
        }
        
        self.config = self.load_config()
        self.history = self.load_history()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    return {**self.default_config, **config}
            except Exception:
                pass
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_history(self) -> list:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []
    
    def save_history(self):
        """保存历史记录"""
        try:
            # 限制历史记录数量
            max_history = self.config.get("max_history", 20)
            self.history = self.history[-max_history:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_history(self, folder_path: str, summary: Dict[str, int]):
        """添加历史记录"""
        from datetime import datetime
        
        record = {
            "folder": folder_path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": summary
        }
        
        # 移除相同路径的旧记录
        self.history = [h for h in self.history if h["folder"] != folder_path]
        
        # 添加新记录到末尾
        self.history.append(record)
        
        # 保存
        self.save_history()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
        self.save_config()
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.save_history()
