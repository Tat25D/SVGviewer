import os
import shutil
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
                             QDialog, QGridLayout, QCheckBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor
from config import THEMES
from utils import render_svg_with_tint

class ExportDialog(QDialog):
    def __init__(self, file_path, theme_mode, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.theme_mode = theme_mode
        self.setWindowTitle("Экспорт иконки")
        self.setMinimumWidth(320)

        c = THEMES[theme_mode]
        self.setStyleSheet(f"""
            QDialog {{ background-color: {c['bg_main']}; color: {c['text_main']}; }}
            QLabel {{ color: {c['text_main']}; font-size: 14px; font-weight: bold; }}
            QCheckBox {{ color: {c['text_main']}; font-size: 13px; spacing: 8px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid {c['border_focus']}; background: {c['bg_card']}; }}
            QCheckBox::indicator:checked {{ background-color: {c['accent']}; border: 1px solid {c['accent']}; }}
            QPushButton {{ background-color: {c['bg_card']}; color: {c['text_main']}; border: 1px solid {c['border']}; border-radius: 6px; padding: 10px 16px; font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {c['border']}; border: 1px solid {c['border_focus']}; }}
        """)

        layout = QVBoxLayout(self)

        # ИЗМЕНЕННЫЙ ТЕКСТ
        layout.addWidget(QLabel("Size:"))
        self.size_checkboxes = {}
        sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
        grid = QGridLayout()
        for i, size in enumerate(sizes):
            cb = QCheckBox(f"{size}x{size}")
            if size == 64: cb.setChecked(True)
            self.size_checkboxes[size] = cb
            grid.addWidget(cb, i // 4, i % 4)

        # ИЗМЕНЕННЫЙ ТЕКСТ
        self.cb_all = QCheckBox("All")
        self.cb_all.stateChanged.connect(self.toggle_all_sizes)
        grid.addWidget(self.cb_all, 2, 0, 1, 4)
        layout.addLayout(grid)

        # ИЗМЕНЕННЫЙ ТЕКСТ
        layout.addWidget(QLabel("Format:"))
        fmt_layout = QHBoxLayout()

        self.btn_png = QPushButton("PNG")
        self.btn_ico = QPushButton("ICO")
        self.btn_jpg = QPushButton("JPG")
        self.btn_svg = QPushButton("SVG")

        self.btn_png.clicked.connect(lambda: self.start_export("PNG"))
        self.btn_ico.clicked.connect(lambda: self.start_export("ICO"))
        self.btn_jpg.clicked.connect(lambda: self.start_export("JPG"))
        self.btn_svg.clicked.connect(lambda: self.start_export("SVG"))

        fmt_layout.addWidget(self.btn_png)
        fmt_layout.addWidget(self.btn_ico)
        fmt_layout.addWidget(self.btn_jpg)
        fmt_layout.addWidget(self.btn_svg)
        layout.addLayout(fmt_layout)

    def toggle_all_sizes(self, state):
        checked = state == 2
        for cb in self.size_checkboxes.values():
            cb.setChecked(checked)
            cb.setEnabled(not checked)

    def get_selected_sizes(self):
        if self.cb_all.isChecked():
            return list(self.size_checkboxes.keys())
        return [size for size, cb in self.size_checkboxes.items() if cb.isChecked()]

    def start_export(self, fmt):
        sizes = self.get_selected_sizes()
        if not sizes and fmt != "SVG":
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы один размер!")
            return

        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        ext = fmt.lower()

        if fmt == "SVG":
            default_name = f"{base_name}.svg"
            filter_str = "SVG Image (*.svg);;All Files (*)"
        else:
            default_name = f"{base_name}_icon.{ext}" if len(sizes) > 1 else f"{base_name}_{sizes[0]}x{sizes[0]}.{ext}"
            filter_str = f"{fmt} Image (*.{ext});;All Files (*)"

        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить как", default_name, filter_str)
        if not file_name: return

        self.save_icons(file_name, fmt, sizes)
        self.accept()

    def save_icons(self, file_name, fmt, sizes):
        base_dir = os.path.dirname(file_name)
        base_name = os.path.splitext(os.path.basename(file_name))[0]

        if fmt == "SVG":
            if len(sizes) > 1:
                for size in sizes:
                    save_path = os.path.join(base_dir, f"{base_name}_{size}x{size}.svg")
                    shutil.copy(self.file_path, save_path)
            else:
                shutil.copy(self.file_path, file_name)
            return

        for size in sizes:
            pixmap = render_svg_with_tint(self.file_path, size, size, self.theme_mode)

            if fmt == "JPG":
                temp_pixmap = QPixmap(pixmap.size())
                temp_pixmap.fill(QColor("#FFFFFF"))
                p = QPainter(temp_pixmap)
                p.drawPixmap(0, 0, pixmap)
                p.end()
                pixmap = temp_pixmap

            if len(sizes) > 1:
                save_path = os.path.join(base_dir, f"{base_name}_{size}x{size}.{fmt.lower()}")
            else:
                save_path = file_name

            pixmap.save(save_path, fmt)
