#!/usr/bin/env python3
"""
测试修复：多行提示词和PDF中文显示
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.report_generator.pdf_generator import PDFReportGenerator
from src.core.models import CheckReport, CheckResult, CheckCategory, Severity, PatentDocument


def test_pdf_chinese():
    """测试PDF中文字体"""
    print("=" * 70)
    print("测试PDF中文字体支持")
    print("=" * 70)
    
    # 创建测试报告
    document = PatentDocument(
        specification_path=str(Path(__file__).parent / "test_data" / "说明书.docx")
    )
    
    report = CheckReport(document=document)
    
    # 添加测试结果
    report.add_result(CheckResult(
        rule_id="TEST001",
        category=CheckCategory.STRUCTURE,
        severity=Severity.INFO,
        title="测试中文显示",
        description="这是一个测试中文显示的检测结果",
        location="测试位置",
        suggestion="这是改进建议",
        reference="专利法第26条"
    ))
    
    # 添加AI审查结果（包含多行文本）
    report.ai_review_result = """这是AI审查结果测试。

## 一、技术方案分析
1. 技术方案完整性良好
2. 逻辑结构清晰
3. 符合专利法要求

## 二、改进建议
建议在以下方面进行优化：
- 补充技术细节
- 完善实施例说明

## 三、总结
整体方案可行，建议修改后提交。"""
    
    report.ai_review_prompt = "请审查这份专利申请的技术方案完整性和逻辑性\n（这是多行提示词测试）"
    
    # 生成PDF
    output_path = Path(__file__).parent / "test_chinese_pdf_output.pdf"
    
    try:
        print("\n正在生成测试PDF...")
        pdf_gen = PDFReportGenerator()
        pdf_gen.generate(report, str(output_path))
        
        print(f"\n✓ PDF生成成功！")
        print(f"  文件位置: {output_path}")
        print(f"\n💡 请打开PDF文件检查：")
        print(f"   1. 中文是否正常显示（不乱码）")
        print(f"   2. AI审查结果是否包含多行内容")
        print(f"   3. 多行提示词是否正确显示")
        
        return True
        
    except Exception as e:
        print(f"\n✗ PDF生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    success = test_pdf_chinese()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ 测试完成！请检查生成的PDF文件。")
        print("=" * 70)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
