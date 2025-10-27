"""
标号检测模块
支持OCR和YOLO两种检测方式
"""
from .ocr_detector import OCRMarkerDetector, HoughCircleDetector, CombinedMarkerDetector

try:
    from .yolo_detector import YOLOMarkerDetector, HybridMarkerDetector
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告: YOLO检测器不可用，请安装ultralytics和torch")

__all__ = [
    'OCRMarkerDetector',
    'HoughCircleDetector', 
    'CombinedMarkerDetector',
    'YOLOMarkerDetector',
    'HybridMarkerDetector',
    'YOLO_AVAILABLE'
]