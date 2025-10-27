"""
PatentCheck-Desktop 主程序入口
V0.9 MVP - 简化版演示
"""
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core.models import PatentDocument, CheckReport, CheckResult, Severity, CheckCategory
from core.rule_engine import RuleEngine


def demo_check():
    """演示检测功能"""
    print("=" * 60)
    print("PatentCheck-Desktop V0.9 MVP")
    print("专利自助预审工具（演示版）")
    print("=" * 60)
    print()
    
    # 创建测试文档
    document = PatentDocument(
        specification_path="/path/to/spec.docx",
        figures=["fig1.jpg", "fig2.jpg", "fig3.jpg"]
    )
    
    # 创建检测报告
    report = CheckReport(document=document)
    
    # 模拟添加一些检查结果
    results = [
        CheckResult(
            rule_id="R001",
            category=CheckCategory.STRUCTURE,
            severity=Severity.ERROR,
            title="缺少技术领域章节",
            description="说明书必须包含'技术领域'章节",
            location="说明书",
            suggestion="请在说明书开头添加'技术领域'章节",
            reference="专利法实施细则第18条"
        ),
        CheckResult(
            rule_id="R002",
            category=CheckCategory.IMAGE_FORMAT,
            severity=Severity.WARNING,
            title="附图分辨率过低",
            description="附图1分辨率为150dpi，低于要求的200dpi",
            location="附图/图1.jpg",
            suggestion="请提高图片分辨率至200dpi以上",
            reference="专利审查指南第一部分第一章5.2节"
        ),
        CheckResult(
            rule_id="R003",
            category=CheckCategory.IMAGE_FORMAT,
            severity=Severity.ERROR,
            title="附图包含彩色像素",
            description="附图2检测到34%彩色像素",
            location="附图/图2.jpg",
            suggestion="请转换为纯黑白线条图",
            reference="专利法实施细则第17条"
        ),
        CheckResult(
            rule_id="R004",
            category=CheckCategory.ALIGNMENT,
            severity=Severity.WARNING,
            title="标号15未在说明书出现",
            description="图中标记15，但说明书中缺少相应解释",
            location="附图3 + 说明书第8页",
            suggestion="请在说明书中补充标号15的说明",
            reference="专利审查指南"
        ),
        CheckResult(
            rule_id="R005",
            category=CheckCategory.STRUCTURE,
            severity=Severity.PASS,
            title="说明书结构完整",
            description="说明书包含所有必需章节",
            location="说明书",
            suggestion=None,
            reference=None
        )
    ]
    
    # 添加到报告
    for result in results:
        report.add_result(result)
    
    # 打印报告
    print("\n📊 检测报告摘要")
    print("-" * 60)
    summary = report.get_summary()
    print(f"  总检查项: {summary['total']}")
    print(f"  🛑 严重错误: {summary['errors']}")
    print(f"  ⚠️  警告: {summary['warnings']}")
    print(f"  ℹ️  提示: {summary['infos']}")
    print(f"  ✅ 通过: {summary['passes']}")
    print()
    
    # 打印详细结果
    print("\n📝 检测详情")
    print("=" * 60)
    
    for i, result in enumerate(report.results, 1):
        severity_icon = {
            Severity.ERROR: "🛑",
            Severity.WARNING: "⚠️",
            Severity.INFO: "ℹ️",
            Severity.PASS: "✅"
        }
        
        print(f"\n{i}. {severity_icon[result.severity]} [{result.severity.value.upper()}] {result.title}")
        print(f"   类别: {result.category.value}")
        print(f"   位置: {result.location}")
        print(f"   描述: {result.description}")
        if result.suggestion:
            print(f"   建议: {result.suggestion}")
        if result.reference:
            print(f"   参考: {result.reference}")
    
    print("\n" + "=" * 60)
    print("✨ 检测完成！")
    print("\n💡 提示:")
    print("  - 这是V0.9 MVP演示版本")
    print("  - 实际版本将支持拖入文件检测")
    print("  - 将生成PDF格式的检测报告")
    print("=" * 60)
    
    return report


def main():
    """主函数"""
    try:
        report = demo_check()
        
        # 可选：保存为JSON
        import json
        output_path = Path("check_report.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n📄 报告已保存到: {output_path.absolute()}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
