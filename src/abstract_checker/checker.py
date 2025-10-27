"""
摘要附图检查器
验证摘要附图的完整性和合规性
"""
from pathlib import Path
from typing import List
import re

from src.core.models import CheckResult, Severity, CheckCategory, PatentDocument
from src.core.rule_engine import BaseChecker


class AbstractChecker(BaseChecker):
    """摘要附图检查器"""
    
    def __init__(self):
        """初始化检查器"""
        super().__init__()
        self.category = CheckCategory.ABSTRACT
    
    def check(self, document: PatentDocument) -> List[CheckResult]:
        """
        执行摘要附图检查
        
        Args:
            document: 专利文档
            
        Returns:
            检查结果列表
        """
        results = []
        
        # 检查1: 是否存在摘要附图
        has_abstract_figure = self._check_abstract_figure_exists(document)
        results.append(has_abstract_figure)
        
        # 如果存在摘要附图，进行进一步检查
        if has_abstract_figure.severity != Severity.ERROR:
            # 检查2: 摘要附图规格
            figure_spec = self._check_abstract_figure_spec(document)
            if figure_spec:
                results.append(figure_spec)
            
            # 检查3: 摘要附图标号
            figure_marker = self._check_abstract_figure_marker(document)
            if figure_marker:
                results.append(figure_marker)
        
        return results
    
    def _check_abstract_figure_exists(self, document: PatentDocument) -> CheckResult:
        """
        检查是否存在摘要附图
        
        Args:
            document: 专利文档
            
        Returns:
            检查结果
        """
        # 查找名称包含"摘要附图"或"abstract"的图片
        abstract_figure = None
        
        for figure in document.figures:
            figure_name = Path(figure).name.lower()
            if '摘要' in figure_name or 'abstract' in figure_name:
                abstract_figure = figure
                break
        
        if abstract_figure:
            return CheckResult(
                category=self.category,
                severity=Severity.PASS,
                title="摘要附图存在性检查",
                description=f"找到摘要附图: {Path(abstract_figure).name}",
                location=abstract_figure,
                suggestion=None
            )
        else:
            return CheckResult(
                category=self.category,
                severity=Severity.ERROR,
                title="缺少摘要附图",
                description="未找到摘要附图文件",
                location="附图文件夹",
                suggestion="请提供名称包含'摘要附图'或'abstract'的图片文件"
            )
    
    def _check_abstract_figure_spec(self, document: PatentDocument) -> CheckResult:
        """
        检查摘要附图规格
        
        Args:
            document: 专利文档
            
        Returns:
            检查结果（如果有问题）
        """
        # 查找摘要附图
        abstract_figure = None
        for figure in document.figures:
            figure_name = Path(figure).name.lower()
            if '摘要' in figure_name or 'abstract' in figure_name:
                abstract_figure = figure
                break
        
        if not abstract_figure:
            return None
        
        # 检查文件格式（应该是常见图片格式）
        valid_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}
        file_ext = Path(abstract_figure).suffix.lower()
        
        if file_ext not in valid_extensions:
            return CheckResult(
                category=self.category,
                severity=Severity.WARNING,
                title="摘要附图格式可能不规范",
                description=f"摘要附图格式为 {file_ext}",
                location=abstract_figure,
                suggestion=f"建议使用常见图片格式: {', '.join(valid_extensions)}"
            )
        
        # 规格检查通过
        return CheckResult(
            category=self.category,
            severity=Severity.PASS,
            title="摘要附图格式检查",
            description=f"摘要附图格式正确: {file_ext}",
            location=abstract_figure,
            suggestion=None
        )
    
    def _check_abstract_figure_marker(self, document: PatentDocument) -> CheckResult:
        """
        检查摘要附图标号
        
        Args:
            document: 专利文档
            
        Returns:
            检查结果（如果有问题）
        """
        # 查找摘要附图
        abstract_figure = None
        for figure in document.figures:
            figure_name = Path(figure).name.lower()
            if '摘要' in figure_name or 'abstract' in figure_name:
                abstract_figure = figure
                break
        
        if not abstract_figure:
            return None
        
        # 检查文件名中是否包含"图1"或"Fig.1"等标识
        figure_name = Path(abstract_figure).stem
        
        # 匹配图号模式
        patterns = [
            r'图\s*1',  # 图1, 图 1
            r'Fig\.?\s*1',  # Fig.1, Fig 1
            r'Figure\s*1',  # Figure 1
        ]
        
        has_marker = any(re.search(pattern, figure_name, re.IGNORECASE) for pattern in patterns)
        
        if not has_marker:
            return CheckResult(
                category=self.category,
                severity=Severity.WARNING,
                title="摘要附图标号建议",
                description="摘要附图文件名中未明确标注'图1'",
                location=abstract_figure,
                suggestion="建议在文件名中包含'图1'或'Fig.1'以明确标识"
            )
        
        return CheckResult(
            category=self.category,
            severity=Severity.PASS,
            title="摘要附图标号检查",
            description="摘要附图标号规范",
            location=abstract_figure,
            suggestion=None
        )
    
    def _check_abstract_content_match(self, document: PatentDocument) -> CheckResult:
        """
        检查摘要内容与附图的对应关系（高级功能）
        
        Args:
            document: 专利文档
            
        Returns:
            检查结果
        """
        # 这个功能需要解析Word文档中的摘要部分
        # 当前版本暂不实现，留作扩展
        return None
