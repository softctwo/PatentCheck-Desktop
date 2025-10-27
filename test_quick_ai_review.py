#!/usr/bin/env python3
"""
快速AI审查测试 - 只测试一个提示词
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ai_reviewer.reviewer import AIReviewer


def main():
    print("=" * 70)
    print("🤖 快速AI审查功能测试")
    print("=" * 70)
    
    test_doc = Path(__file__).parent / "test_data" / "说明书.docx"
    
    if not test_doc.exists():
        print(f"✗ 测试文档不存在: {test_doc}")
        return 1
    
    print(f"\n📄 测试文档: {test_doc.name}")
    print(f"提示词: 请审查这份专利申请的技术方案完整性和逻辑性")
    print("-" * 70)
    
    try:
        reviewer = AIReviewer()
        print("\n⏳ 正在调用AI进行审查...\n")
        
        result = reviewer.review_patent(
            str(test_doc), 
            "请审查这份专利申请的技术方案完整性和逻辑性"
        )
        
        print("✓ 审查完成！\n")
        print("=" * 70)
        print("审查结果:")
        print("=" * 70)
        print(result)
        print("=" * 70)
        
        print("\n✅ 测试成功！AI审查功能运行正常。")
        print("\n💡 现在可以启动GUI进行完整测试:")
        print("   python src/gui/main_window.py")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 审查失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
