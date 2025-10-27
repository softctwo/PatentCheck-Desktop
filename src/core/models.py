"""
核心数据结构定义
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class Severity(Enum):
    """错误严重程度"""
    ERROR = "error"      # 严重错误（红色）
    WARNING = "warning"  # 警告（黄色）
    INFO = "info"        # 提示（蓝色）
    PASS = "pass"        # 通过（绿色）


class CheckCategory(Enum):
    """检查类别"""
    STRUCTURE = "structure"          # 说明书结构
    IMAGE_FORMAT = "image_format"    # 附图形式
    MARKER = "marker"                # 标号检测
    ALIGNMENT = "alignment"          # 图文对齐
    ABSTRACT = "abstract"            # 摘要附图
    AI_REVIEW = "ai_review"          # AI审查


@dataclass
class CheckResult:
    """单个检查结果"""
    rule_id: str                    # 规则ID
    category: CheckCategory         # 检查类别
    severity: Severity              # 严重程度
    title: str                      # 标题
    description: str                # 描述
    location: str                   # 位置（文件名、行号等）
    suggestion: Optional[str] = None  # 修改建议
    reference: Optional[str] = None   # 法规参考
    details: Dict[str, Any] = field(default_factory=dict)  # 详细信息
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'suggestion': self.suggestion,
            'reference': self.reference,
            'details': self.details
        }


@dataclass
class PatentDocument:
    """专利文档数据结构"""
    specification_path: Optional[str] = None  # 说明书路径
    abstract_path: Optional[str] = None       # 摘要路径
    claims_path: Optional[str] = None         # 权利要求路径
    figures: List[str] = field(default_factory=list)  # 附图路径列表
    
    # 解析后的内容
    specification_content: Optional[Any] = None
    figures_content: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """检查文档是否有效"""
        # PDF文档可能包含所有内容，不需要单独的附图文件
        if self.specification_path is not None:
            # 如果是PDF文档，只需要有说明书
            if self.specification_path.lower().endswith('.pdf'):
                return True
            # 如果是Word文档，需要有附图
            else:
                return len(self.figures) > 0
        return False


@dataclass
class CheckReport:
    """检测报告"""
    timestamp: datetime = field(default_factory=datetime.now)
    document: PatentDocument = field(default_factory=PatentDocument)
    results: List[CheckResult] = field(default_factory=list)
    
    # 统计信息
    total_checks: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    passes: int = 0
    
    # AI审查结果
    ai_review_result: Optional[str] = None
    ai_review_prompt: Optional[str] = None
    
    def add_result(self, result: CheckResult):
        """添加检查结果"""
        self.results.append(result)
        self.total_checks += 1
        
        if result.severity == Severity.ERROR:
            self.errors += 1
        elif result.severity == Severity.WARNING:
            self.warnings += 1
        elif result.severity == Severity.INFO:
            self.infos += 1
        elif result.severity == Severity.PASS:
            self.passes += 1
    
    def get_summary(self) -> Dict[str, int]:
        """获取统计摘要"""
        return {
            'total': self.total_checks,
            'errors': self.errors,
            'warnings': self.warnings,
            'infos': self.infos,
            'passes': self.passes
        }
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'summary': self.get_summary(),
            'results': [r.to_dict() for r in self.results],
            'ai_review_result': self.ai_review_result,
            'ai_review_prompt': self.ai_review_prompt
        }
