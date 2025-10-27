#!/usr/bin/env python3
"""
AI审查功能测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_reviewer.reviewer import AIReviewer
from src.ai_reviewer.deepseek_client import DeepSeekClient


def test_api_connection():
    """测试API连接"""
    print("=" * 60)
    print("测试1: DeepSeek API连接测试")
    print("=" * 60)
    
    try:
        client = DeepSeekClient()
        print("✓ DeepSeek客户端初始化成功")
        
        # 测试连接
        result = client.test_connection()
        if result:
            print("✓ API连接成功！")
            return True
        else:
            print("✗ API连接失败")
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_preset_prompts():
    """测试预设提示词"""
    print("\n" + "=" * 60)
    print("测试2: 预设提示词")
    print("=" * 60)
    
    reviewer = AIReviewer()
    prompts = reviewer.get_preset_prompts()
    
    print(f"预设提示词数量: {len(prompts)}")
    for i, prompt in enumerate(prompts, 1):
        print(f"  {i}. {prompt}")
    
    return True


def test_simple_review():
    """测试简单的AI审查"""
    print("\n" + "=" * 60)
    print("测试3: 简单AI审查测试")
    print("=" * 60)
    
    try:
        client = DeepSeekClient()
        
        # 测试简单对话
        print("发送测试消息: '你好，请简短介绍一下你自己'")
        response = client.simple_chat("你好，请简短介绍一下你自己（请用不超过50字回答）")
        
        print(f"\nAI回复:\n{response}")
        print("\n✓ 简单审查测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_document_extraction():
    """测试文档提取功能"""
    print("\n" + "=" * 60)
    print("测试4: 文档提取功能")
    print("=" * 60)
    
    # 查找测试数据
    test_data_dir = Path(__file__).parent / "test_data"
    
    if not test_data_dir.exists():
        print(f"ℹ️  测试数据目录不存在: {test_data_dir}")
        print("   跳过文档提取测试")
        return True
    
    reviewer = AIReviewer()
    
    # 查找Word或PDF文件
    doc_files = list(test_data_dir.glob("*.docx")) + list(test_data_dir.glob("*.pdf"))
    
    if not doc_files:
        print("ℹ️  未找到测试文档文件 (.docx 或 .pdf)")
        print("   跳过文档提取测试")
        return True
    
    test_file = doc_files[0]
    print(f"使用测试文件: {test_file.name}")
    
    try:
        text = reviewer.extract_document_text(str(test_file))
        print(f"✓ 成功提取文档内容，长度: {len(text)} 字符")
        print(f"前100字符预览: {text[:100]}...")
        return True
    except Exception as e:
        print(f"✗ 文档提取失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n🤖 PatentCheck-Desktop AI审查功能测试")
    print("=" * 60)
    
    results = []
    
    # 执行测试
    results.append(("API连接", test_api_connection()))
    results.append(("预设提示词", test_preset_prompts()))
    results.append(("简单AI审查", test_simple_review()))
    results.append(("文档提取", test_document_extraction()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI审查功能已准备就绪。")
        return 0
    else:
        print("⚠️  部分测试未通过，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
