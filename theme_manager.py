from config import THEMES
from utils import (create_svg_icon, SVG_BAR_UP, SVG_BAR_DOWN, SVG_COMPACT_UP, SVG_COMPACT_DOWN,
                   SVG_REFRESH, SVG_THEME, SVG_EXPORT, SVG_NORM_1, SVG_NORM_ALL)

RU_TO_EN_MAP = str.maketrans(
    "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,",
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?"
)

def fix_search_layout(window):
    current_text = window.search_input.text()
    fixed_text = current_text.translate(RU_TO_EN_MAP)
    window.search_input.setText(fixed_text)

def apply_widget_theme_styles(window):
    c = THEMES[window.theme_mode]
    txt_color = c['text_main']

    window.search_input.setStyleSheet(f"QLineEdit {{ background-color: {c['bg_card']}; color: {c['text_main']}; border: 1px solid {c['border']}; border-radius: 6px; padding: 8px; padding-right: 95px; }}")
    window.clear_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {c['text_muted']}; border: none; font-size: 13px; font-weight: bold; min-width: 30px; height: 20px; }} QPushButton:hover {{ color: {c['text_main']}; }}")
    window.layout_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {c['text_muted']}; border: none; font-size: 13px; font-weight: bold; min-width: 45px; height: 20px; }} QPushButton:hover {{ color: {c['text_main']}; }}")

    # Квадратные кнопки с иконками (72x72)
    btn_style = f"QPushButton {{ background-color: {c['bg_card']}; border: 1px solid {c['border']}; border-radius: 6px; }} QPushButton:hover {{ background-color: {c['border']}; border: 1px solid {c['border_focus']}; }}"
    window.theme_btn.setStyleSheet(btn_style)
    window.export_btn.setStyleSheet(btn_style)
    window.reload_btn.setStyleSheet(btn_style)
    window.norm_btn.setStyleSheet(btn_style)
    window.norm_all_btn.setStyleSheet(btn_style)

    # Обновление цвета иконок (36x36)
    window.reload_btn.setIcon(create_svg_icon(SVG_REFRESH, txt_color, 36))
    window.theme_btn.setIcon(create_svg_icon(SVG_THEME, txt_color, 36))
    window.export_btn.setIcon(create_svg_icon(SVG_EXPORT, txt_color, 36))
    window.norm_btn.setIcon(create_svg_icon(SVG_NORM_1, txt_color, 36))
    window.norm_all_btn.setIcon(create_svg_icon(SVG_NORM_ALL, txt_color, 36))

    # Кнопки копирования (ТЕКСТОВЫЕ)
    copy_btn_style = f"QPushButton {{ background-color: {c['bg_card']}; color: {c['text_main']}; border: 1px solid {c['border']}; border-radius: 4px; padding: 6px 12px; font-size: 12px; font-weight: bold; }}"
    for btn in window.btns:
        btn.setStyleSheet(copy_btn_style)

    # Навигационные кнопки
    nav_btn_style = f"""
        QPushButton {{
            background-color: {c['bg_card']};
            border: 1px solid {c['border']};
            border-radius: 0px;
            margin-left: -1px;
        }}
        QPushButton#NavFirstBtn {{
            margin-left: 0px;
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
        }}
        QPushButton#NavLastBtn {{
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QPushButton:hover {{
            background-color: {c['border']};
            border: 1px solid {c['border_focus']};
        }}
    """
    window.btn_top.setStyleSheet(nav_btn_style)
    window.btn_page_up.setStyleSheet(nav_btn_style)
    window.btn_page_down.setStyleSheet(nav_btn_style)
    window.btn_bottom.setStyleSheet(nav_btn_style)

    window.btn_top.setIcon(create_svg_icon(SVG_BAR_UP, txt_color, 28))
    window.btn_page_up.setIcon(create_svg_icon(SVG_COMPACT_UP, txt_color, 28))
    window.btn_page_down.setIcon(create_svg_icon(SVG_COMPACT_DOWN, txt_color, 28))
    window.btn_bottom.setIcon(create_svg_icon(SVG_BAR_DOWN, txt_color, 28))

    window.g_container.setStyleSheet(f"background-color: {c['bg_side']};")
    window.p_frame.setStyleSheet(f"QFrame {{ background-color: {c['bg_preview']}; border: 1px solid {c['border']}; border-radius: 6px; }}")
    window.fn_label.setStyleSheet(f"QLabel {{ color: {c['accent']}; font-size: 14px; text-decoration: underline; background: transparent; padding: 5px; }}")

    zoom_btn_style = f"QPushButton {{ background-color: {c['bg_card']}; color: {c['text_main']}; border: 1px solid {c['border']}; border-radius: 6px; min-width: 40px; max-width: 40px; height: 36px; font-size: 18px; font-weight: bold; }}"
    window.zoom_ctrl.m_btn.setStyleSheet(zoom_btn_style)
    window.zoom_ctrl.p_btn.setStyleSheet(zoom_btn_style)
    window.zoom_ctrl.lbl_percent.setStyleSheet(f"color: {c['text_main']}; font-size: 15px; font-weight: bold;")
