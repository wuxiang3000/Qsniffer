# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from PySide6.QtWidgets import QWidget, QLabel, QToolButton
from PySide6.QtWidgets import QLineEdit, QComboBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from scanner import wifiscanner
from pcaper import pcaper

class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.load_ui()
        self.btn_scan = self.ui.findChild(QToolButton, "btn_scan")
        self.btn_start = self.ui.findChild(QToolButton, "btn_start")
        self.btn_stop = self.ui.findChild(QToolButton, "btn_stop")
        self.btn_browser = self.ui.findChild(QToolButton, "btn_browser")
        self.table = self.ui.findChild(QTableWidget, "list_ap")
        self.le_save_path = self.ui.findChild(QLineEdit, "le_save_path")
        self.cb_band = self.ui.findChild(QComboBox, "cb_band")

        self.label = QLabel(self.ui.findChild(QLabel, "label"))

        self.btn_scan.clicked.connect(self.btn_scan_onclick)
        self.btn_start.clicked.connect(self.btn_start_onclick)
        self.btn_stop.clicked.connect(self.btn_stop_onclick)
        self.btn_browser.clicked.connect(self.btn_browser_onclick)
        self.table.itemSelectionChanged.connect(self.table_on_select_changed)

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)

    def btn_scan_onclick(self):
        for row in range(self.table.rowCount()):
            self.table.removeRow(0)
        self.label.setFixedWidth(128)
        self.label.setText("scan")
        mScanner = wifiscanner()
        self.btn_scan.setEnabled(False)
        ap_list = mScanner.do_scan(self.cb_band.currentText())
        for ap in ap_list:
            self.table.insertRow(self.table.rowCount())
            column = 0
            for attr in ap.split("\t"):
                item = QTableWidgetItem(attr)
                self.table.setItem(self.table.rowCount()-1, column, item)
                column += 1
        self.btn_scan.setEnabled(True)
        self.btn_start.setEnabled(False)

    def btn_start_onclick(self):
        self.label.setText("start")
        mAp = self.table.selectedItems()
        if len(mAp) == 0:
            # toast error
            return
        mFreq = mAp[6].text()
        mBandWidth = mAp[4].text()
        mPcaper = pcaper(mFreq, mBandWidth)
        mPcaper.start("sniffer.pcapng")
        self.btn_scan.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def btn_stop_onclick(self):
        self.label.setText("stop")
        print(self.label.text())
        self.btn_scan.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def btn_browser_onclick(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setNameFilter("*.png *.xpm *.jpg")
        dialog.setViewMode(QFileDialog.Detail)
        if dialog.exec():
            fileName = dialog.selectedFiles()
            print(fileName[0])
            self.le_save_path.setText(fileName[0])
        pass

    def table_on_select_changed(self):
        self.btn_start.setEnabled(True)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent.parent / "ui/main_window.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()



if __name__ == "__main__":
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
