from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from .canvas_scene import CanvasScene


class CanvasView(QGraphicsView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.s = CanvasScene(parent=self)
        self.setScene(self.s)
        # self.img = ImageItem('/home/paul/Desktop/pyinstrument.png')
        # self.s.addItem(self.img)
        self.centerOn(QPointF(0, 0))
        self.panX = None
        self.panY = None
        self.pan = 0
        self.zoom = 1
        self.prev_delta = 0
        self.resize(1000, 800)

    def wheelEvent(self, event):
        import math
        d = event.angleDelta().y() / 2880
        if math.copysign(1, d) == math.copysign(1, self.prev_delta):
            self.zoom = 1
        self.zoom += d
        self.prev_delta = d
        self.scale(self.zoom, self.zoom)
        self.s.setSceneRect(self.viewport().visibleRegion().boundingRect())
        self.scene().update()
        return True

    def reset_scale(self):
        self.scale(1, 1)

    def set_image(self, *args, **kwargs):
        self.s.set_image(*args, **kwargs)

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


# class CanvasView(QGraphicsView):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.sc = CanvasScene(parent=self)
#         self.setScene(self.sc)
#         self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.centerOn(QPointF(0, 0))
#         self.panX = None
#         self.panY = None
#         self.pan = 0
#         self.zoom = 1
#         self.prev_delta = 0
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.MiddleButton:
#             self.pan = 1
#             self.setCursor(Qt.CursorShape.ClosedHandCursor)
#             self.panX = event.x()
#             self.panY = event.y()
#         QGraphicsView.mousePressEvent(self, event)
#
#     def mouseMoveEvent(self, event):
#         if self.pan == 1:
#             self.setInteractive(False)
#             self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self.panX))
#             self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self.panY))
#             self.panX = event.x()
#             self.panY = event.y()
#             event.accept()
#             self.setInteractive(True)
#         else:
#             QGraphicsView.mouseMoveEvent(self, event)
#
#     def mouseReleaseEvent(self, event):
#         self.pan = 0
#         self.setCursor(Qt.CursorShape.ArrowCursor)
#         QGraphicsView.mouseReleaseEvent(self, event)
#
#     def wheelEvent(self, event):
#         import math
#         d = event.angleDelta().y() / 2880
#         if math.copysign(1, d) == math.copysign(1, self.prev_delta):
#             self.zoom = 1
#         self.zoom += d
#         self.prev_delta = d
#         self.scale(self.zoom, self.zoom)
#         self.scene().update()
#         return True
