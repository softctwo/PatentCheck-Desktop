"""
PatentCheck-Desktop GUI主界面
简化版 - 基于PySide6
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QProgressBar,
    QGroupBox, QTableWidget, QTableWidgetItem, QMenuBar, QMenu,
    QMessageBox, QComboBox, QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QAction

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.models import CheckReport
from src.core.rule_engine import RuleEngine
from src.file_parser.parser import FileParser
from src.structure_checker.checker import StructureChecker
from src.image_checker.checker import ImageChecker
from src.alignment_checker.checker import AlignmentChecker
from src.report_generator.pdf_generator import PDFReportGenerator
from src.gui.config_manager import ConfigManager
from src.gui.config_dialog import ConfigDialog
from src.gui.history_dialog import HistoryDialog
from src.gui.document_preview_dialog import DocumentPreviewDialog
from src.ai_reviewer.reviewer import AIReviewer


class AIReviewThread(QThread):
    """计审查线程"""
    finished = Signal(str)  # 审查完成信号
    error = Signal(str)  # 错误信号
    progress = Signal(str)  # 进度信号
    document_content_extracted = Signal(str, str)  # 文档内容提取完成信号（路径，内容）
    
    def __init__(self, document_path, prompt, cached_content=None):
        super().__init__()
        self.document_path = document_path
        self.prompt = prompt
        self.cached_content = cached_content
    
    def run(self):
        """执行AI审查"""
        try:
            self.progress.emit("🤖 正在连接DeepSeek API...")
            
            from src.ai_reviewer.deepseek_client import DeepSeekClient
            client = DeepSeekClient()
            
            # 如果有缓存，直接使用
            if self.cached_content:
                self.progress.emit("✓ 使用缓存的文档内容")
                document_content = self.cached_content
            else:
                # 否则提取文档内容
                self.progress.emit("📄 正在提取文档内容...")
                reviewer = AIReviewer()
                document_content = reviewer.extract_document_text(self.document_path)
                
                # 发送文档内容给主线程缓存
                self.document_content_extracted.emit(self.document_path, document_content)
            
            # 调用API进行审查
            result = client.review_with_prompt(document_content, self.prompt)
            
            self.progress.emit("✓ AI审查完成")
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(f"AI审查失败: {str(e)}")


class CheckThread(QThread):
    """检测线程"""
    progress = Signal(str)  # 进度信号
    finished = Signal(object)  # 完成信号，传递报告对象
    error = Signal(str)  # 错误信号
    
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
    
    def run(self):
        """执行检测"""
        try:
            self.progress.emit("📁 正在扫描文件...")
            
            # 解析文件
            file_parser = FileParser(self.folder_path)
            document = file_parser.parse()
            
            self.progress.emit(f"✓ 找到说明书: {Path(document.specification_path).name if document.specification_path else '无'}")
            self.progress.emit(f"✓ 找到附图: {len(document.figures)}张")
            
            if not document.is_valid():
                self.error.emit("未找到有效的专利文档")
                return
            
            # 创建检测报告
            report = CheckReport(document=document)
            
            # 初始化规则引擎
            self.progress.emit("\n🔍 正在执行检查...")
            engine = RuleEngine()
            
            # 注册检查器
            engine.register_checker(StructureChecker())
            engine.register_checker(ImageChecker())
            engine.register_checker(AlignmentChecker())
            
            # 执行检查
            results = engine.run_checks(document)
            
            # 添加结果到报告
            for result in results:
                report.add_result(result)
            
            self.progress.emit(f"✓ 完成检查，共{len(results)}项结果\n")
            
            # 发送完成信号
            self.finished.emit(report)
            
        except Exception as e:
            self.error.emit(f"检测失败: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.folder_path = None
        self.report = None
        self.check_thread = None
        self.ai_review_thread = None
        
        # 文档内容缓存（用于AI审查）
        self.cached_document_content = None
        self.cached_document_path = None
        
        # 配置管理器
        self.config_manager = ConfigManager()
        
        self.init_ui()
        
        # 恢复上次的文件夹
        last_folder = self.config_manager.get("last_folder", "")
        if last_folder and Path(last_folder).exists():
            self.folder_path = last_folder
            self.lbl_folder.setText(f"上次路径: {last_folder}")
            self.btn_check.setEnabled(True)
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("PatentCheck-Desktop V0.9")
        self.setGeometry(100, 100, 900, 700)
        
        # 设置窗口图标（如果存在）
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 标题
        title = QLabel("专利申请自检工具")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 选择文件夹按钮
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("📁 选择专利文件夹")
        self.btn_select.setMinimumHeight(40)
        self.btn_select.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_check = QPushButton("🔍 开始检测")
        self.btn_check.setMinimumHeight(40)
        self.btn_check.setEnabled(False)
        self.btn_check.clicked.connect(self.start_check)
        btn_layout.addWidget(self.btn_check)
        
        self.btn_preview = QPushButton("📄 预览申请材料")
        self.btn_preview.setMinimumHeight(40)
        self.btn_preview.setEnabled(False)
        self.btn_preview.clicked.connect(self.preview_documents)
        btn_layout.addWidget(self.btn_preview)
        
        layout.addLayout(btn_layout)
        
        # 当前文件夹标签
        self.lbl_folder = QLabel("未选择文件夹")
        layout.addWidget(self.lbl_folder)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # ============ AI审查区域 ============
        ai_review_group = QGroupBox("🤖 AI审查")
        ai_review_layout = QVBoxLayout()
        
        # 预设提示词和输入框
        prompt_layout = QHBoxLayout()
        prompt_layout.addWidget(QLabel("预设提示词:"))
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItems([
            "自定义",
            "请审查这份专利申请的技术方案完整性和逻辑性",
            "请评估专利申请的创新性和实用性",
            "请检查权利要求书的保护范围是否清晰合理",
            "请分析专利申请中可能存在的法律风险"
        ])
        self.prompt_combo.currentIndexChanged.connect(self.on_prompt_combo_changed)
        prompt_layout.addWidget(self.prompt_combo)
        ai_review_layout.addLayout(prompt_layout)
        
        # 提示词输入框（多行）
        prompt_input_label = QLabel("提示词:")
        ai_review_layout.addWidget(prompt_input_label)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("请输入或选择审查提示词...\n支持多行输入")
        self.prompt_input.setMaximumHeight(80)  # 限制高度为3-4行
        ai_review_layout.addWidget(self.prompt_input)
        
        # 同步执行和开始按钮
        ai_control_layout = QHBoxLayout()
        self.sync_review_checkbox = QCheckBox("同步执行AI审查")
        self.sync_review_checkbox.setToolTip("勾选后，形式检查完成后将自动进行AI审查")
        ai_control_layout.addWidget(self.sync_review_checkbox)
        ai_control_layout.addStretch()
        self.ai_review_button = QPushButton("🤖 开始AI审查")
        self.ai_review_button.setEnabled(False)
        self.ai_review_button.setMinimumHeight(35)
        self.ai_review_button.clicked.connect(self.start_ai_review)
        ai_control_layout.addWidget(self.ai_review_button)
        ai_review_layout.addLayout(ai_control_layout)
        
        # AI审查结果展示区
        ai_result_label = QLabel("审查结果:")
        ai_review_layout.addWidget(ai_result_label)
        self.ai_result_text = QTextEdit()
        self.ai_result_text.setReadOnly(True)
        self.ai_result_text.setMaximumHeight(200)
        self.ai_result_text.setPlaceholderText("这里将显示AI审查结果...")
        ai_review_layout.addWidget(self.ai_result_text)
        
        ai_review_group.setLayout(ai_review_layout)
        layout.addWidget(ai_review_group)
        # ============ AI审查区域结束 ============
        
        # 日志输出
        log_group = QGroupBox("检测日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # 结果摘要
        summary_group = QGroupBox("检测摘要")
        summary_layout = QHBoxLayout()
        self.lbl_total = QLabel("总检查项: 0")
        self.lbl_errors = QLabel("🛑 错误: 0")
        self.lbl_warnings = QLabel("⚠️ 警告: 0")
        self.lbl_passes = QLabel("✅ 通过: 0")
        summary_layout.addWidget(self.lbl_total)
        summary_layout.addWidget(self.lbl_errors)
        summary_layout.addWidget(self.lbl_warnings)
        summary_layout.addWidget(self.lbl_passes)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # 结果详情表格
        results_group = QGroupBox("检测详情")
        results_layout = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["级别", "标题", "位置", "建议"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        self.btn_export_pdf = QPushButton("📄 导出PDF报告")
        self.btn_export_pdf.setEnabled(False)
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.btn_export_pdf)
        
        self.btn_export_json = QPushButton("📋 导出JSON数据")
        self.btn_export_json.setEnabled(False)
        self.btn_export_json.clicked.connect(self.export_json)
        export_layout.addWidget(self.btn_export_json)
        
        layout.addLayout(export_layout)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开文件夹...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.select_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 历史菜单
        history_menu = menubar.addMenu("历史")
        
        show_history_action = QAction("查看历史记录", self)
        show_history_action.setShortcut("Ctrl+H")
        show_history_action.triggered.connect(self.show_history)
        history_menu.addAction(show_history_action)
        
        clear_history_action = QAction("清空历史记录", self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        
        config_action = QAction("偏好设置...", self)
        config_action.setShortcut("Ctrl+,")
        config_action.triggered.connect(self.show_config)
        settings_menu.addAction(config_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def select_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择专利文件夹"
        )
        if folder:
            self.folder_path = folder
            self.lbl_folder.setText(f"已选择: {folder}")
            self.btn_check.setEnabled(True)
            self.log("选择文件夹: " + folder)
            
            # 保存到配置
            self.config_manager.set("last_folder", folder)
    
    def start_check(self):
        """开始检测"""
        if not self.folder_path:
            return
        
        # 禁用按钮
        self.btn_select.setEnabled(False)
        self.btn_check.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_export_pdf.setEnabled(False)
        self.btn_export_json.setEnabled(False)
        
        # 清空结果
        self.log_text.clear()
        self.results_table.setRowCount(0)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # 无限进度
        
        # 创建并启动检测线程
        self.check_thread = CheckThread(self.folder_path)
        self.check_thread.progress.connect(self.log)
        self.check_thread.finished.connect(self.on_check_finished)
        self.check_thread.error.connect(self.on_check_error)
        self.check_thread.start()
    
    def on_check_finished(self, report):
        """检测完成"""
        self.report = report
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 更新摘要
        summary = report.get_summary()
        self.lbl_total.setText(f"总检查项: {summary['total']}")
        self.lbl_errors.setText(f"🛑 错误: {summary['errors']}")
        self.lbl_warnings.setText(f"⚠️ 警告: {summary['warnings']}")
        self.lbl_passes.setText(f"✅ 通过: {summary['passes']}")
        
        # 填充结果表格
        self.results_table.setRowCount(len(report.results))
        for i, result in enumerate(report.results):
            # 级别
            severity_map = {
                'error': '🛑 错误',
                'warning': '⚠️ 警告',
                'info': 'ℹ️ 提示',
                'pass': '✅ 通过'
            }
            self.results_table.setItem(i, 0, QTableWidgetItem(
                severity_map.get(result.severity.value, result.severity.value)
            ))
            
            # 标题
            self.results_table.setItem(i, 1, QTableWidgetItem(result.title))
            
            # 位置
            self.results_table.setItem(i, 2, QTableWidgetItem(
                Path(result.location).name if Path(result.location).exists() else result.location
            ))
            
            # 建议
            self.results_table.setItem(i, 3, QTableWidgetItem(
                result.suggestion or result.description
            ))
        
        self.results_table.resizeColumnsToContents()
        
        self.log("\n✨ 检测完成！")
        
        # 添加到历史记录
        self.config_manager.add_history(self.folder_path, summary)
        
        # 自动保存报告
        if self.config_manager.get("auto_save_report", True):
            self.auto_save_report()
        
        # 启用按钮
        self.btn_select.setEnabled(True)
        self.btn_check.setEnabled(True)
        self.btn_preview.setEnabled(True)  # 启用预览按钮
        self.btn_export_pdf.setEnabled(True)
        self.btn_export_json.setEnabled(True)
        self.ai_review_button.setEnabled(True)
        
        # 检查是否需要同步执行AI审查
        if self.sync_review_checkbox.isChecked():
            prompt = self.prompt_input.toPlainText().strip()
            if prompt and self.report and self.report.document.specification_path:
                self.log("\n🤖 开始同步执行AI审查...")
                self.start_ai_review()
    
    def on_check_error(self, error_msg):
        """检测错误"""
        self.progress_bar.setVisible(False)
        self.log(f"\n❌ 错误: {error_msg}")
        
        # 启用按钮
        self.btn_select.setEnabled(True)
        self.btn_check.setEnabled(True)
    
    def export_pdf(self):
        """导出PDF报告"""
        if not self.report:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存PDF报告", "patent_check_report.pdf", "PDF Files (*.pdf)"
        )
        
        if filename:
            try:
                pdf_gen = PDFReportGenerator()
                pdf_gen.generate(self.report, filename)
                self.log(f"✓ PDF报告已保存: {filename}")
            except Exception as e:
                self.log(f"❌ PDF生成失败: {e}")
    
    def export_json(self):
        """导出JSON数据"""
        if not self.report:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存JSON数据", "patent_check_report.json", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.report.to_dict(), f, ensure_ascii=False, indent=2)
                self.log(f"✓ JSON数据已保存: {filename}")
            except Exception as e:
                self.log(f"❌ JSON导出失败: {e}")
    
    def auto_save_report(self):
        """自动保存报告"""
        if not self.report:
            return
        
        try:
            output_format = self.config_manager.get("default_output_format", "pdf")
            folder = Path(self.folder_path)
            
            if output_format == "pdf" or output_format == "both":
                pdf_path = folder / "patent_check_report.pdf"
                pdf_gen = PDFReportGenerator()
                pdf_gen.generate(self.report, str(pdf_path))
                self.log(f"✓ 自动保存PDF: {pdf_path}")
            
            if output_format == "json" or output_format == "both":
                json_path = folder / "patent_check_report.json"
                import json
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.report.to_dict(), f, ensure_ascii=False, indent=2)
                self.log(f"✓ 自动保存JSON: {json_path}")
                
        except Exception as e:
            self.log(f"❌ 自动保存失败: {e}")
    
    def show_history(self):
        """显示历史记录"""
        dialog = HistoryDialog(self.config_manager, self)
        dialog.folder_selected.connect(self.load_from_history)
        dialog.exec()
    
    def load_from_history(self, folder_path: str):
        """从历史记录加载"""
        if Path(folder_path).exists():
            self.folder_path = folder_path
            self.lbl_folder.setText(f"已选择: {folder_path}")
            self.btn_check.setEnabled(True)
            self.log(f"从历史记录加载: {folder_path}")
        else:
            QMessageBox.warning(self, "警告", f"文件夹不存在:\n{folder_path}")
    
    def clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空所有历史记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.clear_history()
            QMessageBox.information(self, "提示", "历史记录已清空")
    
    def preview_documents(self):
        """预览申请文档"""
        if not self.report:
            QMessageBox.warning(self, "提示", "请先进行检测")
            return
        
        # 准备文档字典
        documents = {}
        
        if self.report.document.specification_path:
            documents["说明书"] = self.report.document.specification_path
        
        if self.report.document.claims_path:
            documents["权利要求书"] = self.report.document.claims_path
        
        if self.report.document.abstract_path:
            documents["摘要"] = self.report.document.abstract_path
        
        # 检查是否有可预览的文档
        if not documents:
            QMessageBox.warning(self, "提示", "没有找到可预览的文档\n\n支持的格式：PDF、Word (.docx)")
            return
        
        # 创建并显示预览对话框
        dialog = DocumentPreviewDialog(self)
        dialog.set_documents(documents)
        dialog.exec()
        
        self.log("✓ 已关闭文档预览")
    
    # ================= AI审查 相关方法 =================
    def on_prompt_combo_changed(self, index: int):
        """当选择预设提示词时，自动填充到输入框"""
        text = self.prompt_combo.currentText()
        if text == "自定义":
            self.prompt_input.clear()
            self.prompt_input.setFocus()
        else:
            self.prompt_input.setPlainText(text)
    
    def start_ai_review(self):
        """开始AI审查（独立或同步调用）"""
        if not self.report or not self.report.document.specification_path:
            QMessageBox.warning(self, "提示", "请先选择并检测包含说明书的专利文件夹")
            return
        
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请先输入或选择审查提示词")
            return
        
        self.ai_result_text.clear()
        self.ai_review_button.setEnabled(False)
        self.log("🤖 正在进行AI审查，请稍候...")
        
        doc_path = self.report.document.specification_path
        
        # 检查是否有缓存的文档内容
        cached_content = None
        if self.cached_document_path == doc_path and self.cached_document_content:
            cached_content = self.cached_document_content
            self.log("ℹ️ 使用已缓存的文档内容，无需重新读取")
        
        # 创建并启动AI审查线程
        self.ai_review_thread = AIReviewThread(doc_path, prompt, cached_content)
        self.ai_review_thread.progress.connect(self.log)
        self.ai_review_thread.finished.connect(self.on_ai_review_finished)
        self.ai_review_thread.error.connect(self.on_ai_review_error)
        self.ai_review_thread.document_content_extracted.connect(self.on_document_content_extracted)
        self.ai_review_thread.start()
    
    def on_ai_review_finished(self, result: str):
        """AI审查完成"""
        self.ai_result_text.setPlainText(result)
        if self.report:
            self.report.ai_review_result = result
            self.report.ai_review_prompt = self.prompt_input.toPlainText().strip()
        self.ai_review_button.setEnabled(True)
        self.log("✓ AI审查结果已生成")
    
    def on_ai_review_error(self, error_msg: str):
        """计审查错误"""
        self.ai_result_text.setPlainText(f"❌ AI审查失败：{error_msg}")
        self.ai_review_button.setEnabled(True)
        self.log(f"❌ AI审查失败：{error_msg}")
    
    def on_document_content_extracted(self, doc_path: str, content: str):
        """文档内容提取完成，缓存内容"""
        self.cached_document_path = doc_path
        self.cached_document_content = content
        self.log(f"✓ 文档内容已缓存（{len(content)}字符），下次审查将直接使用")
    # ================= AI审查 方法结束 =================
    
    def show_config(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec():
            self.log("配置已更新")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 PatentCheck-Desktop",
            "<h3>PatentCheck-Desktop V0.9</h3>"
            "<p>专利申请文件自动检测工具</p>"
            "<p>功能：</p>"
            "<ul>"
            "<li>说明书结构完整性检查</li>"
            "<li>附图规范性检查</li>"
            "<li>图文标号对齐检查</li>"
            "</ul>"
            "<p>© 2024 PatentCheck Team</p>"
        )
    
    def log(self, message):
        """添加日志"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )


def main():
    """启动GUI"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
