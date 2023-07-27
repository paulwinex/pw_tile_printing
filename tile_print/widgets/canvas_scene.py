from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from .page_item import CanvasPageItem
from .image_item import ImageItem
from ..tiler import Tiler


class CanvasScene(QGraphicsScene):
    gridSize = 50, 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_item = None
        self.padding = [0, 0, 0, 0]
        self.pages = []
        self.setSceneRect(QRect(0, 0, 6000, 6000))
        self.pos_under_cursor = None
        self.addItem(ImageItem())

    def drawBackground(self, painter, rect):
        painter.setPen(Qt.NoPen)
        painter.fillRect(rect, QBrush(QColor(30,30,30)))
        left = int(rect.left()) - (int(rect.left()) % self.gridSize[0])
        top = int(rect.top()) - (int(rect.top()) % self.gridSize[1])
        lines = []
        right = int(rect.right())
        bottom = int(rect.bottom())
        for x in range(left, right, self.gridSize[0]):
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, bottom, self.gridSize[1]):
            lines.append(QLineF(rect.left(), y, rect.right(), y))

        painter.setPen(QPen(QBrush(QColor(50,50,50)), 1, Qt.SolidLine))
        painter.drawLines(lines)

        if self.pos_under_cursor:
            if not self.itemAt(self.pos_under_cursor, QTransform()):
                x = (self.gridSize[0]*int(self.pos_under_cursor.x() // self.gridSize[0]))
                y = (self.gridSize[1]*int(self.pos_under_cursor.y() // self.gridSize[1]))
                page_rect = QRect(x, y, *self.gridSize)
                page_rect = page_rect.adjusted(-self.padding[0], -self.padding[1], self.padding[2], self.padding[3])
                painter.setPen(QPen(QBrush(QColor(150, 150, 150, 150)), 3, Qt.SolidLine))
                painter.drawRect(page_rect)

        # painter.setPen(QPen(QBrush(QColor(150,150,150, 150)), 2, Qt.SolidLine))
        # painter.drawLine(0, -30, 0, 30)
        # painter.drawLine(-30, 0, 30, 0)
        # painter.drawRect(self.sceneRect())

    def draw_pages(self, **kwargs):
        while self.pages:
            self.removeItem(self.pages.pop())
        grid_size = kwargs.get('paper_size')
        self.gridSize = Tiler.orient_page(grid_size, kwargs['orientation'])
        self.padding = kwargs['padding']
        self.update()

    def mouseMoveEvent(self, event):
        self.pos_under_cursor = event.scenePos()
        self.update()
        return super().mouseMoveEvent(event)

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
