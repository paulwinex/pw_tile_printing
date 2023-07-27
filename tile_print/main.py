from PySide6.QtWidgets import QApplication
from tile_print.main_window import TilerMainWindow


def show():
    app = QApplication()
    dialog = TilerMainWindow()
    dialog.show()
    app.exec()
