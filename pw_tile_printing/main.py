from PySide6.QtWidgets import QApplication
from pw_tile_printing.main_window import TilerMainWindow


def show():
    app = QApplication()
    dialog = TilerMainWindow()
    dialog.show()
    app.exec()
