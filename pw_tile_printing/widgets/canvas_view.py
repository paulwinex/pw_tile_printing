import math
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from .canvas_scene import CanvasScene


class CanvasView(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.s = CanvasScene(parent=self)
        self.setScene(self.s)
        # self.centerOn(QPointF(0, 0))
        self.panX = None
        self.panY = None
        self.pan = 0
        self.zoom = 1
        self.prev_delta = 0
        self.resize(1000, 800)
        self._init_transform = self.transform()

    @property
    def current_scale(self):
        return self.transform().m11()

    def wheelEvent(self, event):
        d = event.angleDelta().y() / 2880
        if math.copysign(1, d) == math.copysign(1, self.prev_delta):
            self.zoom = 1
        self.zoom += d
        self.prev_delta = d
        self.scale(self.zoom, self.zoom)
        self.s.update()
        return True

    def reset_scale(self):
        self.setTransform(self._init_transform)

    def fit(self):
        if self.s.image_item:
            self.fitInView(self.s.image_item.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_image(self, *args, **kwargs):
        self.s.set_image(*args, **kwargs)
        self.s.setSceneRect(self.viewport().visibleRegion().boundingRect())
        self.fit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.pan = 1
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.panX = event.position().x()
            self.panY = event.position().y()
        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.pan == 1:
            px = event.position().x()
            py = event.position().y()
            self.setInteractive(False)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (px - self.panX))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (py - self.panY))
            self.panX = px
            self.panY = py
            event.accept()
            self.setInteractive(True)
        else:
            QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.pan = 0
        self.setCursor(Qt.CursorShape.ArrowCursor)
        QGraphicsView.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        event.ignore()
