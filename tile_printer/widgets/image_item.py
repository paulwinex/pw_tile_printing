from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class ImageItem(QGraphicsItem):
    handle_size = 20, 20

    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.pix = QPixmap(image)
        self.draw_handle = False
        self._is_resized = False
        self._orig_pos_point = None
        self._press_point = None
        self._orig_size = None
        self._aspect_ratio = self.pix.width() / self.pix.height()
        self.w = self.pix.width()
        self.h = self.pix.height()
        self.x = 0
        self.y = 0

    def boundingRect(self):
        rect = QRect(self.x, self.y, self.w, self.h)
        return rect

    def paint(self, painter, option, widget=None):
        painter.drawPixmap(self.boundingRect(), self.pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        opacity = 155 if self.draw_handle else 50
        painter.setBrush(QBrush(QColor(255, 0, 0, opacity)))
        painter.setPen(Qt.PenStyle.NoPen)
        handle_rect = QRect(0, 0, *self.handle_size)
        handle_rect.moveBottomRight(self.boundingRect().bottomRight())
        painter.drawRect(handle_rect)

    def hoverMoveEvent(self, moveEvent):
        pos = moveEvent.pos()
        handle_rect = QRect(0, 0, *self.handle_size)
        handle_rect.moveBottomRight(self.boundingRect().bottomRight())
        if handle_rect.contains(pos.toPoint()):
            self.draw_handle = True
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.draw_handle = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.draw_handle = False
        self.update()
        super().hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        pos = mouseEvent.pos()
        handle_rect = QRect(0, 0, *self.handle_size)
        handle_rect.moveBottomRight(self.boundingRect().bottomRight())
        if handle_rect.contains(pos.toPoint()):
            self._is_resized = True
            self._orig_size = self.w, self.h
        else:
            self._orig_pos_point = QPoint(self.x, self.y)
        self._press_point = pos
        return super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if (mouseEvent.buttons() & Qt.MouseButton.LeftButton) != 0:
            self.prepareGeometryChange()
            current_pos = mouseEvent.pos().toPoint()
            x_delta = self._press_point.x() - current_pos.x()
            y_delta = self._press_point.y() - current_pos.y()
            if self._is_resized:
                self.w = self._orig_size[0] - x_delta
                self.h = self._orig_size[1] - y_delta
                self.w = int(self.h * self._aspect_ratio)
            else:
                self.x = self._orig_pos_point.x() - x_delta
                self.y = self._orig_pos_point.y() - y_delta
            self.update()
        return super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        super().mouseReleaseEvent(mouseEvent)
        self._is_resized = False
        self.update()
        return super().mouseReleaseEvent(mouseEvent)

    def set_scale(self, factor):
        self.w = int(self.w * factor)
        self.h = int(self.h * factor)
        self.update()

    def get_image_info(self):
        return dict(
            image_size=(self.w, self.h),
            offset=(self.x, self.y)
        )
