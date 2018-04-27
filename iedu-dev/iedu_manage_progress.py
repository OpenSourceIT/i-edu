#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import logging
import urllib3
import requests

from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from iedu.config import *

logging.getLogger("paramiko").setLevel(logging.INFO)
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ieduConfig = ieduConfig()

class ieduManageProgress(QObject):
    abort = pyqtSignal()

    STATUS = {
        "OK": "ok",
        "WARNING": "warning",
        "ERROR": "error",
        "INFO": "info"
    }

    progress_max = 0
    client_log = {}

    def __init__(self, parent):
        super(ieduManageProgress, self).__init__()

        self.ui = QMainWindow(parent, Qt.Dialog)
        self.widget = uic.loadUi(ieduConfig.create_media_path("iedu_manage_progress.ui"))  # type: QDialog
        self.ui.setCentralWidget(self.widget)
        self.ui.setWindowModality(Qt.WindowModal)
        self.ui.setMinimumSize(self.widget.width(), self.widget.height())
        self.ui.setWindowTitle(parent.windowTitle() + " - Fortschritt")

        self.tvClientStatus = self.widget.tvClientStatus # type: QTreeView
        self.tvClientStatus.setModel(QStandardItemModel(self.ui))
        self.tvClientStatus.doubleClicked.connect(self.on_tvClientStatus_doubleClicked)
        mClientStatus = self.tvClientStatus.model() # type: QStandardItemModel
        mClientStatus.setHorizontalHeaderLabels(["Status", "Client", "Info"])
        self.tvClientStatus.header().resizeSection(0, 50)
        self.tvClientStatus.header().resizeSection(1, 150)
        self.teLog = self.widget.teLog #type: QTextEdit
        self.btnAbort = self.widget.btnAbort #type: QPushButton
        self.btnAbort.clicked.connect(self.on_btnAbort_clicked)
        self.btnClose = self.widget.btnClose  # type: QPushButton
        self.btnClose.clicked.connect(self.on_btnClose_clicked)
        self.progressBar = self.widget.progressBar  # type: QProgressBar
        self.progressBar.hide()

        self.client_log = {}

        self.ui.show()

    def on_btnAbort_clicked(self):
        self.abort.emit()

    def on_btnClose_clicked(self):
        self.ui.close()

    def showProgressBar(self):
        self.progressBar.show()

    def setProgressMax(self, max):
        self.progress_max = max

    def setProgressUpdate(self, value):
        self.progressBar.setValue(100 / self.progress_max * value)

    def resetProgressbar(self):
        self.progress_max = 0
        self.progressBar.setValue(0)

    def setProgressFinish(self):
        self.progressBar.setValue(100)

    def started(self):
        print("progress_started")
        self.btnAbort.setEnabled(True)
        self.btnClose.setDisabled(True)

    def updateClientStatus(self, client, status, text):
        mClientStatus = self.tvClientStatus.model() # type: QStandardItemModel
        itemRow = mClientStatus.rowCount()

        ic = 0
        while ic < mClientStatus.rowCount():
            item = mClientStatus.item(ic, 1)  # type: QStandardItem
            if item.data() == client:
                itemRow = item.row()
                break

            ic += 1

        item1 = QStandardItem()
        if status == self.STATUS["OK"]:
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/status/ok.png")))
        elif status == self.STATUS["WARNING"]:
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/status/warning.png")))
        elif status == self.STATUS["ERROR"]:
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/status/error.png")))
        else:
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/status/info.png")))

        mClientStatus.setItem(itemRow, 0, item1)

        item2 = QStandardItem()
        item2.setText(client)
        item2.setData(client)
        mClientStatus.setItem(itemRow, 1, item2)

        item3 = QStandardItem()
        item3.setText(text)
        mClientStatus.setItem(itemRow, 2, item3)

    def appendLog(self, text):
        self.teLog.append(text)

    def appendClientLog(self, client, text):
        if client in self.client_log:
            self.client_log[client] += text
        else:
            self.client_log[client] = text

    def finished(self):
        print("progress_finished")
        self.btnAbort.setDisabled(True)
        self.btnClose.setEnabled(True)
        if(self.progressBar.isVisible()):
            self.setProgressFinish()

    def on_tvClientStatus_doubleClicked(self, index):
        mClientStatus = self.tvClientStatus.model()
        item = mClientStatus.item(index.row(), 1)
        client = item.data()
        if client in self.client_log:
            QMessageBox.information(self.ui, "Log für Client %s" % client, self.client_log[client])