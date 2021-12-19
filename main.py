# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget, QLabel, QToolButton
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.load_ui()
        self.btn_scan = self.ui.findChild(QToolButton, "btn_scan")
        self.btn_start = self.ui.findChild(QToolButton, "btn_start")
        self.btn_stop = self.ui.findChild(QToolButton, "btn_stop")

        self.label = QLabel(self.ui.findChild(QLabel, "label"))

        self.btn_scan.clicked.connect(self.btn_scan_onclick)
        self.btn_start.clicked.connect(self.btn_start_onclick)
        self.btn_stop.clicked.connect(self.btn_stop_onclick)

    def btn_scan_onclick(self):
        self.label.setFixedWidth(128)
        self.label.setText("scan")

        print(self.label.lineWidth())

    def btn_start_onclick(self):
        self.label.setText("start")
        print(self.label.text())

    def btn_stop_onclick(self):
        self.label.setText("stop")
        print(self.label.text())

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "ui/main_window.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()



if __name__ == "__main__":
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
