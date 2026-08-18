import os
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QFrame, QPushButton, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor, QPainter, QPixmap, QColor
from config import THEMES
from utils import render_svg_with_tint, open_file_in_explorer

class ClickableFileNameLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file_path = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setWordWrap(True)
        self.hide()

    def set_file(self, file_path):
        self.current_file_path = file_path
        self.setText(os.path.basename(file_path))
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.current_file_path:
            open_file_in_explorer(self.current_file_path)

class SvgIconCell(QFrame):
    def __init__(self, file_path, file_name, on_click_callback, parent=None):
        super().__init__(parent)
        self.file_path, self.on_click_callback = file_path, on_click_callback
        self.lower_name = os.path.basename(file_path).lower()
        self.setFixedSize(110, 130)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(64, 64)

        self.txt_lbl = QLabel(file_name)
        self.txt_lbl.setWordWrap(True)
        self.txt_lbl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.txt_lbl.setMinimumHeight(40)

        layout.addWidget(self.img_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.txt_lbl, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.update_theme("dark")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click_callback(self.file_path)

    def update_theme(self, theme_mode):
        c = THEMES[theme_mode]
        self.setStyleSheet(f"SvgIconCell {{ background-color: {c['bg_card']}; border: 1px solid {c['border']}; border-radius: 6px; }} SvgIconCell:hover {{ border: 1px solid {c['border_focus']}; background-color: {c['border']}; }}")
        self.txt_lbl.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; background: transparent;")

class CopyButton(QPushButton):
    def __init__(self, text, format_type, parent=None):
        super().__init__(text, parent)
        self.format_type, self.orig_text, self.file_path = format_type, text, None
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.hide()
        self.clicked.connect(self.copy_code)

    def set_file(self, file_path):
        self.file_path = file_path
        self.show()

    def copy_code(self):
        if not self.file_path: return

        if self.format_type == "png":
            w = QApplication.activeWindow()
            if w and hasattr(w, 'view_canvas') and hasattr(w, 'theme_mode'):
                px = w.view_canvas.pixmap_item.pixmap()
                if not px.isNull():
                    final_png = QPixmap(px.size())
                    final_png.fill(Qt.GlobalColor.transparent)
                    p = QPainter(final_png)
                    p.drawPixmap(0, 0, px)
                    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    p.fillRect(final_png.rect(), QColor("#ffffff" if w.theme_mode == "dark" else "#000000"))
                    p.end()
                    QApplication.clipboard().setPixmap(final_png)
                    self.setText("PNG скопирован!")
                    QTimer.singleShot(1500, lambda: self.setText(self.orig_text))
            return

        with open(self.file_path, "r", encoding="utf-8") as f:
            code = f.read().strip()

        if self.format_type == "python":
            code = f'svg_code = """{code}"""'
        elif self.format_type == "js":
            code = f'const svgCode = `{code}`;'
        elif self.format_type == "json":
            import json
            code = json.dumps({os.path.basename(self.file_path): code}, ensure_ascii=False, indent=2)

        QApplication.clipboard().setText(code)
        self.setText("Скопировано!")
        QTimer.singleShot(1500, lambda: self.setText(self.orig_text))
