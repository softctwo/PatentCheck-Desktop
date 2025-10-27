#!/usr/bin/env python3
"""
完整的AI审查功能端到端测试
模拟真实使用场景
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_reviewer.reviewer import AIReviewer


def test_full_patent_review():
    """测试完整的专利文档AI审查流程"""
    print("=" * 70)
    print("🤖 完整专利文档AI审查测试")
    print("=" * 70)
    
    # 使用测试数据
    test_doc = Path(__file__).parent / "test_data" / "说明书.docx"
    
    if not test_doc.exists():
        print(f"✗ 测试文档不存在: {test_doc}")
        return False
    
    print(f"\n📄 测试文档: {test_doc.name}")
    print("-" * 70)
    
    reviewer = AIReviewer()
    
    # 使用所有4个预设提示词进行测试
    prompts = reviewer.get_preset_prompts()
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n【测试 {i}/4】")
        print(f"提示词: {prompt}")
        print("-" * 70)
        
        try:
            print("⏳ 正在调用AI进行审查...")
            result = reviewer.review_patent(str(test_doc), prompt)
            
            print(f"\n✓ 审查完成！\n")
            print("审查结果:")
            print("┌" + "─" * 68 + "┐")
            
            # 格式化输出结果
            lines = result.split('\n')
            for line in lines[:15]:  # 只显示前15行
                # 确保行不超过66个字符（考虑边框）
                if len(line) > 66:
                    line = line[:63] + "..."
                print(f"│ {line:<66} │")
            
            if len(lines) > 15:
                print(f"│ {'...(共' + str(len(lines)) + '行，此处省略)':<66} │")
            
            print("└" + "─" * 68 + "┘")
            
            # 短暂延迟，避免API限流
            if i < len(prompts):
                print("\n⏸  等待2秒后进行下一项测试...\n")
                import time
                time.sleep(2)
            
        except Exception as e:
            print(f"\n✗ 审查失败: {e}")
            return False
    
    print("\n" + "=" * 70)
    print("🎉 所有4项AI审查测试均成功完成！")
    print("=" * 70)
    
    return True


def main():
    """主函数"""
    try:
        success = test_full_patent_review()
        
        if success:
            print("\n✅ 测试结论: AI审查功能运行正常，可以在GUI中使用了！")
            print("\n💡 下一步:")
            print("   1. 运行GUI程序: python src/gui/main_window.py")
            print("   2. 选择 test_data 文件夹")
            print("   3. 执行检测后，尝试AI审查功能")
            return 0
        else:
            print("\n⚠️  部分测试未通过")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
