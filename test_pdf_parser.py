#!/usr/bin/env python3
"""
测试PDF专利文档解析功能
"""
import sys
from pathlib import Path

# 添加src到路径
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 设置package路径
import os
os.chdir(Path(__file__).parent)

from src.file_parser.parser import FileParser

def test_pdf_parsing():
    """测试PDF文件解析"""
    print("=" * 70)
    print("PDF专利文档解析测试")
    print("=" * 70)
    print()
    
    # 测试PDF文件路径
    pdf_path = "/Users/zhangyanlong/Patents/实用新型专利授权说明书CN201420398070.2.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"📄 正在解析PDF: {pdf_path}")
    print()
    
    try:
        # 1. 获取PDF信息
        print("1️⃣ PDF文档信息:")
        print("-" * 70)
        pdf_info = FileParser.get_pdf_info(pdf_path)
        print(f"   页数: {pdf_info['page_count']}")
        print(f"   包含图片: {'是' if pdf_info['has_images'] else '否'}")
        if pdf_info['has_images']:
            print(f"   图片分布: {pdf_info['images']}")
        print(f"   元数据: {pdf_info['metadata']}")
        print()
        
        # 2. 提取文本内容
        print("2️⃣ 提取文本内容:")
        print("-" * 70)
        text = FileParser.extract_pdf_text(pdf_path)
        print(f"   文本总长度: {len(text)} 字符")
        print()
        print("   前500字符预览:")
        print("   " + "-" * 66)
        preview = text[:500].replace('\n', '\n   ')
        print(f"   {preview}")
        print("   " + "-" * 66)
        print()
        
        # 3. 识别专利文档结构
        print("3️⃣ 专利文档结构分析:")
        print("-" * 70)
        
        # 检查关键章节
        sections = {
            '技术领域': '技术领域' in text,
            '背景技术': '背景技术' in text,
            '实用新型内容': '实用新型内容' in text or '发明内容' in text,
            '附图说明': '附图说明' in text,
            '具体实施方式': '具体实施方式' in text or '具体实施例' in text,
            '权利要求书': '权利要求' in text,
            '摘要': '摘要' in text
        }
        
        for section, found in sections.items():
            status = "✅" if found else "❌"
            print(f"   {status} {section}")
        print()
        
        # 4. 提取关键信息
        print("4️⃣ 关键信息提取:")
        print("-" * 70)
        
        # 提取专利号
        import re
        patent_no = re.search(r'CN\s*\d+', text)
        if patent_no:
            print(f"   专利号: {patent_no.group()}")
        
        # 提取申请日期
        apply_date = re.search(r'申请日\s*[:\：]?\s*(\d{4}\.\s*\d{2}\.\s*\d{2})', text)
        if apply_date:
            print(f"   申请日: {apply_date.group(1)}")
        
        # 提取专利名称
        title_match = re.search(r'(实用新型|发明)名称\s*[:\：]?\s*(.+)', text)
        if title_match:
            print(f"   专利名称: {title_match.group(2).strip()}")
        
        print()
        
        # 5. 使用FileParser解析
        print("5️⃣ 使用FileParser解析:")
        print("-" * 70)
        parser = FileParser(pdf_path)
        document = parser.parse()
        
        print(f"   说明书路径: {document.specification_path}")
        print(f"   权利要求书路径: {document.claims_path}")
        print(f"   摘要路径: {document.abstract_path}")
        print(f"   附图数量: {len(document.figures)}")
        print()
        
        print("=" * 70)
        print("✅ PDF解析测试完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ 解析错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_parsing()
