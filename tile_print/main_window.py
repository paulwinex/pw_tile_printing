from functools import partial

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from pathlib import Path
from .widgets.canvas_view import CanvasView
from tiler import ORIENT_PORTRAIT, ORIENT_LANDSCAPE, Tiler

resource_path = Path(__file__).parent / "resources"
window_icon_path = resource_path/"tiler.png"


class TilerMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tiler")
        self.setWindowIcon(QIcon(window_icon_path.as_posix()))
        self.resize(1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        # add toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.addAction(QIcon((resource_path/"tiler.png").as_posix()), "Tiler", self.about)

        btn_ly = QHBoxLayout()
        btn_ly.addWidget(QPushButton('Reset',  clicked=self.reset_image))
        btn_ly.addWidget(QPushButton('Save',  clicked=self.save_images))
        btn_ly.addWidget(QPushButton('Print', clicked=self.print_images))
        self.layout.addLayout(btn_ly)

        # self.info_lb = QLabel('Open New Image')
        # self.layout.addWidget(self.info_lb)

        self.canvas_view = CanvasView()
        self.layout.addWidget(self.canvas_view)

        self.paper_cbb = PaperCombo()
        self.paper_cbb.currentIndexChanged.connect(self.refresh_canvas)
        self.toolbar.addWidget(self.paper_cbb)

        rb_widget = QWidget()
        rb_layout = QHBoxLayout()
        rb_widget.setLayout(rb_layout)
        self.toolbar.addWidget(rb_widget)
        self.orient_p = QRadioButton("Portrait")
        self.orient_p.setChecked(True)
        rb_layout.addWidget(self.orient_p)
        self.orient_l = QRadioButton("Landscape")
        rb_layout.addWidget(self.orient_l)
        self.orient_p.toggled.connect(self.refresh_canvas)

        self.dpi_sb = QSpinBox()
        self.dpi_sb.setSuffix(" dpi")
        self.dpi_sb.setRange(1, 600)
        self.dpi_sb.setValue(300)
        self.dpi_sb.setMinimumWidth(50)
        self.dpi_sb.editingFinished.connect(self.refresh_canvas)
        self.toolbar.addWidget(self.dpi_sb)

        self.padding_wd = PaddingWidget()
        self.padding_wd.valueChanged.connect(self.refresh_canvas)
        self.toolbar.addWidget(self.padding_wd)

        self.image_path_le = QLineEdit()
        self.toolbar.addWidget(self.image_path_le)

        self.browse_image_btn = QToolButton(clicked=self.browse_image)
        self.browse_image_btn.setText("...")
        self.toolbar.addWidget(self.browse_image_btn)

        # self.toolbar.addWidget(QPushButton('-', clicked=partial(self.canvas_view.s.scale_image, 0.9)))

        # self.toolbar.addAction(QAction('Update', self, triggered=self.refresh_canvas), )
        self.refresh_canvas()
        self.show()

    def closeEvent(self, event):
        self.status_bar.showMessage("Closing")
        event.accept()

    def about(self):
        QMessageBox.about(self, "About Tiler", "Tiler v0.1")

    def refresh_canvas(self):
        padding = self.padding_wd.get_padding()
        keep_aspect = True
        path = self.image_path_le.text()
        paper_size = self.paper_cbb.get_paper_size()
        paper_size = (paper_size[0] - padding[0] - padding[2], paper_size[1] - padding[1] - padding[3])
        orientation = ORIENT_PORTRAIT if self.orient_p.isChecked() else ORIENT_LANDSCAPE
        dpi = self.dpi_sb.value()
        self.canvas_view.s.draw_pages(
            padding=padding,
            keep_aspect=keep_aspect,
            path=path,
            paper_size=paper_size,
            orientation=orientation,
            dpi=dpi,
        )

    def browse_image(self):
        path = QFileDialog.getOpenFileName(self, "Open Image", filter='*.png')
        if path:
            self.set_image(path[0])
            self.refresh_canvas()

    def canvas_changed(self, kwargs):
        print(kwargs)

    def set_image(self, path):
        self.image_path_le.setText(path)
        self.canvas_view.s.set_image(path)

    def get_current_image(self):
        return self.image_path_le.text()

    def reset_image(self):
        self.set_image(self.get_current_image().strip())
        self.refresh_canvas()

    def save_images(self):
        opt = self.collect_options()
        save_path = QFileDialog.getExistingDirectory(self, "Save Images")
        if save_path:
            t = Tiler(Path(self.get_current_image()), dpi=opt['dpi'])
            tiles = t.make_tiles(**opt, keep_aspect_ratio=True, save_path=Path(save_path))
            print('TILES:')
            print(tiles)

    def print_images(self):
        opt = self.collect_options()
        print(opt)

    def collect_options(self):
        padding = self.padding_wd.get_padding()
        image_info = self.canvas_view.s.image_item.get_image_info()
        return dict(**image_info,
                    padding=padding,
                    page_orient=ORIENT_PORTRAIT if self.orient_p.isChecked() else ORIENT_LANDSCAPE,
                    dpi=self.dpi_sb.value(),
                    page_size=self.get_current_page_size(),
                    )

    def get_current_page_size(self):
        return self.paper_cbb.get_paper_size()


class PaperCombo(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_items()

    def init_items(self):
        from .import tiler
        for i, (name, value) in enumerate(tiler.__dict__.items()):
            if name.startswith("PAPER_") and not name.endswith("_"):
                self.addItem(name.split("_")[1].title(), userData=value)
        self.setCurrentIndex(1)

    def get_paper_size(self):
        return self.currentData()


class PaddingWidget(QWidget):
    valueChanged = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.widgets = {}
        self.layout.addWidget(QLabel("Padding:"))
        for pos in ['left', 'top', 'right', 'bottom']:
            self.layout.addWidget(QLabel(pos.title()))
            s = QSpinBox()
            s.setRange(0, 100)
            s.setValue(0)
            s.setMinimumWidth(50)
            self.layout.addWidget(s)
            self.widgets[pos] = s
            s.editingFinished.connect(self.valueChanged.emit)

    def get_padding(self):
        return (
            self.widgets['left'].value(),
            self.widgets['top'].value(),
            self.widgets['right'].value(),
            self.widgets['bottom'].value()
        )
