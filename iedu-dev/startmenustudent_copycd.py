#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import subprocess

from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ieduCopyCD(QObject):

    base_path_media = ""
    proc = QProcess()

    notreadywarningshowed = False
    insertcdcount = 0
    diskstatuscount = 0

    def __init__(self, parent, path_media):
        super(ieduCopyCD, self).__init__()

        self.ui = QMainWindow(parent, Qt.Dialog)
        self.widget = uic.loadUi(path_media + "menu-copycd.ui")  # type: QDialog
        self.ui.setCentralWidget(self.widget)
        self.ui.setWindowModality(Qt.WindowModal)
        self.ui.setMinimumSize(self.widget.width(), self.widget.height())
        self.ui.setWindowTitle(parent.windowTitle() + " - CD kopieren")

        self.btnStart = self.widget.btnStart # type: QPushButton
        self.btnStart.clicked.connect(self.copyCD)
        self.btnCancel = self.widget.btnCancel # type: QPushButton
        self.btnCancel.clicked.connect(self.cancelProc)
        self.btnExit = self.widget.btnExit # type: QPushButton
        self.btnExit.clicked.connect(self.exitCopyCD)
        self.btnEnter = self.widget.btnEnter # type: QPushButton
        self.btnEnter.clicked.connect(self.sendEnter)
        self.teLog = self.widget.teLog # type: QTextEdit

        self.base_path_media = path_media

        self.ui.installEventFilter(self)

        self.cleanup()

        self.ui.show()

    def cancelProc(self):
        self.proc.kill()
        self.btnStart.setEnabled(True)
        self.btnCancel.setDisabled(True)

    def exitCopyCD(self):
        self.cancelProc()
        self.ui.close()

    def sendEnter(self):
        self.proc.write(QByteArray().append("\n"))
        self.proc.waitForBytesWritten()

    def copyCD(self):
        subprocess.call("umount /dev/sr0", shell=True)

        self.proc = QProcess()
        self.proc.readyReadStandardOutput.connect(self.procRead)
        self.proc.finished.connect(self.procFinished)
        self.proc.started.connect(self.procStarted)
        # QT >= 5.6 only
        # self.proc.errorOccurred.connect(self.procUDPCastErrorOccurred)
        self.proc.readyReadStandardError.connect(self.procError)
        self.proc.start("bash -c \"cd /tmp; cdrdao copy --device /dev/sr0 --source-device /dev/sr0 --eject\"")

    def procRead(self):
        out = self.proc.readAllStandardOutput()
        self.teLog.append(out)

    def procFinished(self):
        self.btnStart.setEnabled(True)
        self.btnCancel.setDisabled(True)
        self.btnExit.setEnabled(True)
        self.cleanup()

    def procStarted(self):
        self.teLog.clear()
        self.notreadywarningshowed = False
        self.insertcdcount = 0
        self.btnStart.setDisabled(True)
        self.btnCancel.setEnabled(True)
        self.btnExit.setDisabled(True)
        self.cleanup()

    def procError(self):
        out = str(self.proc.readAllStandardError(), encoding='utf-8')
        self.teLog.append(out)

        if out.find("WARNING: Unit not ready") != -1 and self.notreadywarningshowed == False:
            self.notreadywarningshowed = True
            QMessageBox.information(self.ui, "CD einlegen", "Bitte legen Sie eine CD ein um fortzufahren.")

        if out.find("CD copying finished successfully") != -1:
            QMessageBox.information(self.ui, "CD fertiggestellt", "Die CD wurde erfolgreich kopiert.")

        if out.find("Please insert a recordable medium") != -1 and self.insertcdcount < 3:
            QMessageBox.information(self.ui, "CD-R/CD-RW einlegen", "Bitte legen Sie eine leere CD-R/CD-RW ein um fortzufahren.")
            self.proc.write(QByteArray().append("\n"))
            self.proc.waitForBytesWritten()
            self.insertcdcount += 1

        if out.find("Cannot determine disk status") != -1 and self.diskstatuscount < 5:
            QMessageBox.information(self.ui, "CD-R/CD-RW Status", "CD-R/CD-RW Status unbekannt, erneut versuchen.")
            self.proc.write(QByteArray().append("\n"))
            self.proc.waitForBytesWritten()
            self.diskstatuscount += 1

        if self.insertcdcount >= 3:
            QMessageBox.information(self.ui, "CD-R/CD-RW Status", "Programm wird abgebrochen, keine leere CD-R/CD-RW gefunden")
            self.cancelProc()

        if self.diskstatuscount >= 5:
            QMessageBox.information(self.ui, "CD-R/CD-RW Status", "Programm wird abgebrochen, CD-Status konnte nicht ermittelt werden")
            self.cancelProc()

    def cleanup(self):
        subprocess.call("rm /tmp/*.bin", shell=True)

    def eventFilter(self, object, event):
        if object == self.ui and event.type() == QEvent.Close:
            self.exitCopyCD()
            return True

        return False
