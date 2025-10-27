"""
PDF报告生成器
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from datetime import datetime

from ..core.models import CheckReport, Severity


class PDFReportGenerator:
    """PDF报告生成器"""
    
    def __init__(self):
        # 注册中文字体（macOS系统）
        self.chinese_font = 'Helvetica'  # 默认字体
        
        # 尝试多个中文字体路径
        font_paths = [
            '/System/Library/Fonts/STHeiti Light.ttc',  # 华文黑体
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/PingFang.ttc',  # 苹方
            '/System/Library/Fonts/Supplemental/Songti.ttc',  # 宋体
        ]
        
        for font_path in font_paths:
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                self.chinese_font = 'ChineseFont'
                print(f"✓ 成功注册中文字体: {font_path}")
                break
            except Exception as e:
                continue
        
        if self.chinese_font == 'Helvetica':
            print("⚠️  未找到中文字体，PDF可能无法正确显示中文")
    
    def generate(self, report: CheckReport, output_path: str):
        """
        生成PDF报告
        
        Args:
            report: 检测报告对象
            output_path: 输出文件路径
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建文档内容
        story = []
        styles = getSampleStyleSheet()
        
        # 创建中文样式
        if self.chinese_font != 'Helvetica':
            # 修改所有样式使用中文字体
            for style_name in styles.byName:
                styles[style_name].fontName = self.chinese_font
        
        # 标题
        title = Paragraph(
            "<b>专利申请自检报告</b>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.5*cm))
        
        # 基本信息
        info_text = f"""
        生成时间: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}<br/>
        检测文件: {report.document.specification_path or '未指定'}
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # 摘要统计
        summary = report.get_summary()
        summary_data = [
            ['统计项', '数量'],
            ['总检查项', str(summary['total'])],
            ['严重错误', str(summary['errors'])],
            ['警告', str(summary['warnings'])],
            ['提示', str(summary['infos'])],
            ['通过', str(summary['passes'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 1*cm))
        
        # 详细结果
        story.append(Paragraph("<b>检测详情</b>", styles['Heading2']))
        story.append(Spacer(1, 0.3*cm))
        
        for i, result in enumerate(report.results, 1):
            # 错误级别图标
            severity_icon = {
                Severity.ERROR: '[ERROR]',
                Severity.WARNING: '[WARNING]',
                Severity.INFO: '[INFO]',
                Severity.PASS: '[PASS]'
            }
            
            result_text = f"""
            <b>{i}. {severity_icon[result.severity]} {result.title}</b><br/>
            位置: {result.location}<br/>
            描述: {result.description}<br/>
            """
            
            if result.suggestion:
                result_text += f"建议: {result.suggestion}<br/>"
            if result.reference:
                result_text += f"参考: {result.reference}<br/>"
            
            story.append(Paragraph(result_text, styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
        
        # AI审查结果
        if report.ai_review_result:
            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("<b>AI审查结果</b>", styles['Heading2']))
            story.append(Spacer(1, 0.3*cm))
            
            # 显示使用的提示词
            if report.ai_review_prompt:
                prompt_text = f"<b>审查提示词:</b> {report.ai_review_prompt}<br/>"
                story.append(Paragraph(prompt_text, styles['Normal']))
                story.append(Spacer(1, 0.2*cm))
            
            # 格式化AI审查结果，将换行符转换为<br/>
            ai_result_text = report.ai_review_result.replace('\n', '<br/>')
            # 简单转义HTML特殊字符
            ai_result_text = ai_result_text.replace('<', '&lt;').replace('>', '&gt;')
            # 再把<br/>恢复
            ai_result_text = ai_result_text.replace('&lt;br/&gt;', '<br/>')
            
            story.append(Paragraph(ai_result_text, styles['Normal']))
            story.append(Spacer(1, 0.5*cm))
        
        # 免责声明
        disclaimer = """
        <br/><br/>
        <b>免责声明</b><br/>
        本报告由PatentCheck-Desktop自动生成，仅供参考。检测结果不构成法律意见，
        最终审查以国家知识产权局的正式审查为准。
        """
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(disclaimer, styles['Normal']))
        
        # 生成PDF
        doc.build(story)
