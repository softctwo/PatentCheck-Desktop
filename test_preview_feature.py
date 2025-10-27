#!/usr/bin/env python3
"""
快速验证文档预览功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.gui.document_preview_dialog import DocumentPreviewDialog


def test_preview_dialog():
    """测试预览对话框"""
    print("=" * 50)
    print("文档预览功能验证")
    print("=" * 50)
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 准备测试文档
    test_docs = {}
    
    # 查找测试文件
    test_pdf = project_root / "test_chinese_pdf_output.pdf"
    test_word = project_root / "test_data" / "说明书.docx"
    test_word2 = project_root / "test_data" / "说明书_完整版.docx"
    
    if test_pdf.exists():
        test_docs["测试PDF文档"] = str(test_pdf)
        print(f"✓ 找到测试PDF: {test_pdf.name}")
    else:
        print(f"✗ 未找到测试PDF: {test_pdf}")
    
    if test_word.exists():
        test_docs["测试Word文档"] = str(test_word)
        print(f"✓ 找到测试Word: {test_word.name}")
    elif test_word2.exists():
        test_docs["测试Word文档"] = str(test_word2)
        print(f"✓ 找到测试Word: {test_word2.name}")
    else:
        print(f"✗ 未找到测试Word文档")
    
    if not test_docs:
        print("\n❌ 没有找到测试文档，无法测试")
        print("请确保以下文件存在:")
        print(f"  - {test_pdf}")
        print(f"  - {test_word}")
        return 1
    
    print(f"\n共找到 {len(test_docs)} 个测试文档")
    print("\n正在打开预览对话框...")
    print("提示：")
    print("  - 可以在标签页之间切换")
    print("  - 可以使用翻页按钮浏览多页文档")
    print("  - 可以使用缩放按钮调整显示大小")
    print("  - 关闭对话框完成测试")
    print("=" * 50)
    
    # 创建并显示预览对话框
    dialog = DocumentPreviewDialog()
    dialog.set_documents(test_docs)
    
    # 显示对话框
    result = dialog.exec()
    
    print("\n✓ 预览对话框已关闭")
    print("=" * 50)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = test_preview_dialog()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
