from PyQt6.QtWidgets import QLayout, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, QRect, QSize

class FlowLayout(QLayout):
    """Кастомный менеджер компоновки для создания адаптивной сетки элементов."""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if margin >= 0:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self._item_list = []

    def __del__(self):
        while self.takeAt(0): pass

    def addItem(self, item): self._item_list.append(item)
    def count(self): return len(self._item_list)
    def itemAt(self, index): return self._item_list[index] if 0 <= index < len(self._item_list) else None
    def takeAt(self, index): return self._item_list.pop(index) if 0 <= index < len(self._item_list) else None
    def expandingDirections(self): return Qt.Orientations(Qt.Orientation.Horizontal | Qt.Orientation.Vertical)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, width): return self._do_layout(QRect(0, 0, width, 0), True)
    def setGeometry(self, rect): super().setGeometry(rect); self._do_layout(rect, False)
    def sizeHint(self): return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list: size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect, test_only):
        l, t, r, b = self.getContentsMargins()
        eff_rect = rect.adjusted(+l, +t, -r, -b)
        x, y, line_height = eff_rect.x(), eff_rect.y(), 0

        for item in self._item_list:
            w = item.widget()
            if w and not w.isVisible(): continue
            sx = self.spacing() if self.spacing() != -1 else w.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            sy = self.spacing() if self.spacing() != -1 else w.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)

            next_x = x + item.sizeHint().width() + sx
            if next_x - sx > eff_rect.right() and line_height > 0:
                x, y = eff_rect.x(), y + line_height + sy
                next_x = x + item.sizeHint().width() + sx
                line_height = 0

            if not test_only: item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x, line_height = next_x, max(line_height, item.sizeHint().height())

        return y + line_height - eff_rect.y() + t + b
