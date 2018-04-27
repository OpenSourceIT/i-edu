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
from iedu.network import ieduServer, ieduSocket

import sys
import signal

class ieduMain:

    def __init__(self):
        self.app = QApplication(sys.argv)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        print("Starting i-EDU Server")

        self.server = ieduServer()
        self.server.listen(QHostAddress.Any, 12345)
        self.server.newConnection.connect(self.newClient)

        self.pktNew = True
        self.pktSize = 0
        self.pktBuf = QByteArray()

        self.app.exec_()

    def newClient(self):
        print("newClient()")
        self.client = self.server.nextPendingConnection() # type: ieduSocket
        self.client.readyReadPkt.connect(self.processPkt)

    def processPkt(self, pkt, client):
        print("pktsize", pkt.size())
        print("pktclient", client.peerAddress().toString())

        out = QDataStream(pkt, QIODevice.ReadWrite)
        out.setVersion(QDataStream.Qt_5_2)

        json = QJsonDocument().fromBinaryData(out.readBytes())

        b64data = json.object()["screen"].toString()
        screen = QByteArray().fromBase64(QByteArray().append(b64data))

        save2 = QPixmap()
        save2.loadFromData(screen, "PNG")
        save2.save("/tmp/zzz2.png", "PNG")

        block = QByteArray()
        block.append("hallo client")
        self.client.write(block)
        self.client.flush()

if __name__ == '__main__':
    ieduMain()