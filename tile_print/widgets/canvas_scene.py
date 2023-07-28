from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from .image_item import ImageItem
from ..tiler import Tiler



class CanvasScene(QGraphicsScene):
    gridSize = 50, 50
    image_item = None
    padding = (0, 0, 0, 0)
    pos_under_cursor = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSceneRect(-3000, -2000, 6000, 4000)

    def drawBackground(self, painter: QPainter, rect: QRect):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, QBrush(QColor(30, 30, 30)))
        left = int(rect.left()) - (int(rect.left()) % self.gridSize[0])
        top = int(rect.top()) - (int(rect.top()) % self.gridSize[1])
        if self.image_item:
            image_rect = self.image_item.boundingRect()
            # image_rect.moveTo(self.image_item.pos().toPoint())
            paper_rects = self.get_paper_rects(image_rect, self.gridSize)
            painter.save()
            painter.setBrush(QBrush(QColor('#444444')))
            for paper_rect in paper_rects:
                painter.drawRect(paper_rect)
            # painter.setBrush(Qt.NoBrush)
            # painter.setPen(QPen(QBrush(QColor('#555555')), 3, Qt.SolidLine))
            # painter.drawRect(image_rect)
            painter.restore()

        lines = []
        right = int(rect.right())
        bottom = int(rect.bottom())
        for x in range(left, right, self.gridSize[0]):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, bottom, self.gridSize[1]):
            lines.append(QLineF(rect.left(), y, rect.right(), y))

        painter.setPen(QPen(QBrush(QColor(50, 50, 50)), 1, Qt.PenStyle.SolidLine))
        painter.drawLines(lines)

        if self.pos_under_cursor:
            if not self.itemAt(self.pos_under_cursor, QTransform()):
                x = (self.gridSize[0]*int(self.pos_under_cursor.x() // self.gridSize[0]))
                y = (self.gridSize[1]*int(self.pos_under_cursor.y() // self.gridSize[1]))
                page_rect = QRect(x, y, *self.gridSize)
                page_rect = page_rect.adjusted(-self.padding[0], -self.padding[1], self.padding[2], self.padding[3])
                painter.setPen(QPen(QBrush(QColor(150, 150, 150, 150)), 3, Qt.PenStyle.SolidLine))
                painter.drawRect(page_rect)

        # r = self.sceneRect()
        # painter.setBrush(Qt.NoBrush)
        # painter.setPen(QPen(QBrush(QColor('#ff0000')), 3, Qt.SolidLine))
        # painter.drawRect(r.adjusted(10, 10, -10, -10))

    def draw_pages(self, **kwargs):
        grid_size = kwargs.get('paper_size')
        self.gridSize = Tiler.orient_page(grid_size, kwargs['orientation'])
        self.padding = kwargs['padding']
        self.update()

    def get_paper_rects(self, image_rect, grid_size):
        x_count = int((image_rect.width()+image_rect.x()) // grid_size[0])+1
        y_count = int((image_rect.height()+image_rect.y()) // grid_size[1])+1
        paper_rects = []
        for x in range(x_count):
            for y in range(y_count):
                paper_rect = QRect(x*grid_size[0], y*grid_size[1], *grid_size)
                if not paper_rect.intersects(image_rect):
                    continue
                paper_rects.append(paper_rect)
        return paper_rects

    def set_paper_size(self, paper_size, padding):
        self.gridSize = paper_size
        self.padding = padding

    def set_image(self, image_path):
        if self.image_item:
            self.removeItem(self.image_item)
            self.image_item = None
        if image_path:
            self.image_item = ImageItem(str(image_path))
            self.addItem(self.image_item)
        self.update()

    def set_image_scale(self, factor):
        if self.image_item:
            self.image_item.set_scale(factor)
            self.update()

    def mouseMoveEvent(self, event):
        self.pos_under_cursor = event.scenePos()
        self.update()
        return super().mouseMoveEvent(event)

# class CanvasScene(QGraphicsScene):
#     gridSize = 50, 50
#     tilesChangedEvent = Signal(dict)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.image_item = None
#         # self.image_item.imageChangedEvent.connect(self.on_image_changed)
#         self.padding = [0, 0, 0, 0]
#         self.pages = []
#         self.setSceneRect(QRect(0, 0, 6000, 6000))
#         self.pos_under_cursor = None
#         # self.addItem(self.image_item)
#         # self.overlay = OverlayItem()
#         # self.addItem(self.overlay)
#
#     def set_image(self, image_path):
#         if self.image_item:
#             self.removeItem(self.image_item)
#             self.image_item = None
#         if image_path:
#             self.image_item = ImageItem(self.on_image_changed, str(image_path))
#             self.addItem(self.image_item)
#         self.update()
#
#     def scale_image(self, scale, *args):
#         print(scale)
#         if self.image_item:
#             self.image_item.set_scale(scale)
#             self.update()
#
#     def drawBackground(self, painter: QPainter, rect: QRect):
#         painter.setPen(Qt.NoPen)
#         painter.fillRect(rect, QBrush(QColor(30,30,30)))
#         left = int(rect.left()) - (int(rect.left()) % self.gridSize[0])
#         top = int(rect.top()) - (int(rect.top()) % self.gridSize[1])
#         if self.image_item:
#             image_rect = self.image_item.boundingRect()
#             image_rect.moveTo(self.image_item.pos())
#             paper_rects = self.get_paper_rects(image_rect, self.gridSize)
#             painter.save()
#             painter.setBrush(QBrush(QColor('#444444')))
#             for paper_rect in paper_rects:
#                 painter.drawRect(paper_rect)
#             painter.setBrush(Qt.NoBrush)
#             painter.setPen(QPen(QBrush(QColor('#555555')), 3, Qt.SolidLine))
#             painter.drawRect(image_rect)
#             painter.restore()
#
#         lines = []
#         right = int(rect.right())
#         bottom = int(rect.bottom())
#         for x in range(left, right, self.gridSize[0]):
#             lines.append(QLineF(x, rect.top(), x, rect.bottom()))
#         for y in range(top, bottom, self.gridSize[1]):
#             lines.append(QLineF(rect.left(), y, rect.right(), y))
#
#         painter.setPen(QPen(QBrush(QColor(50,50,50)), 1, Qt.SolidLine))
#         painter.drawLines(lines)
#
#         if self.pos_under_cursor:
#             if not self.itemAt(self.pos_under_cursor, QTransform()):
#                 x = (self.gridSize[0]*int(self.pos_under_cursor.x() // self.gridSize[0]))
#                 y = (self.gridSize[1]*int(self.pos_under_cursor.y() // self.gridSize[1]))
#                 page_rect = QRect(x, y, *self.gridSize)
#                 page_rect = page_rect.adjusted(-self.padding[0], -self.padding[1], self.padding[2], self.padding[3])
#                 painter.setPen(QPen(QBrush(QColor(150, 150, 150, 150)), 3, Qt.SolidLine))
#                 painter.drawRect(page_rect)
#
#     def get_paper_rects(self, image_rect, grid_size):
#         x_count = int((image_rect.width()+image_rect.x()) // grid_size[0])+1
#         y_count = int((image_rect.height()+image_rect.y()) // grid_size[1])+1
#         paper_rects = []
#         for x in range(x_count):
#             for y in range(y_count):
#                 paper_rect = QRect(x*grid_size[0], y*grid_size[1], *grid_size)
#                 if not paper_rect.intersects(image_rect.toRect()):
#                     continue
#                 paper_rects.append(paper_rect)
#         return paper_rects
#
#     def draw_pages(self, **kwargs):
#         while self.pages:
#             self.removeItem(self.pages.pop())
#         grid_size = kwargs.get('paper_size')
#         self.gridSize = Tiler.orient_page(grid_size, kwargs['orientation'])
#         self.padding = kwargs['padding']
#         self.update()
#
#     def mouseMoveEvent(self, event):
#         self.pos_under_cursor = event.scenePos()
#         self.update()
#         return super().mouseMoveEvent(event)
#
#     def on_image_changed(self, image_geo):
#         pass
        # print(image_geo)

# class OverlayItem(QGraphicsItem):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setAcceptHoverEvents(True)

    # def hoverEnterEvent(self, event):
    #     self.setCursor(Qt.PointingHandCursor)

    # def hoverLeaveEvent(self, event):
    #     self.setCursor(Qt.ArrowCursor)

    # def paint(self, painter, option, widget):
    #     pass
    #
    # def boundingRect(self):
    #     return self.scene().sceneRect()


    # def mouseDoubleClickEvent(self, event):
    #     self.addNode(event.scenePos())

    # def mouseReleaseEvent(self, event):
    #     # curr = self.itemAt(event.scenePos())
    #     # if curr:
    #     #     curr.adjustPos()
    #     for i in sorted(self.items(), key=lambda x:x.pos().y()):
    #         if i.isSelected():
    #             i.adjustPos()
    #         i.getCornerPoints()
    #     super().mouseReleaseEvent(event)


    # def addPage(self, pos=None):
    #     if not pos:
    #         pos = QPoint(0,0)
    #     item = CanvasPageItem(self.gridSize, len(self.items()))
    #     self.addItem(item)
    #     item.setPos(pos)
    #     item.adjustPos()

    # def removeNodes(self):
    #     for i in self.selectedItems():
    #         self.removeItem(i)

    # def snapPoint(self, item):
    #     items = self.items()
    #     items.remove(item)
    #     pointsArray = []
    #     for i in items:
    #         pointsArray += i.getCornerPoints()
    #
    #     p1, p2 = item.getCornerPoints()
    #     for i in pointsArray:
    #         if (i-p1).length() < self.snapDistance:
    #             return i - p1
    #         if (i-p2).length() < self.snapDistance:
    #             return i - p2
