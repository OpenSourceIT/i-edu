#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
try:
    from iedu.network import ieduSocket
except:
    import os
    import sys
    WORK_DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(WORK_DIR + "/../usr/lib/python3/dist-packages")
    from iedu.network import ieduSocket

import sys
import signal
import time
from struct import *

class ieduMain:

    def __init__(self):
        self.app = QApplication(sys.argv)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.serverConnect()
        while not self.sock.waitForConnected(1000):
            print("Error connecting, try again:", self.sock.errorString())
            time.sleep(5)
            self.serverConnect()

        self.sock.waitForEncrypted(1000)
        self.sock.readyRead.connect(self.onSockReadyRead)

        # Screenshot
        screen = QGuiApplication.primaryScreen()
        screenshot = screen.grabWindow(0) # type: QPixmap
        screenb = QByteArray()
        screenbst = QBuffer(screenb)
        screenbst.open(QIODevice.WriteOnly)
        screenshot.save(screenbst, "PNG")
        screenshot.save("/tmp/zorig.png", "PNG")

        # Greeting
        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)
        out.setVersion(QDataStream.Qt_5_2)
        #out.writeQString("Hallo server")
        json = QJsonDocument()
        jsTop = {}
        jsTop["action"] = "screenshot2"
        jsTop["data"] = "123456"
        jsTop["screen"] = str(screenb.toBase64().data(), encoding='utf-8')

        json.setObject(jsTop)

        out.writeBytes(json.toBinaryData())

        self.sock.writePkt(block)

        self.app.exec_()

    def serverConnect(self):
        self.sock = ieduSocket()
        self.sock.ignoreSslErrors()
        # sock.sslErrors.connect(sock.ignoreSslErrors)
        self.sock.setPeerVerifyMode(QSslSocket.VerifyNone)
        self.sock.ignoreSslErrors()
        self.sock.connectToHostEncrypted("localhost", 12345)

    def onSslErrors(self, sslErrors):
        print("SSL-Error12:")
        for error in sslErrors:
            print(error.errorString())

    def onSockReadyRead(self):
        print(self.sock.readAll())

if __name__ == '__main__':
    ieduMain()