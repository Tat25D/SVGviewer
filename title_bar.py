import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor, QPixmap
from utils import get_resource_path

class CustomTitleBar(QWidget):
    """Кастомный заголовок окна для железного вывода иконки."""
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        self.setObjectName("CustomTitleBar")
        self.setFixedHeight(32)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setScaledContents(True)
        
        icon_res_path = get_resource_path("app_icon.ico")
        if os.path.exists(icon_res_path):
            self.icon_label.setPixmap(QPixmap(icon_res_path))
        layout.addWidget(self.icon_label)
        layout.addSpacing(10)
        
        self.title_label = QLabel("SVG Viewer")
        self.title_label.setObjectName("TitleLabel")
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        
        for text, slot, is_close in [("—", self.window.showMinimized, False), ("▢", self.toggle_maximized, False), ("✕", self.window.close, True)]:
            btn = QPushButton(text)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setProperty("class", "TitleBtn")
            if is_close: btn.setObjectName("CloseBtn")
            btn.clicked.connect(slot)
            layout.addWidget(btn)
            if text == "▢": self.btn_max = btn
            
        self._drag_pos = QPoint()

    def toggle_maximized(self):
        if self.window.isMaximized():
            self.window.showNormal()
            self.btn_max.setText("▢")
        else:
            self.window.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.window.move(event.globalPosition().toPoint() - self._drag_pos)
