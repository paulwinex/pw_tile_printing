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

# class ImageItem(QGraphicsRectItem):
#     imageChangedEvent = Signal()
#
#     handleTopLeft = 1
#     handleTopMiddle = 2
#     handleTopRight = 3
#     handleMiddleLeft = 4
#     handleMiddleRight = 5
#     handleBottomLeft = 6
#     handleBottomMiddle = 7
#     handleBottomRight = 8
#
#     handleSize = +30.0
#     handleSpace = -15.0
#
#     handleCursors = {
#         handleTopLeft: Qt.SizeFDiagCursor,
#         # handleTopMiddle: Qt.SizeVerCursor,
#         handleTopRight: Qt.SizeBDiagCursor,
#         # handleMiddleLeft: Qt.SizeHorCursor,
#         # handleMiddleRight: Qt.SizeHorCursor,
#         handleBottomLeft: Qt.SizeBDiagCursor,
#         # handleBottomMiddle: Qt.SizeVerCursor,
#         handleBottomRight: Qt.SizeFDiagCursor,
#     }
#
#     def __init__(self, change_callback, image, *args):
#         super().__init__(*args)
#         self.change_callback = change_callback
#         self.handles = {}
#         self.handleSelected = None
#         self.mousePressPos = None
#         self.mousePressRect = None
#         self.setAcceptHoverEvents(True)
#         self.setFlag(QGraphicsItem.ItemIsMovable, True)
#         self.setFlag(QGraphicsItem.ItemIsSelectable, True)
#         self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
#         self.setFlag(QGraphicsItem.ItemIsFocusable, True)
#         self.pix = QPixmap(image)
#         self.setRect(QRect(0, 0, self.pix.width(), self.pix.height()))
#         self.aspect = self.pix.width() / self.pix.height()
#         self.updateHandlesPos()
#
#     def handleAt(self, point):
#         for k, v, in self.handles.items():
#             if v.contains(point):
#                 return k
#         return None
#
#     def hoverMoveEvent(self, moveEvent):
#         # if self.isSelected():
#         handle = self.handleAt(moveEvent.pos())
#         cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
#         self.setCursor(cursor)
#         super().hoverMoveEvent(moveEvent)
#
#     def hoverLeaveEvent(self, moveEvent):
#         self.setCursor(Qt.ArrowCursor)
#         super().hoverLeaveEvent(moveEvent)
#
#     def mousePressEvent(self, mouseEvent):
#         self.handleSelected = self.handleAt(mouseEvent.pos())
#         if self.handleSelected:
#             self.mousePressPos = mouseEvent.pos()
#             self.mousePressRect = self.boundingRect()
#         super().mousePressEvent(mouseEvent)
#
#     def mouseMoveEvent(self, mouseEvent):
#         if self.handleSelected is not None:
#             self.interactiveResize(mouseEvent.pos())
#         else:
#             super().mouseMoveEvent(mouseEvent)
#
#     def mouseReleaseEvent(self, mouseEvent):
#         super().mouseReleaseEvent(mouseEvent)
#         self.handleSelected = None
#         self.mousePressPos = None
#         self.mousePressRect = None
#         self.update()
#         self.change_callback(dict(
#             size=self.get_current_size(),
#             pos=self.get_current_pos()
#         ))
#
#     def boundingRect(self):
#         o = self.handleSize + self.handleSpace
#         return self.rect().adjusted(-o, -o, o, o)
#
#     def updateHandlesPos(self):
#         s = self.handleSize
#         b = self.boundingRect()
#         # self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
#         # self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
#         # self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
#         # self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
#         # self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
#         # self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
#         # self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
#         self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)
#
#     def apply_aspect(self, rect: QRect, corner):
#
#         rect.setWidth(int(rect.height() * self.aspect))
#         if corner == 'lt':
#             rect.moveBottomRight(self.rect().bottomRight())
#         elif corner == 'rt':
#             rect.moveBottomLeft(self.rect().bottomLeft())
#         elif corner == 'lb':
#             rect.moveTopRight(self.rect().topRight())
#         elif corner == 'rb':
#             rect.moveTopLeft(self.rect().topLeft())
#         return rect
#
#     def update_aspect(self):
#         self.aspect = self.rect().width() / self.rect().height()
#         # self.updateHandlesPos()
#
#     def interactiveResize(self, mousePos):
#         offset = self.handleSize + self.handleSpace
#         boundingRect = self.boundingRect()
#         rect = self.rect()
#         diff = QPointF(0, 0)
#
#         self.prepareGeometryChange()
#
#         # if self.handleSelected == self.handleTopLeft:
#         #     fromX = self.mousePressRect.left()
#         #     fromY = self.mousePressRect.top()
#         #     toX = fromX + mousePos.x() - self.mousePressPos.x()
#         #     toY = fromY + mousePos.y() - self.mousePressPos.y()
#         #     diff.setX(toX - fromX)
#         #     diff.setY(toY - fromY)
#         #     boundingRect.setLeft(toX)
#         #     boundingRect.setTop(toY)
#         #     rect.setLeft(boundingRect.left() + offset)
#         #     rect.setTop(boundingRect.top() + offset)
#         #     self.setRect(self.apply_aspect(rect, 'lt'))
#
#         # elif self.handleSelected == self.handleTopMiddle:
#         #     fromY = self.mousePressRect.top()
#         #     toY = fromY + mousePos.y() - self.mousePressPos.y()
#         #     diff.setY(toY - fromY)
#         #     boundingRect.setTop(toY)
#         #     rect.setTop(boundingRect.top() + offset)
#         #     self.setRect(rect)
#         #     self.update_aspect()
#
#         # elif self.handleSelected == self.handleTopRight:
#         #     fromX = self.mousePressRect.right()
#         #     fromY = self.mousePressRect.top()
#         #     toX = fromX + mousePos.x() - self.mousePressPos.x()
#         #     toY = fromY + mousePos.y() - self.mousePressPos.y()
#         #     diff.setX(toX - fromX)
#         #     diff.setY(toY - fromY)
#         #     boundingRect.setRight(toX)
#         #     boundingRect.setTop(toY)
#         #     rect.setRight(boundingRect.right() - offset)
#         #     rect.setTop(boundingRect.top() + offset)
#         #     self.setRect(self.apply_aspect(rect, 'rt'))
#
#         # elif self.handleSelected == self.handleMiddleLeft:
#         #     fromX = self.mousePressRect.left()
#         #     toX = fromX + mousePos.x() - self.mousePressPos.x()
#         #     diff.setX(toX - fromX)
#         #     boundingRect.setLeft(toX)
#         #     rect.setLeft(boundingRect.left() + offset)
#         #     self.setRect(rect)
#         #     self.update_aspect()
#
#         # elif self.handleSelected == self.handleMiddleRight:
#         #     fromX = self.mousePressRect.right()
#         #     toX = fromX + mousePos.x() - self.mousePressPos.x()
#         #     diff.setX(toX - fromX)
#         #     boundingRect.setRight(toX)
#         #     rect.setRight(boundingRect.right() - offset)
#         #     self.setRect(rect)
#         #     self.update_aspect()
#
#         # elif self.handleSelected == self.handleBottomLeft:
#         #     fromX = self.mousePressRect.left()
#         #     fromY = self.mousePressRect.bottom()
#         #     toX = fromX + mousePos.x() - self.mousePressPos.x()
#         #     toY = fromY + mousePos.y() - self.mousePressPos.y()
#         #     diff.setX(toX - fromX)
#         #     diff.setY(toY - fromY)
#         #     boundingRect.setLeft(toX)
#         #     boundingRect.setBottom(toY)
#         #     rect.setLeft(boundingRect.left() + offset)
#         #     rect.setBottom(boundingRect.bottom() - offset)
#         #     self.setRect(self.apply_aspect(rect, 'lb'))
#
#         # elif self.handleSelected == self.handleBottomMiddle:
#         #     fromY = self.mousePressRect.bottom()
#         #     toY = fromY + mousePos.y() - self.mousePressPos.y()
#         #     diff.setY(toY - fromY)
#         #     boundingRect.setBottom(toY)
#         #     rect.setBottom(boundingRect.bottom() - offset)
#         #     self.setRect(rect)
#         #     self.update_aspect()
#
#         if self.handleSelected == self.handleBottomRight:
#             fromX = self.mousePressRect.right()
#             fromY = self.mousePressRect.bottom()
#             toX = fromX + mousePos.x() - self.mousePressPos.x()
#             toY = fromY + mousePos.y() - self.mousePressPos.y()
#             diff.setX(toX - fromX)
#             diff.setY(toY - fromY)
#             boundingRect.setRight(toX)
#             boundingRect.setBottom(toY)
#             rect.setRight(boundingRect.right() - offset)
#             rect.setBottom(boundingRect.bottom() - offset)
#             self.setRect(self.apply_aspect(rect, 'rb'))
#         self.updateHandlesPos()
#
#     def set_scale(self, value):
#         rect: QRectF = self.boundingRect()
#         rect.setWidth(rect.width()*value)
#         rect.setHeight(rect.height()*value)
#         self.setRect(self.apply_aspect(rect, 'rb'))
#         self.updateHandlesPos()
#
#     def shape(self):
#         path = QPainterPath()
#         path.addRect(self.rect())
#         if self.isSelected():
#             for shape in self.handles.values():
#                 path.addEllipse(shape)
#         return path
#
#     def paint(self, painter, option, widget=None):
#         painter.drawPixmap(self.rect().toRect(), self.pix)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
#         painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
#         for handle, rect in self.handles.items():
#             if self.handleSelected is None or handle == self.handleSelected:
#                 painter.drawEllipse(rect)
#
#     def get_current_size(self):
#         s: QSize = self.rect().size()
#         return s.width(), s.height()
#
#     def get_current_pos(self):
#         return self.pos().x(), self.pos().y()