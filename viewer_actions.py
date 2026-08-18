import os
import sys
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer
from utils import render_svg_with_tint, create_svg_icon, SVG_NORM_1, SVG_NORM_ALL, SVG_EXPORT, THEMES
from ui_components import SvgIconCell
from export_dialog import ExportDialog

def load_svg_icons(window):
    app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    svg_dir = os.path.join(app_dir, "SVG")

    if not os.path.exists(svg_dir):
        os.makedirs(svg_dir, exist_ok=True)
        with open(os.path.join(svg_dir, "circle.svg"), "w") as f:
            f.write('<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="4"/></svg>')

    svg_files = [f for f in os.listdir(svg_dir) if f.lower().endswith('.svg')]
    for f_name in svg_files:
        f_path = os.path.join(svg_dir, f_name)
        disp_name = f_name if len(f_name) < 12 else f_name[:9] + "..."
        cell = SvgIconCell(f_path, disp_name, window.show_preview, window)
        window.flow_layout.addWidget(cell)
        window.icon_cells.append(cell)
        cell.img_lbl.setPixmap(render_svg_with_tint(f_path, 64, 64, window.theme_mode))

    if window.icon_cells:
        window.show_preview(window.icon_cells[0].file_path)

def reload_icons(window):
    while window.flow_layout.count():
        item = window.flow_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
    window.icon_cells.clear()
    load_svg_icons(window)

def open_export_dialog(window):
    if not window.current_file_path:
        QMessageBox.warning(window, "Внимание", "Сначала выберите иконку для предпросмотра!")
        return
    dialog = ExportDialog(window.current_file_path, window.theme_mode, window)
    if dialog.exec():
        animate_button(window.export_btn)

def normalize_svg_file(file_path):
    try:
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
        tree = ET.parse(file_path)
        root = tree.getroot()

        vb = root.get('viewBox')
        if not vb:
            w = root.get('width', '1024').replace('px', '').strip()
            h = root.get('height', '1024').replace('px', '').strip()
            try:
                float(w); float(h)
                vb = f"0 0 {w} {h}"
            except ValueError:
                vb = "0 0 1024 1024"
            root.set('viewBox', vb)

        root.set('width', '1024')
        root.set('height', '1024')
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        return True
    except Exception as e:
        print(f"Ошибка нормализации {file_path}: {e}")
        return False

def normalize_current(window):
    if not window.current_file_path:
        animate_button(window.norm_btn)
        return
    if normalize_svg_file(window.current_file_path):
        window.update_preview(reset_zoom=True)
    animate_button(window.norm_btn)

def normalize_all(window):
    app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    svg_dir = os.path.join(app_dir, "SVG")
    if not os.path.exists(svg_dir):
        animate_button(window.norm_all_btn)
        return

    svg_files = [f for f in os.listdir(svg_dir) if f.lower().endswith('.svg')]
    for f_name in svg_files:
        f_path = os.path.join(svg_dir, f_name)
        normalize_svg_file(f_path)

    reload_icons(window)
    animate_button(window.norm_all_btn)

# Единая функция анимации кнопки (меняет только фон, иконку не трогает)
def animate_button(btn):
    original_style = btn.styleSheet()
    green_style = "QPushButton { background-color: #28a745; border: 1px solid #1e7e34; border-radius: 6px; } QPushButton:hover { background-color: #218838; }"

    btn.setStyleSheet(green_style)

    QTimer.singleShot(2000, lambda: (
        btn.setStyleSheet(original_style)
    ))
