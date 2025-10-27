"""
测试YOLO标号检测器
"""
import sys
import os
from pathlib import Path
import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.marker_detector import YOLO_AVAILABLE

# 仅在YOLO可用时导入
if YOLO_AVAILABLE:
    from src.marker_detector.yolo_detector import (
        YOLOMarkerDetector,
        HybridMarkerDetector
    )


@pytest.fixture
def test_image_path():
    """测试图片路径"""
    test_images = [
        project_root / "test_data" / "图1.png",
        project_root / "test_data" / "图2.jpg"
    ]
    
    for img_path in test_images:
        if img_path.exists():
            return str(img_path)
    
    return None


@pytest.mark.skipif(not YOLO_AVAILABLE, reason="YOLO不可用")
class TestYOLOMarkerDetector:
    """测试YOLO标号检测器"""
    
    def test_init_without_model(self):
        """测试初始化（无自定义模型）"""
        detector = YOLOMarkerDetector()
        assert detector is not None
        # 注意：没有自定义模型时会使用预训练模型，可能仍然可用
    
    def test_detect_markers_with_image(self, test_image_path):
        """测试检测标号"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = YOLOMarkerDetector()
        result = detector.detect_markers(test_image_path)
        
        # 验证结果结构
        assert 'image_path' in result
        assert 'detections' in result
        assert 'circles' in result
        assert 'arrows' in result
        assert 'count' in result
        assert isinstance(result['detections'], list)
    
    def test_detect_markers_nonexistent_file(self):
        """测试检测不存在的文件"""
        detector = YOLOMarkerDetector()
        result = detector.detect_markers("/nonexistent/image.jpg")
        
        # 应该返回空结果
        assert result['count'] == 0
        assert len(result['detections']) == 0
    
    def test_detect_batch(self, test_image_path):
        """测试批量检测"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = YOLOMarkerDetector()
        image_paths = [test_image_path] * 2  # 重复同一张图片
        
        results = detector.detect_batch(image_paths)
        
        assert len(results) == 2
        assert all('detections' in r for r in results)
    
    def test_get_marker_positions(self, test_image_path):
        """测试获取标号位置"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = YOLOMarkerDetector()
        positions = detector.get_marker_positions(test_image_path)
        
        assert isinstance(positions, list)
        # 每个位置应该是(x, y)元组
        for pos in positions:
            assert len(pos) == 2
            assert isinstance(pos[0], (int, float))
            assert isinstance(pos[1], (int, float))
    
    def test_visualize_detections(self, test_image_path):
        """测试可视化检测结果"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = YOLOMarkerDetector()
        
        # 不保存到文件，仅返回图像
        result_image = detector.visualize_detections(test_image_path)
        
        # 可能返回None（如果图片无法读取）或numpy数组
        assert result_image is None or hasattr(result_image, 'shape')
    
    def test_confidence_threshold(self, test_image_path):
        """测试置信度阈值设置"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        # 高置信度阈值
        detector_high = YOLOMarkerDetector(confidence=0.9)
        result_high = detector_high.detect_markers(test_image_path)
        
        # 低置信度阈值
        detector_low = YOLOMarkerDetector(confidence=0.1)
        result_low = detector_low.detect_markers(test_image_path)
        
        # 低阈值应该检测到更多或相同数量的对象
        assert result_low['count'] >= result_high['count']


@pytest.mark.skipif(not YOLO_AVAILABLE, reason="YOLO不可用")
class TestHybridMarkerDetector:
    """测试混合标号检测器"""
    
    def test_init(self):
        """测试初始化"""
        detector = HybridMarkerDetector()
        assert detector is not None
        assert hasattr(detector, 'yolo_detector')
        assert hasattr(detector, 'ocr_detector')
    
    def test_init_yolo_only(self):
        """测试仅使用YOLO"""
        detector = HybridMarkerDetector(use_yolo=True, use_ocr=False)
        assert detector.yolo_detector is not None
        assert detector.ocr_detector is None
    
    def test_init_ocr_only(self):
        """测试仅使用OCR"""
        detector = HybridMarkerDetector(use_yolo=False, use_ocr=True)
        assert detector.yolo_detector is None
        assert detector.ocr_detector is not None
    
    def test_detect_markers_hybrid(self, test_image_path):
        """测试混合检测"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = HybridMarkerDetector()
        result = detector.detect_markers(test_image_path)
        
        # 验证结果结构
        assert 'image_path' in result
        assert 'yolo_result' in result
        assert 'ocr_markers' in result
        assert 'detected_markers' in result
        assert 'marker_positions' in result
        assert 'confidence' in result
        
        # 置信度应该在0-1之间
        assert 0 <= result['confidence'] <= 1
    
    def test_detect_batch_hybrid(self, test_image_path):
        """测试混合批量检测"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = HybridMarkerDetector()
        image_paths = [test_image_path]
        
        results = detector.detect_batch(image_paths)
        
        assert len(results) == 1
        assert 'detected_markers' in results[0]
    
    def test_get_all_markers(self, test_image_path):
        """测试获取所有标号"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        detector = HybridMarkerDetector()
        image_paths = [test_image_path]
        
        all_markers = detector.get_all_markers(image_paths)
        
        assert isinstance(all_markers, set)
        # 标号应该是字符串
        for marker in all_markers:
            assert isinstance(marker, str)


class TestYOLOAvailability:
    """测试YOLO可用性检查"""
    
    def test_yolo_available_flag(self):
        """测试YOLO_AVAILABLE标志"""
        assert isinstance(YOLO_AVAILABLE, bool)
    
    def test_import_graceful_failure(self):
        """测试导入失败时的优雅处理"""
        # 这个测试验证即使YOLO不可用，模块仍可导入
        from src.marker_detector import YOLO_AVAILABLE
        
        if not YOLO_AVAILABLE:
            # 如果YOLO不可用，不应该能导入YOLO相关类
            with pytest.raises(ImportError):
                from src.marker_detector.yolo_detector import YOLOMarkerDetector


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.skipif(not YOLO_AVAILABLE, reason="YOLO不可用")
    def test_full_workflow(self, test_image_path):
        """测试完整工作流"""
        if not test_image_path:
            pytest.skip("测试图片不存在")
        
        # 1. 创建混合检测器
        detector = HybridMarkerDetector(use_yolo=True, use_ocr=True)
        
        # 2. 检测标号
        result = detector.detect_markers(test_image_path)
        
        # 3. 验证结果
        assert result is not None
        assert 'detected_markers' in result
        
        # 4. 获取所有标号
        all_markers = detector.get_all_markers([test_image_path])
        assert isinstance(all_markers, set)
        
        print(f"\n检测到的标号: {all_markers}")
        print(f"置信度: {result['confidence']}")
        print(f"YOLO检测数量: {result['yolo_result']['count'] if result['yolo_result'] else 0}")
        print(f"OCR识别数量: {len(result['ocr_markers'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
