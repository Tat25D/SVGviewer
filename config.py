# Цветовые палитры для тем
THEMES = {
    "dark": {
        "bg_main": "#1e1e1e", "bg_side": "#1a1a1a", "bg_card": "#242424",
        "bg_preview": "#1a1a1a", "border": "#2f2f2f", "border_focus": "#484848",
        "text_main": "#dcddde", "text_muted": "#a3a3a3", "accent": "#7f6df2"
    },
    "light": {
        "bg_main": "#ffffff", "bg_side": "#f5f5f5", "bg_card": "#e0e0e0",
        "bg_preview": "#fafafa", "border": "#ccc", "border_focus": "#999",
        "text_main": "#222222", "text_muted": "#666666", "accent": "#5c49d6"
    }
}

def get_stylesheet(theme_mode):
    """Генерирует стили под выбранную тему."""
    c = THEMES[theme_mode]
    return f"""
        QMainWindow {{ background-color: {c['bg_main']}; }}
        QScrollArea {{ background-color: {c['bg_side']}; border: 1px solid {c['border']}; border-radius: 6px; }}
        QScrollBar:vertical {{ border: none; background: {c['bg_side']}; width: 10px; margin: 0px; }}
        QScrollBar::handle:vertical {{ background: {c['border']}; min-height: 20px; border-radius: 5px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_focus']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        QSplitter::handle {{ background-color: {c['border']}; }}
        QSplitter::handle:hover {{ background-color: {c['border_focus']}; }}
        
        /* Стили для нашей кастомной рамки */
        #CustomTitleBar {{ background-color: {c['bg_side']}; border-bottom: 1px solid {c['border']}; }}
        #TitleLabel {{ color: {c['text_main']}; font-size: 12px; font-weight: bold; }}
        .TitleBtn {{ background: transparent; color: {c['text_muted']}; border: none; font-size: 14px; min-width: 45px; height: 30px; }}
        .TitleBtn:hover {{ background-color: {c['border']}; color: {c['text_main']}; }}
        #CloseBtn:hover {{ background-color: #e81123; color: white; }}
    """
