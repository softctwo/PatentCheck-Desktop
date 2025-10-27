"""
规则引擎核心
"""
import json
from typing import List, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod

from .models import CheckResult, PatentDocument, CheckCategory, Severity


class BaseChecker(ABC):
    """检查器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    def check(self, document: PatentDocument) -> List[CheckResult]:
        """执行检查，返回检查结果列表"""
        pass
    
    def is_enabled(self) -> bool:
        """检查器是否启用"""
        return self.enabled


class RuleEngine:
    """规则引擎"""
    
    def __init__(self, rules_path: str = None):
        """
        初始化规则引擎
        
        Args:
            rules_path: 规则配置文件路径
        """
        self.rules = {}
        self.checkers = []
        
        if rules_path:
            self.load_rules(rules_path)
    
    def load_rules(self, rules_path: str):
        """加载规则配置"""
        with open(rules_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.rules = config.get('rules', [])
    
    def register_checker(self, checker: BaseChecker):
        """注册检查器"""
        self.checkers.append(checker)
    
    def run_checks(self, document: PatentDocument) -> List[CheckResult]:
        """
        执行所有检查
        
        Args:
            document: 专利文档
            
        Returns:
            检查结果列表
        """
        all_results = []
        
        for checker in self.checkers:
            if checker.is_enabled():
                try:
                    results = checker.check(document)
                    all_results.extend(results)
                except Exception as e:
                    # 记录错误但不中断检查流程
                    print(f"检查器 {checker.__class__.__name__} 执行失败: {e}")
        
        return all_results
    
    def get_rules_by_category(self, category: str) -> List[Dict]:
        """获取指定类别的规则"""
        return [r for r in self.rules if r.get('category') == category]
