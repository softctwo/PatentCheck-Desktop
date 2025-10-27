"""
说明书结构检查器
"""
from typing import List
from docx import Document

from ..core.models import CheckResult, PatentDocument, CheckCategory, Severity
from ..core.rule_engine import BaseChecker


class StructureChecker(BaseChecker):
    """说明书结构检查器"""
    
    # 必需章节
    REQUIRED_SECTIONS = [
        '技术领域',
        '背景技术',
        '发明内容',
        '附图说明',
        '具体实施方式'
    ]
    
    def __init__(self, config: dict = None):
        super().__init__(config or {'enabled': True})
    
    def check(self, document: PatentDocument) -> List[CheckResult]:
        """检查说明书结构"""
        results = []
        
        if not document.specification_path:
            results.append(CheckResult(
                rule_id="S000",
                category=CheckCategory.STRUCTURE,
                severity=Severity.ERROR,
                title="未找到说明书文件",
                description="请提供说明书文件（.docx格式）",
                location="文件夹",
                suggestion="确保文件名包含'说明书'关键字"
            ))
            return results
        
        try:
            from ..file_parser.parser import FileParser
            
            # 根据文件类型加载文档
            if document.specification_path.lower().endswith('.pdf'):
                # 加载PDF文档
                text = FileParser.extract_pdf_text(document.specification_path, use_ocr=True)
                # 将文本按行分割
                paragraphs = [line.strip() for line in text.split('\n') if line.strip()]
            else:
                # 加载Word文档
                doc = FileParser.load_word_document(document.specification_path)
                # 提取所有段落标题
                paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            
            # 检查必需章节
            missing_sections = []
            for section in self.REQUIRED_SECTIONS:
                if not self._section_exists(section, paragraphs):
                    missing_sections.append(section)
            
            if missing_sections:
                results.append(CheckResult(
                    rule_id="S001",
                    category=CheckCategory.STRUCTURE,
                    severity=Severity.ERROR,
                    title=f"缺少必需章节",
                    description=f"说明书缺少以下章节：{', '.join(missing_sections)}",
                    location=document.specification_path,
                    suggestion=f"请在说明书中添加：{', '.join(missing_sections)}",
                    reference="专利法实施细则第18条",
                    details={'missing': missing_sections}
                ))
            else:
                results.append(CheckResult(
                    rule_id="S002",
                    category=CheckCategory.STRUCTURE,
                    severity=Severity.PASS,
                    title="说明书结构完整",
                    description="说明书包含所有必需章节",
                    location=document.specification_path
                ))
            
        except Exception as e:
            results.append(CheckResult(
                rule_id="S003",
                category=CheckCategory.STRUCTURE,
                severity=Severity.ERROR,
                title="无法解析说明书",
                description=f"读取说明书时发生错误: {str(e)}",
                location=document.specification_path,
                suggestion="请检查文件格式是否正确"
            ))
        
        return results
    
    def _section_exists(self, section: str, paragraphs: List[str]) -> bool:
        """检查章节是否存在"""
        for para in paragraphs:
            # 简单的关键词匹配
            if section in para and len(para) < 50:  # 标题通常较短
                return True
        return False
