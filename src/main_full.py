"""
PatentCheck-Desktop 完整版主程序
支持实际文件检测
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.models import CheckReport
from src.core.rule_engine import RuleEngine
from src.file_parser.parser import FileParser
from src.structure_checker.checker import StructureChecker
from src.image_checker.checker import ImageChecker
from src.alignment_checker.checker import AlignmentChecker
from src.report_generator.pdf_generator import PDFReportGenerator


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='PatentCheck-Desktop - 专利申请自检工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main_full.py /path/to/patent_folder
  python main_full.py /path/to/specification.docx
  python main_full.py --output report.pdf /path/to/files
        """
    )
    parser.add_argument('path', help='专利文件或文件夹路径')
    parser.add_argument('-o', '--output', default='patent_check_report.pdf',
                       help='输出PDF报告路径 (默认: patent_check_report.pdf)')
    parser.add_argument('-j', '--json', default='patent_check_report.json',
                       help='输出JSON报告路径 (默认: patent_check_report.json)')
    parser.add_argument('--no-pdf', action='store_true',
                       help='不生成PDF报告')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PatentCheck-Desktop V0.9 完整版")
    print("专利自助预审工具")
    print("=" * 60)
    print()
    
    try:
        # 1. 解析文件
        print("📁 正在扫描文件...")
        file_parser = FileParser(args.path)
        document = file_parser.parse()
        
        print(f"   ✓ 找到说明书: {document.specification_path or '无'}")
        print(f"   ✓ 找到附图: {len(document.figures)}张")
        print()
        
        if not document.is_valid():
            print("❌ 错误: 未找到有效的专利文档")
            print("   请确保文件夹中包含说明书(.docx)和附图")
            return 1
        
        # 2. 创建检测报告
        report = CheckReport(document=document)
        
        # 3. 初始化规则引擎
        engine = RuleEngine()
        
        # 4. 注册检查器
        print("🔍 正在执行检查...")
        engine.register_checker(StructureChecker())
        engine.register_checker(ImageChecker())
        engine.register_checker(AlignmentChecker())
        
        # 5. 执行检查
        results = engine.run_checks(document)
        
        # 6. 添加结果到报告
        for result in results:
            report.add_result(result)
        
        print(f"   ✓ 完成检查，共{len(results)}项结果")
        print()
        
        # 7. 打印摘要
        print_summary(report)
        
        # 8. 生成报告
        print("\n📄 正在生成报告...")
        
        # JSON报告
        import json
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"   ✓ JSON报告: {Path(args.json).absolute()}")
        
        # PDF报告
        if not args.no_pdf:
            try:
                pdf_gen = PDFReportGenerator()
                pdf_gen.generate(report, args.output)
                print(f"   ✓ PDF报告: {Path(args.output).absolute()}")
            except Exception as e:
                print(f"   ⚠ PDF生成失败: {e}")
                print("   (JSON报告已成功生成)")
        
        print()
        print("=" * 60)
        print("✨ 检测完成！")
        print("=" * 60)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ 文件未找到: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def print_summary(report: CheckReport):
    """打印检测报告摘要"""
    print("\n📊 检测报告摘要")
    print("-" * 60)
    summary = report.get_summary()
    print(f"  总检查项: {summary['total']}")
    print(f"  🛑 严重错误: {summary['errors']}")
    print(f"  ⚠️  警告: {summary['warnings']}")
    print(f"  ℹ️  提示: {summary['infos']}")
    print(f"  ✅ 通过: {summary['passes']}")
    
    # 打印错误详情
    if summary['errors'] > 0 or summary['warnings'] > 0:
        print("\n⚠️  发现的主要问题：")
        for result in report.results:
            if result.severity.value in ['error', 'warning']:
                icon = "🛑" if result.severity.value == 'error' else "⚠️"
                print(f"  {icon} {result.title}")
                print(f"     位置: {result.location}")


if __name__ == "__main__":
    sys.exit(main())
