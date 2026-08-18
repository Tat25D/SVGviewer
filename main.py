import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from utils import get_resource_path

# Импортируем класс главного окна из нового модуля
from viewer_window import SvgViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_res_path = get_resource_path("app_icon.ico")
    if os.path.exists(icon_res_path):
        app.setWindowIcon(QIcon(icon_res_path))

    global viewer
    viewer = SvgViewer()
    viewer.show()
    sys.exit(app.exec())
