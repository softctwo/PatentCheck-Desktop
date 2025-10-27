"""
OCR标号检测器
使用Tesseract OCR识别图片中的数字标号
"""
import re
from pathlib import Path
from typing import List, Set, Tuple
from PIL import Image
import cv2
import numpy as np

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("警告: pytesseract未安装，OCR功能将不可用")


class OCRMarkerDetector:
    """OCR标号检测器"""
    
    def __init__(self):
        """初始化OCR检测器"""
        self.tesseract_available = TESSERACT_AVAILABLE
        
        # 标号的正则表达式模式
        # 匹配: 1, 10, 100, 1a, 10a, 100a 等
        self.marker_pattern = re.compile(r'\b(\d+[a-zA-Z]?)\b')
        
    def detect_markers_from_image(self, image_path: str) -> Set[str]:
        """
        从图片中检测标号
        
        Args:
            image_path: 图片路径
            
        Returns:
            检测到的标号集合
        """
        if not self.tesseract_available:
            return set()
        
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                return set()
            
            # 预处理图片以提高OCR准确率
            processed = self._preprocess_image(image)
            
            # 使用Tesseract进行OCR
            # 使用配置: 只识别数字和字母
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            text = pytesseract.image_to_string(processed, config=custom_config)
            
            # 提取标号
            markers = self._extract_markers(text)
            
            return markers
            
        except Exception as e:
            print(f"OCR检测失败 {image_path}: {e}")
            return set()
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图片以提高OCR识别率
        
        Args:
            image: 输入图片
            
        Returns:
            处理后的图片
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # 去噪
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        # 增强对比度
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def _extract_markers(self, text: str) -> Set[str]:
        """
        从OCR文本中提取标号
        
        Args:
            text: OCR识别的文本
            
        Returns:
            标号集合
        """
        markers = set()
        
        # 查找所有匹配的标号
        matches = self.marker_pattern.findall(text)
        
        for match in matches:
            # 过滤掉明显不是标号的数字
            if self._is_valid_marker(match):
                markers.add(match)
        
        return markers
    
    def _is_valid_marker(self, marker: str) -> bool:
        """
        判断是否为有效标号
        
        Args:
            marker: 标号字符串
            
        Returns:
            是否有效
        """
        # 提取数字部分
        num_part = re.match(r'(\d+)', marker)
        if not num_part:
            return False
        
        num = int(num_part.group(1))
        
        # 标号通常在1-999范围内
        # 过滤掉年份(>1900)等明显不是标号的数字
        if num < 1 or num > 999:
            return False
        
        # 过滤掉看起来像年份的数字
        if num >= 1900 and num <= 2100:
            return False
        
        return True
    
    def detect_markers_batch(self, image_paths: List[str]) -> dict:
        """
        批量检测多张图片的标号
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            {图片路径: 标号集合}
        """
        results = {}
        
        for path in image_paths:
            markers = self.detect_markers_from_image(path)
            if markers:
                results[path] = markers
        
        return results
    
    def get_all_markers(self, image_paths: List[str]) -> Set[str]:
        """
        获取所有图片中的所有标号
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            所有标号的集合
        """
        all_markers = set()
        
        batch_results = self.detect_markers_batch(image_paths)
        for markers in batch_results.values():
            all_markers.update(markers)
        
        return all_markers


class HoughCircleDetector:
    """霍夫圆检测器 - 检测图中的圆形标注"""
    
    def __init__(self):
        """初始化霍夫圆检测器"""
        pass
    
    def detect_circles(self, image_path: str) -> List[Tuple[int, int, int]]:
        """
        检测图片中的圆形标注
        
        Args:
            image_path: 图片路径
            
        Returns:
            圆形列表 [(x, y, radius), ...]
        """
        try:
            # 读取图片
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return []
            
            # 使用霍夫圆变换检测圆
            circles = cv2.HoughCircles(
                image,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=5,
                maxRadius=50
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                return [(x, y, r) for x, y, r in circles[0, :]]
            
            return []
            
        except Exception as e:
            print(f"霍夫圆检测失败 {image_path}: {e}")
            return []
    
    def count_circles(self, image_path: str) -> int:
        """
        统计图片中的圆形标注数量
        
        Args:
            image_path: 图片路径
            
        Returns:
            圆形数量
        """
        circles = self.detect_circles(image_path)
        return len(circles)


# 组合检测器：OCR + 霍夫圆
class CombinedMarkerDetector:
    """组合标号检测器：OCR识别 + 霍夫圆检测"""
    
    def __init__(self):
        """初始化组合检测器"""
        self.ocr_detector = OCRMarkerDetector()
        self.circle_detector = HoughCircleDetector()
    
    def detect_markers(self, image_path: str) -> dict:
        """
        综合检测图片中的标号
        
        Args:
            image_path: 图片路径
            
        Returns:
            检测结果字典
        """
        result = {
            'image_path': image_path,
            'ocr_markers': set(),
            'circle_count': 0,
            'markers': set()
        }
        
        # OCR检测
        ocr_markers = self.ocr_detector.detect_markers_from_image(image_path)
        result['ocr_markers'] = ocr_markers
        
        # 霍夫圆检测
        circle_count = self.circle_detector.count_circles(image_path)
        result['circle_count'] = circle_count
        
        # 合并结果（优先使用OCR结果）
        result['markers'] = ocr_markers
        
        return result
