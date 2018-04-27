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
import paramiko

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from paramiko import *
from time import sleep

from iedu.config import *
from iedu_manage_progress import ieduManageProgress

logging.getLogger("paramiko").setLevel(logging.INFO)
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ieduConfig = ieduConfig()

class cmdData():
    cmd = ""
    user = ""
    x11 = False

class ieduManageCMD():

    parent_win = 0
    clients = {}

    def __init__(self, parent, clients):
        self.ui = QMainWindow(parent, Qt.Dialog)
        self.widget = uic.loadUi(ieduConfig.create_media_path("iedu_manage_cmd.ui"))  # type: QDialog
        self.ui.setCentralWidget(self.widget)
        self.ui.setWindowModality(Qt.WindowModal)
        self.ui.setMinimumSize(self.widget.width(), self.widget.height())
        self.ui.setWindowTitle(parent.windowTitle() + " - Befehl ausführen")

        self.teCMD = self.widget.teCMD  # type: QTextEdit
        self.rbUserRoot = self.widget.rbUserRoot  # type: QRadioButton
        self.rbUserStudent = self.widget.rbUserStudent  # type: QRadioButton
        self.cbUseX11 = self.widget.cbUseX11  # type: QCheckBox

        self.btnCancel = self.widget.btnCancel  # type: QPushButton
        self.btnCancel.clicked.connect(self.on_btnCancel_clicked)
        self.btnCMD = self.widget.btnCMD  # type: QPushButton
        self.btnCMD.clicked.connect(self.on_btnCMD_clicked)

        self.parent_win = parent
        self.clients = clients

        self.ui.show()

    def on_btnCancel_clicked(self):
        self.ui.hide()

    def on_btnCMD_clicked(self):
        # Collect data
        data = cmdData()
        data.cmd = self.teCMD.toPlainText()
        data.user = "root" if self.rbUserRoot.isChecked() else "student"
        data.x11 = self.cbUseX11.isChecked()

        self.win_status = ieduManageProgress(self.ui)

        # Start worker thread
        self.cmd_thread = QThread()
        self.cmd_thread.setTerminationEnabled(True)
        self.cmd_worker = ieduManageCMDWorker()
        self.win_status.abort.connect(self.cmd_worker.abort)
        self.cmd_worker.setData(self.cmd_thread, self.clients, data)
        self.cmd_worker.moveToThread(self.cmd_thread)
        self.cmd_thread.started.connect(self.cmd_worker.process)
        self.cmd_worker.started.connect(self.win_status.started)
        self.cmd_worker.finished.connect(self.cmd_thread.quit)
        self.cmd_worker.finished.connect(self.win_status.finished)
        self.cmd_worker.hostupdate.connect(self.win_status.updateClientStatus)
        self.cmd_worker.logupdate.connect(self.win_status.appendLog)
        self.cmd_worker.logclientupdate.connect(self.win_status.appendClientLog)
        self.cmd_thread.start()

        pass

class ieduManageCMDWorker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    hostupdate = pyqtSignal(str, str, str)
    logupdate = pyqtSignal(str)
    logclientupdate = pyqtSignal(str, str)

    iedu_clients = {}
    iedu_cmd_data = ""

    cur_nic = ""
    proc = QProcess()
    thread = QThread()

    def setData(self, thread, clients, data):
        self.thread = thread
        self.iedu_clients = clients
        self.iedu_cmd_data = data

    def process(self):

        self.logupdate.emit("Starte CMD-Ausführung")
        self.started.emit()

        # Generate udpcastlist
        for cclient in self.iedu_clients:
            self.hostupdate.emit(cclient, ieduManageProgress.STATUS["INFO"], "Starte CMD")

            try:
                client = SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(cclient, username="root", port=22)
                csftp = client.open_sftp()

                cmd = ""

                if(self.iedu_cmd_data.x11 == True):
                    cmd += "export $(/usr/share/epoptes-client/get-display)\n"

                if(self.iedu_cmd_data.user == "root"):
                    cmd += self.iedu_cmd_data.cmd + "\n"
                else:
                    for line in self.iedu_cmd_data.cmd.split("\n"):
                        cmd += "su %s -c '%s'\n" % (self.iedu_cmd_data.user, line)

                fp = csftp.file("/root/tmp_iedumanage", "w")
                fp.write(cmd)
                fp.close()

                stdin, stdout, stderr = client.exec_command('bash /root/tmp_iedumanage')
                self.logclientupdate.emit(cclient, stdout.read().decode("utf-8"))
                self.logclientupdate.emit(cclient, stderr.read().decode("utf-8"))

                csftp.remove("/root/tmp_iedumanage")

                client.close()
                self.hostupdate.emit(cclient, ieduManageProgress.STATUS["OK"], "CMD erfolgreich.")
            except Exception as inst:
                self.hostupdate.emit(cclient, ieduManageProgress.STATUS["ERROR"], "CMD nicht erfolgreich (%s)" % inst)

        self.logupdate.emit("CMD abgeschlossen")

        self.logupdate.emit("Beende CMD-Thread")
        self.finished.emit()

    def abort(self):
        print("abort process")
        self.logupdate.emit("Prozess wird abgebrochen")
        self.proc.terminate()
        sleep(2)
        self.proc.kill()

        self.thread.quit()
        self.thread.terminate()