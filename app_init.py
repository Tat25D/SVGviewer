import os
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from utils import get_resource_path

def initialize_app_icon(app: QApplication):
    """Безопасно извлекает и устанавливает глобальную иконку для всего процесса приложения."""
    icon_res_path = get_resource_path("app_icon.ico")
    
    if os.path.exists(icon_res_path):
        # Железно фиксируем иконку на уровне операционной системы для панели задач и окон
        app.setWindowIcon(QIcon(icon_res_path))
        
        # Специфичный костыль для Windows: заставляем ОС группировать окна 
        # по ID приложения, чтобы иконка на панели задач применилась на 100%
        if sys.platform == "win32":
            try:
                import ctypes
                myappid = "mycompany.svgviewer.app.1.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass
