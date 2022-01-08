# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QToolButton, QComboBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from interface import wifiInterface
from pcaper import pcaper
import logging

class MainWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.wifiInterface = None
        self.btn_connect = None
        self.lineEdit_passwd = None
        self.lineEdit_IP = None
        self.cb_band = None
        self.cb_iface = None
        self.btn_stop = None
        self.btn_start = None
        self.btn_scan = None
        self.table = None
        self.ui = None
        self.load_ui()
        self.initGuiComponents()
        self.updateGuiComponents()

    def btn_scan_onclick(self):
        print("btn_scan_onclick")
        for row in range(self.table.rowCount()):
            self.table.removeRow(0)
        self.btn_scan.setEnabled(False)
        ap_list = self.wifiInterface.do_scan(self.cb_band.currentText(), self.cb_iface.currentText())
        for ap in ap_list:
            self.table.insertRow(self.table.rowCount())
            column = 0
            for attr in ap.split("\t"):
                item = QTableWidgetItem(attr)
                self.table.setItem(self.table.rowCount()-1, column, item)
                column += 1
        self.table.resizeColumnsToContents()
        self.btn_start.setEnabled(False)
        self.btn_scan.setEnabled(True)

    def btn_start_onclick(self):
        ap_list = self.table.selectedItems()
        if len(ap_list) == 0:
            # toast error
            return
        ap_channel = ap_list[5].text()
        ap_bandwidth = ap_list[6].text()
        ap_center_freq = ap_list[7].text()
        print(ap_channel, ap_bandwidth, ap_center_freq)
        l_pcaper = pcaper("wlan0", ap_channel, ap_bandwidth, ap_center_freq)
        l_pcaper.start("sniffer.pcapng")
        self.btn_scan.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def btn_stop_onclick(self):
        self.btn_scan.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def btn_connect_onclick(self):
        self.btn_connect.setEnabled(False)
        print("btn_connect onclick")
        self.wifiInterface = wifiInterface(self.lineEdit_IP.text(), self.lineEdit_passwd.text())
        if self.wifiInterface.ssh_connected is True:
            self.btn_scan.setEnabled(True)
            self.updateGuiComponents()
        self.btn_connect.setEnabled(True)

    def table_on_select_changed(self):
        self.btn_start.setEnabled(True)

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

    def initGuiComponents(self):
        # Find components
        self.table = self.ui.findChild(QTableWidget, "tableWidget")
        self.btn_scan = self.ui.findChild(QToolButton, "btn_scan")
        self.btn_start = self.ui.findChild(QToolButton, "btn_start")
        self.btn_stop = self.ui.findChild(QToolButton, "btn_stop")
        self.btn_connect = self.ui.findChild(QToolButton, "btn_connect")
        self.cb_iface = self.ui.findChild(QComboBox, "cb_iface")
        self.cb_band = self.ui.findChild(QComboBox, "cb_band")
        self.lineEdit_IP = QLineEdit(self.ui.findChild(QLineEdit, 'lineEdit_IP'))
        self.lineEdit_passwd = QLineEdit(self.ui.findChild(QLineEdit, 'lineEdit_passwd'))
        # Hook Signals
        self.btn_scan.clicked.connect(self.btn_scan_onclick)
        self.btn_start.clicked.connect(self.btn_start_onclick)
        self.btn_stop.clicked.connect(self.btn_stop_onclick)
        self.btn_connect.clicked.connect(self.btn_connect_onclick)
        self.table.itemSelectionChanged.connect(self.table_on_select_changed)
        # Set initial state
        self.btn_scan.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.lineEdit_IP.setText("127.0.0.1")
        self.lineEdit_passwd.setText("password")
        self.setLayout(self.ui.findChild(QVBoxLayout, "verticalLayout"))

    def updateGuiComponents(self):
        if self.wifiInterface and self.wifiInterface.ssh_connected is True:
            for ifaceName in self.wifiInterface.getIfaceNames():
                self.cb_iface.addItem(ifaceName)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        widget = MainWidget()
        self.setCentralWidget(widget)

if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
