#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import sys
import configparser
import re

from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from subprocess import Popen, PIPE
from sys import argv
from os import listdir
from os.path import isdir, basename, exists, isfile

DEV_D = False
base_path_media = "/usr/share/vlizedlab/"
base_path_etc = "/etc/vlizedlab/"
if(len(argv) > 1 and argv[1] == "dev"):
    base_path_media = ""
    base_path_etc = "etc/"
    DEV_D = True

VL_LOG = "/etc/vlizedlab/installonfirstboot.log"

class MainMenu:

    def __init__(self):
        self.app = QApplication(sys.argv)

        self.ui = uic.loadUi(self.create_media_path("menu-firstboot.ui"))
        self.ui.setStyleSheet("""
        #Form {
        	background-image: url(%s);
        }
        """ % (self.create_media_path("world.gif")))

        self.ui.show()

        logWatcher = QFileSystemWatcher()
        logWatcher.addPath(VL_LOG)
        logWatcher.fileChanged.connect(self.onLogUpdate)

        self.app.exec_()

    def create_media_path(self, file):
        return base_path_media + file

    def onLogUpdate(self):
        fp = open(VL_LOG, "r")
        lines = fp.readlines()
        fp.close()
        self.ui.teLog.setPlainText(''.join(lines))
        scrollbar = self.ui.teLog.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

if __name__ == '__main__':
    MainMenu()