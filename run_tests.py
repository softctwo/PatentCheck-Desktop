#!/usr/bin/env python3
"""
测试运行脚本
"""
import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("PatentCheck-Desktop 测试套件")
    print("=" * 60)
    print()
    
    # 发现所有测试
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出摘要
    print()
    print("=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"✅ 通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败: {len(result.failures)}")
    print(f"⚠️  错误: {len(result.errors)}")
    print()
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_name):
    """
    运行特定测试
    
    Args:
        test_name: 测试名称，如 'test_core' 或 'test_checkers'
    """
    print(f"运行测试: {test_name}")
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_name}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行指定测试
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # 运行所有测试
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
