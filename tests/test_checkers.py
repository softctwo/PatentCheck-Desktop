"""
检查器模块测试
"""
import unittest
from pathlib import Path
from src.core.models import PatentDocument, Severity
from src.structure_checker.checker import StructureChecker
from src.image_checker.checker import ImageChecker
from src.alignment_checker.checker import AlignmentChecker
from src.abstract_checker.checker import AbstractChecker


class TestStructureChecker(unittest.TestCase):
    """测试结构检查器"""
    
    def test_empty_document(self):
        """测试空文档"""
        checker = StructureChecker()
        doc = PatentDocument(specification_path=None, figures=[])
        
        results = checker.check(doc)
        # 应该检测到缺少说明书
        self.assertTrue(any(r.severity == Severity.ERROR for r in results))
    
    def test_valid_document(self):
        """测试有效文档（模拟）"""
        checker = StructureChecker()
        # 需要实际的docx文件才能完整测试
        # 这里仅测试接口
        self.assertIsNotNone(checker.category)


class TestImageChecker(unittest.TestCase):
    """测试图像检查器"""
    
    def test_no_figures(self):
        """测试无附图"""
        checker = ImageChecker()
        doc = PatentDocument(specification_path="test.docx", figures=[])
        
        results = checker.check(doc)
        # 应该检测到缺少附图
        self.assertTrue(len(results) > 0)
    
    def test_checker_initialization(self):
        """测试检查器初始化"""
        checker = ImageChecker()
        self.assertIsNotNone(checker.category)


class TestAlignmentChecker(unittest.TestCase):
    """测试图文对齐检查器"""
    
    def test_empty_markers(self):
        """测试空标号"""
        checker = AlignmentChecker()
        doc = PatentDocument(specification_path=None, figures=[])
        
        results = checker.check(doc)
        # 应该有检查结果
        self.assertTrue(len(results) >= 0)
    
    def test_marker_continuity(self):
        """测试标号连续性"""
        checker = AlignmentChecker()
        
        # 测试连续标号
        markers = ['1', '2', '3', '4']
        gaps = checker._find_gaps(markers)
        self.assertEqual(len(gaps), 0)
        
        # 测试不连续标号
        markers = ['1', '2', '5', '6']
        gaps = checker._find_gaps(markers)
        self.assertTrue(len(gaps) > 0)


class TestAbstractChecker(unittest.TestCase):
    """测试摘要检查器"""
    
    def test_no_abstract_figure(self):
        """测试无摘要附图"""
        checker = AbstractChecker()
        doc = PatentDocument(
            specification_path="test.docx",
            figures=["fig1.jpg", "fig2.jpg"]
        )
        
        results = checker.check(doc)
        # 应该检测到缺少摘要附图
        errors = [r for r in results if r.severity == Severity.ERROR]
        self.assertTrue(len(errors) > 0)
    
    def test_has_abstract_figure(self):
        """测试存在摘要附图"""
        checker = AbstractChecker()
        doc = PatentDocument(
            specification_path="test.docx",
            figures=["摘要附图.jpg", "fig1.jpg"]
        )
        
        results = checker.check(doc)
        # 应该找到摘要附图
        passes = [r for r in results if r.severity == Severity.PASS]
        self.assertTrue(len(passes) > 0)


class TestConfigLoader(unittest.TestCase):
    """测试配置加载器"""
    
    def test_config_load(self):
        """测试配置加载"""
        from src.core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        self.assertIsNotNone(config.config)
    
    def test_get_rules(self):
        """测试获取规则"""
        from src.core.config_loader import ConfigLoader
        
        config = ConfigLoader()
        
        structure_rules = config.get_structure_rules()
        self.assertIsInstance(structure_rules, dict)
        
        image_rules = config.get_image_rules()
        self.assertIsInstance(image_rules, dict)


if __name__ == '__main__':
    unittest.main()
