from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QLineF, QRectF
from PyQt6.QtGui import QCursor, QPainter, QMouseEvent, QWheelEvent, QResizeEvent, QPen, QColor

class SvgGraphicsView(QGraphicsView):
    zoom_changed_manually = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setStyleSheet("background: transparent; border: none;")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.is_panning = False
        self.pan_start_pos = QPoint()

        # --- КВАДРАТЫ РАЗНЫХ РАЗМЕРОВ (64px, 128px, 256px, 512px, 1024px, 2048px) ---
        self.ref_sizes = [64, 128, 256, 512, 1024, 2048]
        self.ref_rects = []
        ref_pen = QPen(QColor("#333333"), 1)
        ref_pen.setStyle(Qt.PenStyle.DotLine)
        ref_pen.setCosmetic(True)

        for size in self.ref_sizes:
            half = size / 2.0
            rect = QGraphicsRectItem(QRectF(-half, -half, size, size))
            rect.setPen(ref_pen)
            rect.setZValue(0)
            self.scene.addItem(rect)
            self.ref_rects.append(rect)

        # --- НАСТРАИВАЕМАЯ РАМКА И КРЕСТИК (100px по умолчанию) ---
        self.marker_size = 100
        half_size = self.marker_size / 2.0

        line_pen = QPen(QColor("#4A4A4A"), 1)
        line_pen.setCosmetic(True)

        self.h_line = QGraphicsLineItem(QLineF(-half_size, 0, half_size, 0))
        self.h_line.setPen(line_pen)
        self.h_line.setZValue(0)

        self.v_line = QGraphicsLineItem(QLineF(0, -half_size, 0, half_size))
        self.v_line.setPen(line_pen)
        self.v_line.setZValue(0)

        dash_pen = QPen(QColor("#4A4A4A"), 1)
        dash_pen.setStyle(Qt.PenStyle.DashLine)
        dash_pen.setCosmetic(True)
        self.bounding_rect = QGraphicsRectItem(QRectF(-half_size, -half_size, self.marker_size, self.marker_size))
        self.bounding_rect.setPen(dash_pen)
        self.bounding_rect.setZValue(0)

        self.scene.addItem(self.h_line)
        self.scene.addItem(self.v_line)
        self.scene.addItem(self.bounding_rect)

        self.pixmap_item.setZValue(1)

    def scrollContentsBy(self, dx, dy): pass

    def recenter(self):
        s = self.transform().m11()
        if s == 0: return

        self.resetTransform()
        self.scale(s, s)

        view_w = self.viewport().width()
        view_h = self.viewport().height()

        dx = (view_w / 2.0) / s
        dy = (view_h / 2.0) / s

        self.translate(dx, dy)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.recenter()

    def set_pixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(-1000000, -1000000, 2000000, 2000000)
        self.pixmap_item.setPos(-pixmap.width() / 2, -pixmap.height() / 2)

    def wheelEvent(self, event: QWheelEvent):
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        self.scale(zoom_factor, zoom_factor)
        self.zoom_changed_manually.emit(self.transform().m11())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning, self.pan_start_pos = True, event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_panning:
            delta = (event.pos() - self.pan_start_pos) / self.transform().m11()
            self.pan_start_pos = event.pos()
            self.translate(delta.x(), delta.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

class ZoomController(QWidget):
    zoom_in_signal, zoom_out_signal = pyqtSignal(), pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.m_btn = QPushButton("-")
        self.m_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.m_btn.clicked.connect(self.zoom_out_signal.emit)

        self.lbl_percent = QLabel("100%")
        self.lbl_percent.setFixedWidth(60)
        self.lbl_percent.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.p_btn = QPushButton("+")
        self.p_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.p_btn.clicked.connect(self.zoom_in_signal.emit)

        layout.addWidget(self.m_btn); layout.addWidget(self.lbl_percent); layout.addWidget(self.p_btn)

    def set_percent(self, current_transform_m11):
        self.lbl_percent.setText(f"{int(current_transform_m11 * 100)}%")
