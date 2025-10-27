"""
核心模块单元测试
"""
import unittest
from src.core.models import (
    Severity, CheckCategory, CheckResult, 
    PatentDocument, CheckReport
)
from src.core.rule_engine import BaseChecker, RuleEngine


class TestModels(unittest.TestCase):
    """测试数据模型"""
    
    def test_severity_enum(self):
        """测试严重程度枚举"""
        self.assertEqual(Severity.ERROR.value, 'error')
        self.assertEqual(Severity.WARNING.value, 'warning')
        self.assertEqual(Severity.INFO.value, 'info')
        self.assertEqual(Severity.PASS.value, 'pass')
    
    def test_check_category_enum(self):
        """测试检查类别枚举"""
        self.assertEqual(CheckCategory.STRUCTURE.value, 'structure')
        self.assertEqual(CheckCategory.IMAGE.value, 'image')
        self.assertEqual(CheckCategory.MARKER.value, 'marker')
    
    def test_check_result(self):
        """测试检查结果"""
        result = CheckResult(
            category=CheckCategory.STRUCTURE,
            severity=Severity.ERROR,
            title="测试错误",
            description="这是一个测试错误",
            location="test.docx",
            suggestion="修复建议"
        )
        
        self.assertEqual(result.severity, Severity.ERROR)
        self.assertEqual(result.title, "测试错误")
        
        # 测试to_dict
        result_dict = result.to_dict()
        self.assertEqual(result_dict['severity'], 'error')
        self.assertEqual(result_dict['category'], 'structure')
    
    def test_patent_document(self):
        """测试专利文档"""
        doc = PatentDocument(
            specification_path="spec.docx",
            figures=["fig1.jpg", "fig2.jpg"]
        )
        
        self.assertTrue(doc.is_valid())
        self.assertEqual(len(doc.figures), 2)
    
    def test_check_report(self):
        """测试检测报告"""
        doc = PatentDocument(
            specification_path="spec.docx",
            figures=["fig1.jpg"]
        )
        
        report = CheckReport(document=doc)
        
        # 添加结果
        result1 = CheckResult(
            category=CheckCategory.STRUCTURE,
            severity=Severity.ERROR,
            title="错误1",
            description="描述",
            location="位置"
        )
        
        result2 = CheckResult(
            category=CheckCategory.IMAGE,
            severity=Severity.WARNING,
            title="警告1",
            description="描述",
            location="位置"
        )
        
        report.add_result(result1)
        report.add_result(result2)
        
        # 测试摘要
        summary = report.get_summary()
        self.assertEqual(summary['total'], 2)
        self.assertEqual(summary['errors'], 1)
        self.assertEqual(summary['warnings'], 1)


class MockChecker(BaseChecker):
    """模拟检查器"""
    
    def check(self, document):
        return [
            CheckResult(
                category=CheckCategory.STRUCTURE,
                severity=Severity.PASS,
                title="模拟检查",
                description="检查通过",
                location="mock"
            )
        ]


class TestRuleEngine(unittest.TestCase):
    """测试规则引擎"""
    
    def test_register_checker(self):
        """测试注册检查器"""
        engine = RuleEngine()
        checker = MockChecker()
        
        engine.register_checker(checker)
        self.assertEqual(len(engine.checkers), 1)
    
    def test_run_checks(self):
        """测试运行检查"""
        engine = RuleEngine()
        checker = MockChecker()
        engine.register_checker(checker)
        
        doc = PatentDocument(
            specification_path="test.docx",
            figures=["test.jpg"]
        )
        
        results = engine.run_checks(doc)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].severity, Severity.PASS)


if __name__ == '__main__':
    unittest.main()
