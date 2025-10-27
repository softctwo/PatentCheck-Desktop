"""
历史记录对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal

from .config_manager import ConfigManager


class HistoryDialog(QDialog):
    """历史记录对话框"""
    
    # 信号：选择了某个历史记录
    folder_selected = Signal(str)
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_history()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("检测历史")
        self.setMinimumSize(700, 400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "文件夹", "检测时间", "总数", "错误", "警告"
        ])
        
        # 设置列宽
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.history_table)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.btn_open = QPushButton("打开选中文件夹")
        self.btn_open.clicked.connect(self.open_selected)
        btn_layout.addWidget(self.btn_open)
        
        self.btn_delete = QPushButton("删除选中记录")
        self.btn_delete.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch()
        
        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
    
    def load_history(self):
        """加载历史记录"""
        history = self.config_manager.history
        
        self.history_table.setRowCount(len(history))
        
        for i, record in enumerate(reversed(history)):  # 倒序显示
            # 文件夹
            self.history_table.setItem(i, 0, QTableWidgetItem(record["folder"]))
            
            # 时间
            self.history_table.setItem(i, 1, QTableWidgetItem(record["time"]))
            
            # 摘要
            summary = record.get("summary", {})
            self.history_table.setItem(i, 2, QTableWidgetItem(
                str(summary.get("total", 0))
            ))
            self.history_table.setItem(i, 3, QTableWidgetItem(
                str(summary.get("errors", 0))
            ))
            self.history_table.setItem(i, 4, QTableWidgetItem(
                str(summary.get("warnings", 0))
            ))
    
    def on_item_double_clicked(self):
        """双击打开"""
        self.open_selected()
    
    def open_selected(self):
        """打开选中的文件夹"""
        selected_rows = self.history_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        folder = self.history_table.item(row, 0).text()
        
        # 发射信号
        self.folder_selected.emit(folder)
        self.accept()
    
    def delete_selected(self):
        """删除选中的记录"""
        from PySide6.QtWidgets import QMessageBox
        
        selected_rows = self.history_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        folder = self.history_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除此记录吗？\n{folder}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从历史记录中删除
            self.config_manager.history = [
                h for h in self.config_manager.history 
                if h["folder"] != folder
            ]
            self.config_manager.save_history()
            
            # 刷新表格
            self.load_history()
