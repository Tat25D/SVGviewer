from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QScrollArea, QLineEdit,
                             QPushButton, QWidget, QFrame, QSplitter, QLabel)
from PyQt6.QtCore import Qt, QSize

from flow_layout import FlowLayout
from ui_components import ClickableFileNameLabel, CopyButton
from graphics_widgets import SvgGraphicsView, ZoomController
from theme_manager import fix_search_layout
from viewer_actions import open_export_dialog, reload_icons, normalize_current, normalize_all
from utils import (create_svg_icon, SVG_BAR_UP, SVG_BAR_DOWN, SVG_COMPACT_UP, SVG_COMPACT_DOWN,
                   SVG_REFRESH, SVG_THEME, SVG_EXPORT, SVG_NORM_1, SVG_NORM_ALL, THEMES)

class ViewerUIMixin:
    def setup_ui(self):
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        self._setup_left_panel()
        self._setup_right_panel()
        self.splitter.setSizes([450, 1150])

    def _setup_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Поиск...")
        search_overlay = QHBoxLayout(self.search_input)
        search_overlay.setContentsMargins(0, 0, 8, 0)
        search_overlay.setSpacing(8)
        search_overlay.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.clear_btn = QPushButton(""); self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(lambda: self.search_input.clear())
        search_overlay.addWidget(self.clear_btn)

        self.layout_btn = QPushButton("Я-Z"); self.layout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout_btn.clicked.connect(lambda: fix_search_layout(self))
        search_overlay.addWidget(self.layout_btn)

        left_layout.addWidget(self.search_input)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.g_container = QWidget()
        self.flow_layout = FlowLayout(self.g_container, margin=10, spacing=10); self.scroll.setWidget(self.g_container)
        left_layout.addWidget(self.scroll, stretch=1)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        c = THEMES[self.theme_mode]

        self.btn_top = QPushButton("")
        self.btn_top.setIcon(create_svg_icon(SVG_BAR_UP, c['text_main'], 28))
        self.btn_top.setIconSize(QSize(28, 28))
        self.btn_top.setObjectName("NavFirstBtn")

        self.btn_page_up = QPushButton("")
        self.btn_page_up.setIcon(create_svg_icon(SVG_COMPACT_UP, c['text_main'], 28))
        self.btn_page_up.setIconSize(QSize(28, 28))

        self.btn_page_down = QPushButton("")
        self.btn_page_down.setIcon(create_svg_icon(SVG_COMPACT_DOWN, c['text_main'], 28))
        self.btn_page_down.setIconSize(QSize(28, 28))

        self.btn_bottom = QPushButton("")
        self.btn_bottom.setIcon(create_svg_icon(SVG_BAR_DOWN, c['text_main'], 28))
        self.btn_bottom.setIconSize(QSize(28, 28))
        self.btn_bottom.setObjectName("NavLastBtn")

        self.btn_top.clicked.connect(self.scroll_to_top)
        self.btn_page_up.clicked.connect(self.scroll_page_up)
        self.btn_page_down.clicked.connect(self.scroll_page_down)
        self.btn_bottom.clicked.connect(self.scroll_to_bottom)

        for btn in (self.btn_top, self.btn_page_up, self.btn_page_down, self.btn_bottom):
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_layout.addWidget(btn, stretch=1)

        left_layout.addLayout(nav_layout)
        left_widget.setMinimumWidth(200); self.splitter.addWidget(left_widget)

    def _setup_right_panel(self):
        self.p_frame = QFrame()
        p_layout = QVBoxLayout(self.p_frame)
        p_layout.setContentsMargins(20, 20, 20, 20)
        p_layout.setSpacing(10)

        # 1. ПАНЕЛЬ УПРАВЛЕНИЯ (КНОПКИ 72x72, ЭКСПОРТ В КОНЦЕ)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(8)

        c = THEMES[self.theme_mode]

        self.reload_btn = QPushButton("")
        self.reload_btn.setIcon(create_svg_icon(SVG_REFRESH, c['text_main'], 36))
        self.reload_btn.setIconSize(QSize(36, 36))
        self.reload_btn.setFixedSize(72, 72)
        self.reload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reload_btn.clicked.connect(lambda: reload_icons(self))
        self.reload_btn.setToolTip("Обновить")
        top_bar_layout.addWidget(self.reload_btn)

        self.theme_btn = QPushButton("")
        self.theme_btn.setIcon(create_svg_icon(SVG_THEME, c['text_main'], 36))
        self.theme_btn.setIconSize(QSize(36, 36))
        self.theme_btn.setFixedSize(72, 72)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setToolTip("Сменить тему")
        top_bar_layout.addWidget(self.theme_btn)

        self.norm_btn = QPushButton("")
        self.norm_btn.setIcon(create_svg_icon(SVG_NORM_1, c['text_main'], 36))
        self.norm_btn.setIconSize(QSize(36, 36))
        self.norm_btn.setFixedSize(72, 72)
        self.norm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.norm_btn.clicked.connect(lambda: normalize_current(self))
        self.norm_btn.setToolTip("Нормализовать текущую")
        top_bar_layout.addWidget(self.norm_btn)

        self.norm_all_btn = QPushButton("")
        self.norm_all_btn.setIcon(create_svg_icon(SVG_NORM_ALL, c['text_main'], 36))
        self.norm_all_btn.setIconSize(QSize(36, 36))
        self.norm_all_btn.setFixedSize(72, 72)
        self.norm_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.norm_all_btn.clicked.connect(lambda: normalize_all(self))
        self.norm_all_btn.setToolTip("Нормализовать все")
        top_bar_layout.addWidget(self.norm_all_btn)

        self.export_btn = QPushButton("")
        self.export_btn.setIcon(create_svg_icon(SVG_EXPORT, c['text_main'], 36))
        self.export_btn.setIconSize(QSize(36, 36))
        self.export_btn.setFixedSize(72, 72)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(lambda: open_export_dialog(self))
        self.export_btn.setToolTip("Экспорт")
        top_bar_layout.addWidget(self.export_btn)

        top_bar_layout.addStretch(1)
        p_layout.addLayout(top_bar_layout)

        # 2. ИНСТРУМЕНТЫ ЗУМИРОВАНИЯ
        zoom_bar = QHBoxLayout()
        zoom_bar.setContentsMargins(0, 0, 0, 0)
        zoom_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zoom_ctrl = ZoomController()
        self.zoom_ctrl.zoom_in_signal.connect(lambda: self.trigger_zoom(1.2))
        self.zoom_ctrl.zoom_out_signal.connect(lambda: self.trigger_zoom(1.0 / 1.2))
        zoom_bar.addWidget(self.zoom_ctrl)
        p_layout.addLayout(zoom_bar)

        # 3. ПРОСМОТР ИКОНКИ (Холст)
        self.view_canvas = SvgGraphicsView()
        self.view_canvas.zoom_changed_manually.connect(self.zoom_ctrl.set_percent)
        p_layout.addWidget(self.view_canvas, stretch=1)

        # 4. ИМЯ ФАЙЛА
        self.fn_label = ClickableFileNameLabel()
        p_layout.addWidget(self.fn_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 5. КНОПКИ КОПИРОВАНИЯ (ТЕКСТОВЫЕ)
        b_widget = QWidget()
        b_layout = QHBoxLayout(b_widget)
        b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_layout.setSpacing(8)
        self.btns = [
            CopyButton("Copy PNG", "png"),
            CopyButton("Copy Python", "python"),
            CopyButton("Copy HTML", "html"),
            CopyButton("Copy JS", "js"),
            CopyButton("Copy JSON", "json")
        ]
        for btn in self.btns: b_layout.addWidget(btn)
        p_layout.addWidget(b_widget)

        self.p_frame.setMinimumWidth(300)
        self.splitter.addWidget(self.p_frame)
