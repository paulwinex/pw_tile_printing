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

    def drawBackground(self, painter: QPainter, rect: QRect):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, QBrush(QColor(30, 30, 30)))
        left = int(rect.left()) - (int(rect.left()) % self.gridSize[0])
        top = int(rect.top()) - (int(rect.top()) % self.gridSize[1])
        if self.image_item:
            image_rect = self.image_item.boundingRect()
            paper_rects = self.get_paper_rects(image_rect, self.gridSize)
            painter.save()
            painter.setBrush(QBrush(QColor('#444444')))
            for paper_rect in paper_rects:
                painter.drawRect(paper_rect)
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
