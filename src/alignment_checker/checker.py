"""
图文标号对齐检查器
"""
import re
from typing import List, Set
from docx import Document

from ..core.models import CheckResult, PatentDocument, CheckCategory, Severity
from ..core.rule_engine import BaseChecker


class AlignmentChecker(BaseChecker):
    """图文标号对齐检查器"""
    
    def __init__(self, config: dict = None):
        super().__init__(config or {'enabled': True})
    
    def check(self, document: PatentDocument) -> List[CheckResult]:
        """检查图文标号一致性"""
        results = []
        
        if not document.specification_path:
            return results
        
        try:
            # 1. 从说明书中提取标号
            spec_markers = self._extract_markers_from_spec(document.specification_path)
            
            # 2. 从附图说明段落提取图中应有的标号
            # 这里简化处理：假设说明书中提到的所有数字标号都应该在图中
            
            # 3. 检查标号合理性
            if spec_markers:
                # 检查标号是否连续
                sorted_markers = sorted(spec_markers)
                missing_markers = []
                
                if sorted_markers:
                    for i in range(sorted_markers[0], sorted_markers[-1] + 1):
                        if i not in spec_markers:
                            missing_markers.append(i)
                    
                    if missing_markers:
                        results.append(CheckResult(
                            rule_id="A001",
                            category=CheckCategory.ALIGNMENT,
                            severity=Severity.WARNING,
                            title="标号序列不连续",
                            description=f"标号从{sorted_markers[0]}到{sorted_markers[-1]}，但缺少：{missing_markers}",
                            location=document.specification_path,
                            suggestion="检查是否遗漏了某些标号的说明",
                            reference="专利审查指南"
                        ))
                    
                    # 统计信息
                    results.append(CheckResult(
                        rule_id="A002",
                        category=CheckCategory.ALIGNMENT,
                        severity=Severity.PASS,
                        title=f"检测到{len(spec_markers)}个标号",
                        description=f"标号范围: {sorted_markers[0]}-{sorted_markers[-1]}",
                        location=document.specification_path,
                        details={'markers': sorted(list(spec_markers))}
                    ))
            else:
                results.append(CheckResult(
                    rule_id="A003",
                    category=CheckCategory.ALIGNMENT,
                    severity=Severity.INFO,
                    title="未检测到标号",
                    description="说明书中未找到附图标号（可能是方法类专利）",
                    location=document.specification_path
                ))
            
        except Exception as e:
            results.append(CheckResult(
                rule_id="A004",
                category=CheckCategory.ALIGNMENT,
                severity=Severity.ERROR,
                title="标号检查失败",
                description=f"检查标号时发生错误: {str(e)}",
                location=document.specification_path
            ))
        
        return results
    
    def _extract_markers_from_spec(self, spec_path: str) -> Set[int]:
        """
        从说明书中提取标号
        
        Returns:
            标号集合
        """
        markers = set()
        
        from ..file_parser.parser import FileParser
        
        # 根据文件类型提取文本
        if spec_path.lower().endswith('.pdf'):
            # PDF文档
            full_text = FileParser.extract_pdf_text(spec_path, use_ocr=True)
        else:
            # Word文档
            doc = FileParser.load_word_document(spec_path)
            full_text = '\n'.join([p.text for p in doc.paragraphs])
        
        # 正则表达式匹配常见的标号模式
        # 模式1: "标号12"、"零件15"、"部件20"等
        pattern1 = r'(?:标号|零件|部件|元件|组件|构件)[\s]?(\d+)'
        matches1 = re.findall(pattern1, full_text)
        markers.update(int(m) for m in matches1)
        
        # 模式2: "12—螺栓"、"15-连接件"等（中文破折号和短横线）
        pattern2 = r'(\d+)[—\-—]\s*[\u4e00-\u9fa5]+'
        matches2 = re.findall(pattern2, full_text)
        markers.update(int(m) for m in matches2)
        
        # 模式3: "如图1所示，12为..."
        pattern3 = r'(\d+)\s*[为是]'
        matches3 = re.findall(pattern3, full_text)
        markers.update(int(m) for m in matches3 if 1 < int(m) < 1000)
        
        # 过滤掉明显不是标号的数字（如年份、图号等）
        markers = {m for m in markers if 1 < m < 200}  # 标号通常在1-200之间
        
        return markers
