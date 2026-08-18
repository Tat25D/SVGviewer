import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt6.QtWidgets import QMainWindow, QGraphicsView
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from config import get_stylesheet
from utils import render_svg_with_tint, get_resource_path
from theme_manager import apply_widget_theme_styles
from viewer_actions import load_svg_icons

# ПРАВИЛЬНЫЕ ИМПОРТЫ МИКСИНОВ:
from viewer_ui import ViewerUIMixin
from viewer_navigation import ViewerNavigationMixin

class SvgViewer(QMainWindow, ViewerUIMixin, ViewerNavigationMixin):
    def __init__(self):
        super().__init__()
        self.theme_mode = "dark"
        self.setWindowTitle("SVG Viewer")
        self.resize(1600, 1000)
        self.setStyleSheet(get_stylesheet(self.theme_mode))
        self.icon_cells = []
        self.current_file_path = None

        icon_res_path = get_resource_path("app_icon.ico")
        if os.path.exists(icon_res_path):
            self.setWindowIcon(QIcon(icon_res_path))

        self.setup_ui()

        apply_widget_theme_styles(self)
        load_svg_icons(self)
        self.search_input.textChanged.connect(self.filter_icons)

    def showEvent(self, event):
        super().showEvent(event)
        if self.current_file_path:
            self.update_preview(reset_zoom=True)

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.setStyleSheet(get_stylesheet(self.theme_mode))
        apply_widget_theme_styles(self)
        for cell in self.icon_cells:
            cell.img_lbl.setPixmap(render_svg_with_tint(cell.file_path, 64, 64, self.theme_mode))
            cell.update_theme(self.theme_mode)
        self.update_preview(reset_zoom=False)

    def filter_icons(self, text):
        query = text.lower().strip()
        for cell in self.icon_cells:
            cell.setVisible(not query or query in cell.lower_name)
        self.flow_layout.update()

    def trigger_zoom(self, factor):
        self.view_canvas.scale(factor, factor)
        self.zoom_ctrl.set_percent(self.view_canvas.transform().m11())

    def show_preview(self, file_path):
        self.current_file_path = file_path
        self.update_preview(reset_zoom=True)
        for btn in self.btns: btn.set_file(file_path)

    def update_preview(self, reset_zoom=True):
        if not self.current_file_path: return

        rend = QSvgRenderer(self.current_file_path)
        bs = rend.defaultSize()
        # УБРАН МНОЖИТЕЛЬ * 8. Теперь 1px SVG = 1px на холсте.
        w = int(bs.width() if bs.width() > 0 else 64)
        h = int(bs.height() if bs.height() > 0 else 64)

        pixmap = render_svg_with_tint(self.current_file_path, w, h, self.theme_mode)
        self.view_canvas.set_pixmap(pixmap)

        if reset_zoom:
            self.view_canvas.resetTransform()

            view_size = self.view_canvas.viewport().size()
            min_view_dim = min(view_size.width(), view_size.height())
            min_pixmap_dim = min(pixmap.width(), pixmap.height())

            if min_pixmap_dim > 0 and min_view_dim > 0:
                target_dim = min_view_dim / 2.0
                scale_factor = target_dim / min_pixmap_dim
                self.view_canvas.scale(scale_factor, scale_factor)

            self.view_canvas.recenter()

        self.zoom_ctrl.set_percent(self.view_canvas.transform().m11())
        self.fn_label.set_file(self.current_file_path)
