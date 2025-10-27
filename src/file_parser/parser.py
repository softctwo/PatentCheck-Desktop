"""
文件解析模块 - 识别和解析专利文档
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple
from docx import Document
from PIL import Image
import pymupdf  # PyMuPDF for PDF parsing
import pytesseract  # OCR for text extraction from images
import io

from ..core.models import PatentDocument


class FileParser:
    """文件解析器"""
    
    SUPPORTED_DOC_FORMATS = ['.docx']
    SUPPORTED_PDF_FORMATS = ['.pdf']
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']
    
    def __init__(self, base_path: str):
        """
        初始化文件解析器
        
        Args:
            base_path: 文件或文件夹路径
        """
        self.base_path = Path(base_path)
        
    def parse(self) -> PatentDocument:
        """
        解析文件，返回专利文档对象
        
        Returns:
            PatentDocument对象
        """
        document = PatentDocument()
        
        if self.base_path.is_file():
            # 单个文件
            self._process_file(self.base_path, document)
        elif self.base_path.is_dir():
            # 文件夹
            self._scan_directory(self.base_path, document)
        else:
            raise ValueError(f"路径不存在: {self.base_path}")
        
        return document
    
    def _scan_directory(self, directory: Path, document: PatentDocument):
        """扫描目录，识别文件"""
        for file_path in directory.iterdir():
            if file_path.is_file():
                self._process_file(file_path, document)
            elif file_path.is_dir():
                # 递归扫描子目录
                self._scan_directory(file_path, document)
    
    def _process_file(self, file_path: Path, document: PatentDocument):
        """处理单个文件"""
        ext = file_path.suffix.lower()
        
        # PDF文档
        if ext in self.SUPPORTED_PDF_FORMATS:
            if self._is_specification(file_path):
                document.specification_path = str(file_path)
            elif self._is_claims(file_path):
                document.claims_path = str(file_path)
            elif self._is_abstract(file_path):
                document.abstract_path = str(file_path)
        
        # Word文档
        elif ext in self.SUPPORTED_DOC_FORMATS:
            if self._is_specification(file_path):
                document.specification_path = str(file_path)
            elif self._is_claims(file_path):
                document.claims_path = str(file_path)
            elif self._is_abstract(file_path):
                document.abstract_path = str(file_path)
        
        # 图片文件
        elif ext in self.SUPPORTED_IMAGE_FORMATS:
            document.figures.append(str(file_path))
    
    def _is_specification(self, file_path: Path) -> bool:
        """判断是否为说明书"""
        name_lower = file_path.stem.lower()
        keywords = ['说明书', 'specification', 'spec', '发明']
        return any(kw in name_lower for kw in keywords)
    
    def _is_claims(self, file_path: Path) -> bool:
        """判断是否为权利要求书"""
        name_lower = file_path.stem.lower()
        keywords = ['权利要求', 'claims', 'claim']
        return any(kw in name_lower for kw in keywords)
    
    def _is_abstract(self, file_path: Path) -> bool:
        """判断是否为摘要"""
        name_lower = file_path.stem.lower()
        keywords = ['摘要', 'abstract']
        return any(kw in name_lower for kw in keywords)
    
    @staticmethod
    def load_word_document(file_path: str) -> Document:
        """
        加载Word文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            Document对象
        """
        try:
            return Document(file_path)
        except Exception as e:
            raise ValueError(f"无法打开Word文档 {file_path}: {e}")
    
    @staticmethod
    def load_image(file_path: str) -> Image.Image:
        """
        加载图片
        
        Args:
            file_path: 文件路径
            
        Returns:
            PIL Image对象
        """
        try:
            return Image.open(file_path)
        except Exception as e:
            raise ValueError(f"无法打开图片 {file_path}: {e}")
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """
        获取图片信息
        
        Args:
            image: PIL Image对象
            
        Returns:
            图片信息字典
        """
        info = {
            'size': image.size,  # (width, height)
            'mode': image.mode,  # RGB, L, RGBA等
            'format': image.format,
            'dpi': image.info.get('dpi', (72, 72))  # 默认72dpi
        }
        return info
    
    @staticmethod
    def load_pdf_document(file_path: str) -> pymupdf.Document:
        """
        加载PDF文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            PyMuPDF Document对象
        """
        try:
            return pymupdf.open(file_path)
        except Exception as e:
            raise ValueError(f"无法打开PDF文档 {file_path}: {e}")
    
    @staticmethod
    def extract_pdf_text(file_path: str, use_ocr: bool = True) -> str:
        """
        提取PDF文本内容，支持OCR
        
        Args:
            file_path: PDF文件路径
            use_ocr: 是否使用OCR提取图片中的文字（当直接提取为空时）
            
        Returns:
            提取的文本内容
        """
        try:
            doc = pymupdf.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 尝试直接提取文本
                page_text = page.get_text()
                
                # 如果文本为空且启用OCR，则使用OCR提取
                if not page_text.strip() and use_ocr:
                    # 将页面转换为图片
                    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # 2x放大提高OCR精度
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # 使用OCR提取文字（中英文）
                    page_text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                
                text += page_text + "\n"
            
            doc.close()
            return text
        except Exception as e:
            raise ValueError(f"无法提取PDF文本 {file_path}: {e}")
    
    @staticmethod
    def get_pdf_info(file_path: str) -> dict:
        """
        获取PDF文档信息
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            PDF信息字典
        """
        try:
            doc = pymupdf.open(file_path)
            info = {
                'page_count': doc.page_count,
                'metadata': doc.metadata,
                'has_images': False,
                'images': []
            }
            
            # 检查是否包含图片
            for page_num in range(doc.page_count):
                page = doc[page_num]
                image_list = page.get_images()
                if image_list:
                    info['has_images'] = True
                    info['images'].extend([
                        {'page': page_num + 1, 'count': len(image_list)}
                    ])
            
            doc.close()
            return info
        except Exception as e:
            raise ValueError(f"无法获取PDF信息 {file_path}: {e}")
