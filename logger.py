import os
from PyQt6.QtGui import QImageReader

def run_icon_diagnostics(icon_res_path):
    """Выводит подробные технические метрики и структуру слоев иконки в терминал."""
    print("\n" + "="*50)
    print(" ДИАГНОСТИКА СИСТЕМНОЙ ИКОНКИ ПРИЛОЖЕНИЯ")
    print("="*50)
    print(f"1. Целевой путь файла: {icon_res_path}")
    
    file_exists = os.path.exists(icon_res_path)
    print(f"2. Файл физически существует: {file_exists}")
    
    if file_exists:
        file_size = os.path.getsize(icon_res_path)
        print(f"3. Размер файла на диске: {file_size} байт")
        
        # Проверяем структуру через движок QImageReader
        reader = QImageReader(icon_res_path)
        format_name = reader.format().data().decode('utf-8', 'ignore')
        print(f"4. Формат, определенный Qt: {format_name}")
        
        # Считываем доступные размеры внутри .ico контейнера
        icon_sizes = reader.supportedSizes()
        print(f"5. Найдено внутренних слоев (разрешений): {len(icon_sizes)}")
        for idx, s in enumerate(icon_sizes):
            print(f"   -> Слой [{idx}]: {s.width()}x{s.height()} px")
    else:
        print("[ВНИМАНИЕ] Файл иконки не найден. Проверьте сборку PyInstaller!")
    print("="*50 + "\n")
