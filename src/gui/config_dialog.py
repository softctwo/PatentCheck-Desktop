"""
配置对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QCheckBox, QComboBox, QSpinBox,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt

from .config_manager import ConfigManager


class ConfigDialog(QDialog):
    """配置对话框"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 报告设置组
        report_group = QGroupBox("报告设置")
        report_layout = QFormLayout()
        
        # 自动保存报告
        self.chk_auto_save = QCheckBox()
        self.chk_auto_save.setChecked(
            self.config_manager.get("auto_save_report", True)
        )
        report_layout.addRow("自动保存报告:", self.chk_auto_save)
        
        # 默认输出格式
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(["pdf", "json", "both"])
        current_format = self.config_manager.get("default_output_format", "pdf")
        self.cmb_format.setCurrentText(current_format)
        report_layout.addRow("默认输出格式:", self.cmb_format)
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        # 历史记录设置组
        history_group = QGroupBox("历史记录")
        history_layout = QFormLayout()
        
        # 最大历史记录数
        self.spin_max_history = QSpinBox()
        self.spin_max_history.setRange(5, 100)
        self.spin_max_history.setValue(
            self.config_manager.get("max_history", 20)
        )
        history_layout.addRow("最大记录数:", self.spin_max_history)
        
        # 清空历史按钮
        self.btn_clear_history = QPushButton("清空历史记录")
        self.btn_clear_history.clicked.connect(self.clear_history)
        history_layout.addRow("", self.btn_clear_history)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QFormLayout()
        
        # 显示提示
        self.chk_show_hints = QCheckBox()
        self.chk_show_hints.setChecked(
            self.config_manager.get("show_hints", True)
        )
        ui_layout.addRow("显示操作提示:", self.chk_show_hints)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self.save_config)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def save_config(self):
        """保存配置"""
        self.config_manager.set("auto_save_report", self.chk_auto_save.isChecked())
        self.config_manager.set("default_output_format", self.cmb_format.currentText())
        self.config_manager.set("max_history", self.spin_max_history.value())
        self.config_manager.set("show_hints", self.chk_show_hints.isChecked())
        
        self.accept()
    
    def clear_history(self):
        """清空历史记录"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            "确认",
            "确定要清空所有历史记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.clear_history()
            QMessageBox.information(self, "提示", "历史记录已清空")
