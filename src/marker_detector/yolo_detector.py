"""
YOLO标号检测器
使用YOLOv5模型检测专利附图中的标号
"""
import os
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
import cv2
import numpy as np

# 动态导入YOLO相关库
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告: ultralytics未安装，YOLO检测功能将不可用")


class YOLOMarkerDetector:
    """
    YOLO标号检测器
    使用YOLOv5-nano模型检测专利附图中的圆圈标号和箭头
    """
    
    # 模型配置
    DEFAULT_MODEL_PATH = "models/yolov5n_marker.pt"  # 自定义训练的标号检测模型
    FALLBACK_MODEL = "yolov5n.pt"  # 预训练的YOLOv5-nano通用模型
    
    # 检测类别（根据实际训练数据定义）
    CLASSES = {
        0: "circle_marker",  # 圆圈标号
        1: "arrow",          # 指示箭头
        2: "number"          # 数字标记
    }
    
    def __init__(self, model_path: Optional[str] = None, confidence: float = 0.25, device: str = "cpu"):
        """
        初始化YOLO检测器
        
        Args:
            model_path: 模型权重文件路径，None则使用默认路径
            confidence: 检测置信度阈值
            device: 推理设备 ("cpu" 或 "cuda")
        """
        self.available = YOLO_AVAILABLE
        self.confidence = confidence
        self.device = device
        self.model = None
        
        if not self.available:
            print("YOLO检测器不可用")
            return
        
        # 确定模型路径
        if model_path is None:
            # 尝试使用自定义训练的模型
            project_root = Path(__file__).parent.parent.parent
            custom_model = project_root / self.DEFAULT_MODEL_PATH
            
            if custom_model.exists():
                model_path = str(custom_model)
                print(f"使用自定义标号检测模型: {model_path}")
            else:
                # 使用预训练的YOLOv5n作为fallback
                model_path = self.FALLBACK_MODEL
                print(f"自定义模型不存在，使用预训练模型: {model_path}")
        
        # 加载模型
        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"✓ YOLO模型加载成功 (设备: {self.device})")
        except Exception as e:
            print(f"✗ YOLO模型加载失败: {e}")
            self.available = False
    
    def detect_markers(self, image_path: str) -> Dict:
        """
        检测图片中的标号
        
        Args:
            image_path: 图片路径
            
        Returns:
            检测结果字典，包含:
                - detections: 检测到的目标列表
                - circles: 圆圈标号位置
                - arrows: 箭头位置
                - count: 检测到的标号总数
        """
        if not self.available or self.model is None:
            return self._empty_result()
        
        try:
            # 读取图片
            if not os.path.exists(image_path):
                print(f"图片不存在: {image_path}")
                return self._empty_result()
            
            # 使用YOLO进行推理
            results = self.model.predict(
                source=image_path,
                conf=self.confidence,
                device=self.device,
                verbose=False
            )
            
            # 解析结果
            return self._parse_results(results[0], image_path)
            
        except Exception as e:
            print(f"YOLO检测失败 {image_path}: {e}")
            return self._empty_result()
    
    def _parse_results(self, result, image_path: str) -> Dict:
        """
        解析YOLO检测结果
        
        Args:
            result: YOLO检测结果对象
            image_path: 图片路径
            
        Returns:
            解析后的检测结果
        """
        detections = []
        circles = []
        arrows = []
        
        # 获取检测框
        boxes = result.boxes
        
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # 获取置信度和类别
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # 计算中心点和尺寸
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                width = int(x2 - x1)
                height = int(y2 - y1)
                
                detection = {
                    'class_id': cls,
                    'class_name': self.CLASSES.get(cls, f"class_{cls}"),
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': [center_x, center_y],
                    'size': [width, height]
                }
                
                detections.append(detection)
                
                # 按类别分类
                if cls == 0:  # circle_marker
                    circles.append(detection)
                elif cls == 1:  # arrow
                    arrows.append(detection)
        
        return {
            'image_path': image_path,
            'detections': detections,
            'circles': circles,
            'arrows': arrows,
            'count': len(detections),
            'circle_count': len(circles),
            'arrow_count': len(arrows)
        }
    
    def _empty_result(self) -> Dict:
        """返回空检测结果"""
        return {
            'image_path': '',
            'detections': [],
            'circles': [],
            'arrows': [],
            'count': 0,
            'circle_count': 0,
            'arrow_count': 0
        }
    
    def detect_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        批量检测多张图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            检测结果列表
        """
        results = []
        for image_path in image_paths:
            result = self.detect_markers(image_path)
            results.append(result)
        return results
    
    def visualize_detections(self, image_path: str, output_path: Optional[str] = None) -> np.ndarray:
        """
        可视化检测结果
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（可选）
            
        Returns:
            标注后的图片
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # 获取检测结果
        result = self.detect_markers(image_path)
        
        # 绘制检测框
        for detection in result['detections']:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            conf = detection['confidence']
            
            # 不同类别用不同颜色
            if class_name == "circle_marker":
                color = (0, 255, 0)  # 绿色
            elif class_name == "arrow":
                color = (255, 0, 0)  # 蓝色
            else:
                color = (0, 0, 255)  # 红色
            
            # 绘制边界框
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(image, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 保存图片
        if output_path:
            cv2.imwrite(output_path, image)
        
        return image
    
    def get_marker_positions(self, image_path: str) -> List[Tuple[int, int]]:
        """
        获取所有标号的位置
        
        Args:
            image_path: 图片路径
            
        Returns:
            位置列表 [(x, y), ...]
        """
        result = self.detect_markers(image_path)
        positions = [tuple(det['center']) for det in result['detections']]
        return positions


class HybridMarkerDetector:
    """
    混合标号检测器
    结合YOLO检测和OCR识别，提供更准确的标号检测
    """
    
    def __init__(self, use_yolo: bool = True, use_ocr: bool = True):
        """
        初始化混合检测器
        
        Args:
            use_yolo: 是否使用YOLO检测
            use_ocr: 是否使用OCR识别
        """
        self.use_yolo = use_yolo and YOLO_AVAILABLE
        self.use_ocr = use_ocr
        
        # 初始化检测器
        if self.use_yolo:
            self.yolo_detector = YOLOMarkerDetector()
        else:
            self.yolo_detector = None
        
        if self.use_ocr:
            from .ocr_detector import OCRMarkerDetector
            self.ocr_detector = OCRMarkerDetector()
        else:
            self.ocr_detector = None
    
    def detect_markers(self, image_path: str) -> Dict:
        """
        综合检测标号
        
        Args:
            image_path: 图片路径
            
        Returns:
            检测结果字典
        """
        result = {
            'image_path': image_path,
            'yolo_result': None,
            'ocr_markers': set(),
            'detected_markers': set(),
            'marker_positions': [],
            'confidence': 0.0
        }
        
        # YOLO检测
        if self.use_yolo and self.yolo_detector:
            yolo_result = self.yolo_detector.detect_markers(image_path)
            result['yolo_result'] = yolo_result
            result['marker_positions'] = self.yolo_detector.get_marker_positions(image_path)
        
        # OCR识别
        if self.use_ocr and self.ocr_detector:
            ocr_markers = self.ocr_detector.detect_markers_from_image(image_path)
            result['ocr_markers'] = ocr_markers
        
        # 合并结果
        # YOLO提供位置信息，OCR提供数字识别
        result['detected_markers'] = result['ocr_markers']
        
        # 计算置信度
        if result['yolo_result'] and result['yolo_result']['count'] > 0:
            result['confidence'] = 0.8  # YOLO检测到标号
        elif len(result['ocr_markers']) > 0:
            result['confidence'] = 0.6  # 仅OCR识别
        else:
            result['confidence'] = 0.0  # 未检测到
        
        return result
    
    def detect_batch(self, image_paths: List[str]) -> List[Dict]:
        """批量检测"""
        return [self.detect_markers(path) for path in image_paths]
    
    def get_all_markers(self, image_paths: List[str]) -> Set[str]:
        """获取所有图片中的所有标号"""
        all_markers = set()
        for result in self.detect_batch(image_paths):
            all_markers.update(result['detected_markers'])
        return all_markers
