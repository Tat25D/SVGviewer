import os
from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
                             QApplication, QWidget, QGraphicsView, QGraphicsScene,
                             QGraphicsPixmapItem, QDialog, QGridLayout, QCheckBox,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QCursor, QPainter, QMouseEvent, QWheelEvent, QPixmap, QColor
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
        self.setFixedSize(85, 95)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(64, 64)
        self.txt_lbl = QLabel(file_name)
        self.txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.img_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.txt_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
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

class SvgGraphicsView(QGraphicsView):
    zoom_changed_manually = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setStyleSheet("background: transparent; border: none;")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.is_panning = False
        self.pan_start_pos = QPoint()

    def scrollContentsBy(self, dx, dy): pass

    def set_pixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.pixmap_item.setPos(-pixmap.width() / 2, -pixmap.height() / 2)
        self.centerOn(0, 0)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(zoom_factor, zoom_factor)
        self.zoom_changed_manually.emit(self.transform().m11())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning, self.pan_start_pos = True, event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_panning:
            delta = (event.pos() - self.pan_start_pos) / self.transform().m11()
            self.pan_start_pos = event.pos()
            self.translate(delta.x(), delta.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

class ZoomController(QWidget):
    zoom_in_signal, zoom_out_signal = pyqtSignal(), pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.m_btn = QPushButton("-")
        self.m_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.m_btn.clicked.connect(self.zoom_out_signal.emit)

        self.lbl_percent = QLabel("800%")
        self.lbl_percent.setFixedWidth(60)
        self.lbl_percent.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.p_btn = QPushButton("+")
        self.p_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.p_btn.clicked.connect(self.zoom_in_signal.emit)

        layout.addWidget(self.m_btn); layout.addWidget(self.lbl_percent); layout.addWidget(self.p_btn)

    def set_percent(self, current_transform_m11):
        self.lbl_percent.setText(f"{int(current_transform_m11 * 800)}%")

class ExportDialog(QDialog):
    def __init__(self, file_path, theme_mode, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.theme_mode = theme_mode
        self.setWindowTitle("Экспорт иконки")
        self.setMinimumWidth(320)

        # ПРИМЕНЕНИЕ СТИЛЕЙ ПРИЛОЖЕНИЯ К ОКНУ ЭКСПОРТА
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

        # 1. Выбор размеров
        layout.addWidget(QLabel("Выберите размеры:"))
        self.size_checkboxes = {}
        sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
        grid = QGridLayout()
        for i, size in enumerate(sizes):
            cb = QCheckBox(f"{size}x{size}")
            if size == 64: cb.setChecked(True)
            self.size_checkboxes[size] = cb
            grid.addWidget(cb, i // 4, i % 4)

        self.cb_all = QCheckBox("Все размеры")
        self.cb_all.stateChanged.connect(self.toggle_all_sizes)
        grid.addWidget(self.cb_all, 2, 0, 1, 4)
        layout.addLayout(grid)

        # 2. Выбор формата
        layout.addWidget(QLabel("Формат сохранения:"))
        fmt_layout = QHBoxLayout()

        self.btn_png = QPushButton("PNG")
        self.btn_ico = QPushButton("ICO")
        self.btn_jpg = QPushButton("JPG")

        self.btn_png.clicked.connect(lambda: self.start_export("PNG"))
        self.btn_ico.clicked.connect(lambda: self.start_export("ICO"))
        self.btn_jpg.clicked.connect(lambda: self.start_export("JPG"))

        fmt_layout.addWidget(self.btn_png)
        fmt_layout.addWidget(self.btn_ico)
        fmt_layout.addWidget(self.btn_jpg)
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
        if not sizes:
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы один размер!")
            return

        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        ext = fmt.lower()
        default_name = f"{base_name}_icon.{ext}" if len(sizes) > 1 else f"{base_name}_{sizes[0]}x{sizes[0]}.{ext}"
        filter_str = f"{fmt} Image (*.{ext});;All Files (*)"

        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить как", default_name, filter_str)
        if not file_name: return

        self.save_icons(file_name, fmt, sizes)
        self.accept()

    def save_icons(self, file_name, fmt, sizes):
        base_dir = os.path.dirname(file_name)
        base_name = os.path.splitext(os.path.basename(file_name))[0]

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
