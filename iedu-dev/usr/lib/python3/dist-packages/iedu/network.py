#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import logging
import re
import socket
import struct
import paramiko

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

from struct import *
from paramiko import *

from iedu.common import ieduCommonHelper

mutex = QMutex()

logging.getLogger("paramiko").setLevel(logging.INFO)

class ieduNetworkHelper():
    @staticmethod
    def get_net_interfaces():
        nets = ieduCommonHelper.run_cmd_stdout("ip addr", argShell=True)
        foundeth = False
        cureth = ""
        eths = {}
        for line in nets[1].split("\n"):
            l = line.strip()
            m = re.search("^[0-9]: (.*): .*", l)
            if m != None:
                foundeth = True
                cureth = m.group(1)
                eths[cureth] = {}
                eths[cureth]["ip"] = ""

            if foundeth == True:
                m2 = re.search("^inet ([^ ]*)/([0-9]{1,2}) .*", l)
                if m2 != None:
                    eths[cureth]["ip"] = m2.group(1)
                    eths[cureth]["cidr"] = m2.group(2)
                    eths[cureth]["fqip"] = m2.group(1) + "/" + m2.group(2)
                    foundeth = False
                    cureth = ""

        return eths

    @staticmethod
    def send_wol_packet(macaddress):
        # Check macaddress format and try to compensate.
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 12 + 5:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            return

        # Pad the synchronization stream.
        data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
        send_data = b''

        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
            send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

        # Broadcast it to the LAN.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ("255.255.255.255", 9))

    @staticmethod
    def send_ssh_cmd(host, cmd, user="root"):
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, port=22)

        stdin, stdout, stderr = client.exec_command(cmd)
        client.close()

        return stdout, stderr

class ieduServer(QTcpServer):

    def incomingConnection(self, socketDescriptor):
        self.serverSocket = ieduSocket()
        self.serverSocket.setLocalCertificate("ssl/cert.pem")
        self.serverSocket.setPrivateKey("ssl/key.pem")
        self.serverSocket.setPeerVerifyMode(QSslSocket.VerifyNone)
        if(self.serverSocket.setSocketDescriptor(socketDescriptor)):
            self.serverSocket.startServerEncryption()
            self.addPendingConnection(self.serverSocket)

    def onSslErrors(self, sslErrors):
        print(sslErrors)

class ieduSocket(QSslSocket):
    readyReadClient = pyqtSignal('PyQt_PyObject')
    readyReadPkt = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    pktNew = True
    pktSize = 0
    pktBuf = QByteArray()

    PKT_HEADER = "==iedudata=="

    def __init__(self):
        super(ieduSocket, self).__init__()
        self.readyRead.connect(self.readyReadExt)

    def readyReadExt(self):
        self.readyReadClient.emit(self)

        print("client read2: ", self.peerAddress().toString())
        bytesavail = self.bytesAvailable()
        while bytesavail < 16:
            return

        print("bytes waiting:", self.bytesAvailable())

        if self.pktNew == True:
            block = QByteArray().append(self.read(12))
            print("block: ", block)
            if self.PKT_HEADER == str(block.data(), encoding='utf-8'):
                print("beginning received")
                self.pktSize = unpack('i', self.read(4))[0]
                print("we need data:", self.pktSize)

                bytesavail -= 16
                if bytesavail > 0:
                    if bytesavail > self.pktSize:
                        self.pktBuf.append(self.read(self.pktSize))
                        self.pktSize = 0
                        self.readyReadPkt.emit(self.pktBuf, self)
                        self.pktBuf.clear()
                    else:
                        self.pktBuf.append(self.read(bytesavail))
                        self.pktSize -= bytesavail
                        self.pktNew = False
                        if self.pktSize == 0:
                            self.readyReadPkt.emit(self.pktBuf, self)
                            self.pktBuf.clear()
                            self.pktNew = True

        else:

            if self.pktSize > 0:
                print("we need further data:", self.pktSize)

                if bytesavail > self.pktSize:
                    self.pktBuf.append(self.read(self.pktSize))
                    self.pktSize = 0
                    self.readyReadPkt.emit(self.pktBuf, self)
                    self.pktBuf.clear()
                    self.pktNew = True
                else:
                    self.pktBuf.append(self.read(bytesavail))
                    self.pktSize -= bytesavail
                    if self.pktSize == 0:
                        self.readyReadPkt.emit(self.pktBuf, self)
                        self.pktBuf.clear()
                        self.pktNew = True

    def writeSafe(self, data):
        mutex.lock()

        self.write(data)
        self.flush()
        self.waitForBytesWritten()

        mutex.unlock()

    def writePkt(self, data):
        mutex.lock()

        self.write(QByteArray().append(self.PKT_HEADER))
        self.write(pack('i', data.size()))
        self.write(data)
        self.flush()
        self.waitForBytesWritten()

        mutex.unlock()