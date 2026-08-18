import os
import sys
import ctypes
from utils import get_resource_path

def apply_windows_dwm_patch(win_id):
    """Исправляет баг Windows DWM: принудительно включает темную рамку и возвращает иконку в угол."""
    if sys.platform != "win32":
        return
        
    try:
        hwnd = int(win_id)
        
        # 1. Задаем оригинальный темный цвет заголовка Obsidian
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        rendering_val = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(rendering_val), ctypes.sizeof(rendering_val))
        
        # 2. Пробиваем блокировку иконки через расширенный стиль модального окна
        GWL_EXSTYLE = -20
        WS_EX_DLGMODALFRAME = 0x00000001
        current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, current_style | WS_EX_DLGMODALFRAME)
        
        # 3. Насильно шлем системные сообщения на установку мелкой и крупной иконки заголовка
        icon_res_path = get_resource_path("app_icon.ico")
        if os.path.exists(icon_res_path):
            WM_SETICON = 0x0080
            h_icon = ctypes.windll.user32.LoadImageW(0, icon_res_path, 1, 0, 0, 0x0010)
            if h_icon:
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, h_icon)
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, h_icon)
                
        # 4. Принудительно заставляем Windows мгновенно обновить заголовок окна
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0020 | 0x0002 | 0x0001 | 0x0004)
    except Exception:
        pass
