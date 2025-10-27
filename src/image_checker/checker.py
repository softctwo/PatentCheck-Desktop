"""
附图格式检查器
"""
from typing import List
import numpy as np
from PIL import Image

from ..core.models import CheckResult, PatentDocument, CheckCategory, Severity
from ..core.rule_engine import BaseChecker


class ImageChecker(BaseChecker):
    """附图格式检查器"""
    
    MIN_DPI = 200  # 最低分辨率要求
    COLOR_THRESHOLD = 0.05  # 彩色像素阈值（5%）
    
    def __init__(self, config: dict = None):
        super().__init__(config or {'enabled': True})
    
    def check(self, document: PatentDocument) -> List[CheckResult]:
        """检查附图格式"""
        results = []
        
        if not document.figures:
            results.append(CheckResult(
                rule_id="I000",
                category=CheckCategory.IMAGE_FORMAT,
                severity=Severity.WARNING,
                title="未找到附图",
                description="专利申请通常需要附图",
                location="文件夹"
            ))
            return results
        
        # 检查每张图片
        for i, fig_path in enumerate(document.figures, 1):
            try:
                from ..file_parser.parser import FileParser
                img = FileParser.load_image(fig_path)
                info = FileParser.get_image_info(img)
                
                # 检查分辨率
                dpi = info['dpi'][0] if isinstance(info['dpi'], tuple) else info['dpi']
                if dpi < self.MIN_DPI:
                    results.append(CheckResult(
                        rule_id="I001",
                        category=CheckCategory.IMAGE_FORMAT,
                        severity=Severity.WARNING,
                        title=f"附图{i}分辨率过低",
                        description=f"当前分辨率为{dpi}dpi，低于要求的{self.MIN_DPI}dpi",
                        location=fig_path,
                        suggestion=f"请提高图片分辨率至{self.MIN_DPI}dpi以上",
                        reference="专利审查指南第一部分第一章5.2节"
                    ))
                
                # 检查彩色像素
                if info['mode'] in ['RGB', 'RGBA']:
                    color_ratio = self._check_color_pixels(img)
                    if color_ratio > self.COLOR_THRESHOLD:
                        results.append(CheckResult(
                            rule_id="I002",
                            category=CheckCategory.IMAGE_FORMAT,
                            severity=Severity.ERROR,
                            title=f"附图{i}包含彩色像素",
                            description=f"检测到{color_ratio*100:.1f}%彩色像素",
                            location=fig_path,
                            suggestion="请转换为纯黑白线条图",
                            reference="专利法实施细则第17条"
                        ))
                    else:
                        results.append(CheckResult(
                            rule_id="I003",
                            category=CheckCategory.IMAGE_FORMAT,
                            severity=Severity.PASS,
                            title=f"附图{i}格式正确",
                            description=f"附图为黑白图，分辨率{dpi}dpi",
                            location=fig_path
                        ))
                
            except Exception as e:
                results.append(CheckResult(
                    rule_id="I004",
                    category=CheckCategory.IMAGE_FORMAT,
                    severity=Severity.ERROR,
                    title=f"无法检查附图{i}",
                    description=f"读取图片时发生错误: {str(e)}",
                    location=fig_path
                ))
        
        return results
    
    def _check_color_pixels(self, img: Image.Image) -> float:
        """
        检查彩色像素比例
        
        Returns:
            彩色像素占比 (0.0-1.0)
        """
        # 转换为numpy数组
        img_array = np.array(img)
        
        if len(img_array.shape) < 3:
            return 0.0  # 灰度图
        
        # 检查RGB三个通道是否相同
        # 如果R=G=B，则为灰度；否则为彩色
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # 允许小的差异（容忍度为5）
        tolerance = 5
        is_gray = (np.abs(r - g) <= tolerance) & (np.abs(g - b) <= tolerance)
        
        color_pixels = np.sum(~is_gray)
        total_pixels = r.size
        
        return color_pixels / total_pixels
