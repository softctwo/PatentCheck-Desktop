#!/usr/bin/env python3
"""测试PDF文档验证"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.file_parser.parser import FileParser
from src.core.models import PatentDocument

def test_validation():
    pdf_path = "/Users/zhangyanlong/Patents/实用新型专利授权说明书CN201420398070.2.pdf"
    
    print("=" * 70)
    print("测试PDF文档验证")
    print("=" * 70)
    print()
    
    # 测试1: 直接创建PatentDocument
    print("1️⃣ 直接创建PatentDocument对象:")
    doc1 = PatentDocument(specification_path=pdf_path)
    print(f"   specification_path: {doc1.specification_path}")
    print(f"   figures: {doc1.figures}")
    print(f"   is_valid(): {doc1.is_valid()}")
    print()
    
    # 测试2: 使用FileParser解析
    print("2️⃣ 使用FileParser解析:")
    parser = FileParser(pdf_path)
    doc2 = parser.parse()
    print(f"   specification_path: {doc2.specification_path}")
    print(f"   claims_path: {doc2.claims_path}")
    print(f"   abstract_path: {doc2.abstract_path}")
    print(f"   figures: {doc2.figures}")
    print(f"   is_valid(): {doc2.is_valid()}")
    print()
    
    if doc2.is_valid():
        print("✅ 验证通过！文档有效")
    else:
        print("❌ 验证失败！文档无效")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    test_validation()
