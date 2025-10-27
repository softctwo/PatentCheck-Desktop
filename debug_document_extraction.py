#!/usr/bin/env python3
"""
调试文档提取 - 检查文档内容是否正确提取
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ai_reviewer.reviewer import AIReviewer


def main():
    print("=" * 70)
    print("调试：检查文档内容提取")
    print("=" * 70)
    
    test_doc = Path(__file__).parent / "test_data" / "说明书.docx"
    
    if not test_doc.exists():
        print(f"✗ 测试文档不存在: {test_doc}")
        return 1
    
    print(f"\n📄 测试文档: {test_doc.name}")
    print("-" * 70)
    
    try:
        reviewer = AIReviewer()
        
        # 提取文档内容
        print("\n⏳ 正在提取文档内容...")
        content = reviewer.extract_document_text(str(test_doc))
        
        print(f"\n✓ 文档内容提取成功！")
        print(f"文档长度: {len(content)} 字符")
        print("\n" + "=" * 70)
        print("文档内容预览：")
        print("=" * 70)
        print(content)
        print("=" * 70)
        
        # 测试review_with_prompt方法组装的完整消息
        print("\n\n" + "=" * 70)
        print("测试：组装给DeepSeek的完整消息")
        print("=" * 70)
        
        from src.ai_reviewer.deepseek_client import DeepSeekClient
        client = DeepSeekClient()
        
        prompt = "请审查这份专利申请的技术方案完整性和逻辑性"
        
        # 手动组装消息（模拟review_with_prompt）
        system_prompt = (
            "你是一个专业的专利审查助手，擅长分析专利申请文档。"
            "请基于用户的要求，对提供的专利文档进行专业、详细的审查分析。"
            "你的分析应该包括：问题识别、改进建议、法律风险提示等。"
            "请使用清晰、结构化的中文进行回答。"
        )
        
        user_message = f"""请根据以下要求审查这份专利申请文档：

审查要求：
{prompt}

专利文档内容：
{content}

请提供专业的审查意见。"""
        
        print(f"\n系统提示词长度: {len(system_prompt)} 字符")
        print(f"用户消息长度: {len(user_message)} 字符")
        print(f"总计: {len(system_prompt) + len(user_message)} 字符")
        
        print("\n用户消息内容预览（前500字符）：")
        print("-" * 70)
        print(user_message[:500] + "...")
        print("-" * 70)
        
        print("\n✅ 调试信息输出完成！")
        print("\n💡 分析：")
        print(f"   - 如果文档内容很短（{len(content)}字符），可能是文档解析不完整")
        print(f"   - 如果文档内容为空或很少，AI会回复要求提供文档")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
