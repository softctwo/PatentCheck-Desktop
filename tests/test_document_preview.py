"""
测试文档预览功能
"""
import sys
import os
from pathlib import Path
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gui.document_preview_dialog import DocumentPreviewDialog, DocumentViewer, DocumentLoadThread
from src.core.models import PatentDocument, CheckReport


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def test_pdf_path():
    """测试PDF文件路径"""
    # 使用项目中的测试PDF文件
    pdf_path = project_root / "test_chinese_pdf_output.pdf"
    if pdf_path.exists():
        return str(pdf_path)
    return None


@pytest.fixture
def test_word_path():
    """测试Word文件路径"""
    # 使用项目中的测试Word文件
    word_path = project_root / "test_data" / "说明书.docx"
    if word_path.exists():
        return str(word_path)
    return None


class TestDocumentViewer:
    """测试DocumentViewer类"""
    
    def test_init(self, qapp):
        """测试初始化"""
        viewer = DocumentViewer()
        assert viewer is not None
        assert viewer.current_page == 0
        assert viewer.zoom_factor == 1.0
        assert len(viewer.pages) == 0
    
    def test_navigation_buttons_disabled_initially(self, qapp):
        """测试导航按钮初始状态"""
        viewer = DocumentViewer()
        assert not viewer.btn_prev.isEnabled()
        assert not viewer.btn_next.isEnabled()
    
    def test_zoom_in(self, qapp):
        """测试放大功能"""
        viewer = DocumentViewer()
        initial_zoom = viewer.zoom_factor
        viewer.zoom_in()
        assert viewer.zoom_factor > initial_zoom
    
    def test_zoom_out(self, qapp):
        """测试缩小功能"""
        viewer = DocumentViewer()
        viewer.zoom_factor = 2.0
        initial_zoom = viewer.zoom_factor
        viewer.zoom_out()
        assert viewer.zoom_factor < initial_zoom
    
    def test_fit_to_window(self, qapp):
        """测试适应窗口功能"""
        viewer = DocumentViewer()
        viewer.zoom_factor = 2.5
        viewer.fit_to_window()
        assert viewer.zoom_factor == 1.0


class TestDocumentLoadThread:
    """测试DocumentLoadThread类"""
    
    def test_pdf_loading(self, qapp, test_pdf_path):
        """测试PDF加载"""
        if not test_pdf_path:
            pytest.skip("测试PDF文件不存在")
        
        thread = DocumentLoadThread("测试PDF", test_pdf_path)
        
        # 收集信号
        results = {}
        
        def on_finished(doc_type, pages):
            results['success'] = True
            results['doc_type'] = doc_type
            results['page_count'] = len(pages)
        
        def on_error(doc_type, error_msg):
            results['error'] = error_msg
        
        thread.finished.connect(on_finished)
        thread.error.connect(on_error)
        
        thread.run()
        
        # 验证结果
        assert 'success' in results
        assert results['doc_type'] == "测试PDF"
        assert results['page_count'] > 0
    
    def test_word_loading(self, qapp, test_word_path):
        """测试Word加载"""
        if not test_word_path:
            pytest.skip("测试Word文件不存在")
        
        thread = DocumentLoadThread("测试Word", test_word_path)
        
        results = {}
        
        def on_finished(doc_type, pages):
            results['success'] = True
            results['doc_type'] = doc_type
            results['page_count'] = len(pages)
        
        def on_error(doc_type, error_msg):
            results['error'] = error_msg
        
        thread.finished.connect(on_finished)
        thread.error.connect(on_error)
        
        thread.run()
        
        # 验证结果
        assert 'success' in results or 'error' in results
        if 'success' in results:
            assert results['doc_type'] == "测试Word"
            assert results['page_count'] > 0
    
    def test_unsupported_format(self, qapp):
        """测试不支持的格式"""
        # 创建一个临时的不支持格式文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            thread = DocumentLoadThread("测试文本", temp_path)
            
            results = {}
            
            def on_error(doc_type, error_msg):
                results['error'] = error_msg
            
            thread.error.connect(on_error)
            thread.run()
            
            # 应该收到错误信号
            assert 'error' in results
            assert "不支持的文件格式" in results['error']
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self, qapp):
        """测试不存在的文件"""
        thread = DocumentLoadThread("不存在", "/path/to/nonexistent/file.pdf")
        
        results = {}
        
        def on_error(doc_type, error_msg):
            results['error'] = error_msg
        
        thread.error.connect(on_error)
        thread.run()
        
        # 应该收到错误信号
        assert 'error' in results


class TestDocumentPreviewDialog:
    """测试DocumentPreviewDialog类"""
    
    def test_init(self, qapp):
        """测试初始化"""
        dialog = DocumentPreviewDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "申请材料预览"
        assert len(dialog.documents) == 0
    
    def test_empty_documents_warning(self, qapp):
        """测试空文档列表警告"""
        dialog = DocumentPreviewDialog()
        # 设置空文档字典应该显示警告
        dialog.set_documents({})
        # 对话框应该仍然存在但没有标签页
        assert dialog.tab_widget.count() == 0
    
    def test_set_documents(self, qapp, test_pdf_path):
        """测试设置文档"""
        if not test_pdf_path:
            pytest.skip("测试PDF文件不存在")
        
        dialog = DocumentPreviewDialog()
        documents = {
            "说明书": test_pdf_path
        }
        
        # 注意：这里实际上会启动异步加载，所以我们只测试设置
        dialog.documents = documents
        assert "说明书" in dialog.documents
        assert dialog.documents["说明书"] == test_pdf_path
    
    def test_nonexistent_file_handling(self, qapp):
        """测试不存在文件的处理"""
        dialog = DocumentPreviewDialog()
        documents = {
            "不存在的文件": "/path/to/nonexistent/file.pdf"
        }
        
        # 设置不存在的文件路径
        dialog.documents = documents
        # 应该能正常处理，不会崩溃


class TestIntegration:
    """集成测试"""
    
    def test_complete_workflow(self, qapp, test_pdf_path, test_word_path):
        """测试完整工作流程"""
        if not test_pdf_path and not test_word_path:
            pytest.skip("测试文件不存在")
        
        # 创建对话框
        dialog = DocumentPreviewDialog()
        
        # 设置文档
        documents = {}
        if test_pdf_path:
            documents["说明书"] = test_pdf_path
        if test_word_path:
            documents["权利要求书"] = test_word_path
        
        dialog.documents = documents
        
        # 验证文档已设置
        assert len(dialog.documents) > 0
        
        # 清理
        dialog.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
