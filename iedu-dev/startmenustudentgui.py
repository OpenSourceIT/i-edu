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
import hashlib

from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from subprocess import Popen, PIPE
from sys import argv
from os import listdir
from os.path import isdir, basename, exists, isfile

from startmenustudent_copycd import ieduCopyCD

DEV_D = False
base_path_media = "/usr/share/vlizedlab/"
base_path_etc = "/etc/vlizedlab/"
if(len(argv) > 1 and argv[1] == "dev"):
    base_path_media = ""
    base_path_etc = "etc/"
    DEV_D = True

c_sound = 'yes'
c_sound_default_level = 55
c_sound_greeting = 'Willkommen Schüler'
c_autostart_vms = ''
c_beamer = 'no'
c_beamer_output = 'VGA-1'
c_screensaver = 'no'
c_umountusb = 'yes'
c_copycd = 'no'

c_program_teamviewer = 'yes'
c_program_terminal = 'yes'
c_program_browser = 'yes'
c_program_teamviewer_cmd = 'teamviewer'
c_program_terminal_cmd = 'xfce4-terminal'
c_program_browser_cmd = 'google-chrome-stable'
if exists(base_path_etc + "startmenustudentgui.ini"):
    config = configparser.ConfigParser()
    config.read(base_path_etc + "startmenustudentgui.ini")

    if "main" in config:
        if "sound" in config['main']:
            c_sound = config['main']['sound']

        if "sound_default_level" in config['main']:
            c_sound_default_level = config['main']['sound_default_level']

        if "greeting" in config['main']:
            c_sound_greeting = config['main']['greeting']

        if "autostart_vms" in config['main']:
            c_autostart_vms = config['main']['autostart_vms']

        if "beamer" in config['main']:
            c_beamer = config['main']['beamer']

        if "beamer_output" in config['main']:
            c_beamer_output = config['main']['beamer_output']

        if "screensaver" in config['main']:
            c_screensaver = config['main']['screensaver']

        if "umountusb" in config['main']:
            c_umountusb = config['main']['umountusb']

        if "copycd" in config['main']:
            c_copycd = config['main']['copycd']

    if "program" in config:
        if "teamviewer" in config['program']:
            c_program_teamviewer = config['program']['teamviewer']

        if "terminal" in config['program']:
            c_program_terminal = config['program']['terminal']

        if "browser" in config['program']:
            c_program_browser = config['program']['browser']

        if "teamviewer_cmd" in config['program']:
            c_program_teamviewer_cmd = config['program']['teamviewer_cmd']

        if "terminal_cmd" in config['program']:
            c_program_terminal_cmd = config['program']['terminal_cmd']

        if "browser_cmd" in config['program']:
            c_program_browser_cmd = config['program']['browser_cmd']

class MainMenu:
    ITEM_DATA_PASSWORD = Qt.UserRole + 2

    def __init__(self):
        self.app = QApplication(sys.argv)

        self.ui = uic.loadUi(self.create_media_path("menu.ui"))
        #border-image: url(%s) 0 0 0 0 stretch stretch;
        self.ui.setStyleSheet("""
        #Form {
        	background-image: url(%s);
        }
        QTreeView{
            border-radius: 15px;
            background: #FFFFFF;
            opacity: 100;
        }
        QPushButton:hover{
            background-color:#97C4C4;
        }
        QTreeView::item:hover{
            background-color:#97C4C4;
        }
        QTreeView::item:selected{
            background-color:#42bff4;
            color:#000000;
        }
        QTreeView::item:first{
            border-top-left-radius: 15px;
            border-bottom-left-radius: 15px;
        }
        QTreeView::item:last{
            border-top-right-radius: 15px;
            border-bottom-right-radius: 15px;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 10px;
            border-radius: 4px;
        }
        
        QSlider::sub-page:horizontal {
            background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                stop: 0 #66e, stop: 1 #bbf);
            background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                stop: 0 #bbf, stop: 1 #55f);
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
        }
        
        QSlider::add-page:horizontal {
            background: #fff;
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: -2px;
            margin-bottom: -2px;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff, stop:1 #ddd);
            border: 1px solid #444;
            border-radius: 4px;
        }
        
        QSlider::sub-page:horizontal:disabled {
            background: #bbb;
            border-color: #999;
        }
        
        QSlider::add-page:horizontal:disabled {
            background: #eee;
            border-color: #999;
        }
        
        QSlider::handle:horizontal:disabled {
            background: #eee;
            border: 1px solid #aaa;
            border-radius: 4px;
        }
        
        """ % (self.create_media_path("world.gif")))

        self.ui.lblVolumeLow.setPixmap(QPixmap(self.create_media_path("volume-low.png")).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.ui.lblVolumeHigh.setPixmap(QPixmap(self.create_media_path("volume-high.png")).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.ui.tvPrograms.setModel(QStandardItemModel())
        self.ui.btnStart.clicked.connect(self.on_btnStart_clicked)
        self.ui.btnRefresh.clicked.connect(self.build_items)
        self.ui.btnRestartMenu.clicked.connect(self.close_app)
        #self.ui.tvPrograms.doubleClicked.connect(self.on_btnStart_clicked)
        self.ui.tvPrograms.activated.connect(self.on_btnStart_clicked)
        self.ui.slVolume.valueChanged.connect(self.volumeChanged)
        self.ui.btnBeamer.clicked.connect(self.beamerToggle)
        self.ui.btnBeamer.setIcon(QIcon(self.create_media_path("beamer.png")))
        self.ui.btnInfo.clicked.connect(self.aboutInfo)
        self.ui.btnUmountUSB.clicked.connect(self.umountUSB)
        self.ui.btnUmountUSB.setIcon(QIcon(self.create_media_path("usbdrive.png")))
        self.ui.btnCopyCD.clicked.connect(self.copyCD)
        self.ui.btnCopyCD.setIcon(QIcon(self.create_media_path("cd.png")))

        if c_beamer != "yes":
            self.ui.btnBeamer.hide()

        # Beamer default ausschalten
        if c_beamer == "yes":
            self.run_cmd_stdout("xrandr --output %s --off" % c_beamer_output, argShell=True)

        # Screensaver deaktivieren
        if c_screensaver == "no":
            self.run_cmd_stdout("xset s off", argShell=True)
            self.run_cmd_stdout("xset -dpms", argShell=True)

        if c_umountusb != "yes":
            self.ui.btnUmountUSB.hide()

        if c_copycd != "yes":
            self.ui.btnCopyCD.hide()

        self.updateBeamerStatus()

        self.build_items()

        self.ui.show()

        self.speak(c_sound_greeting)

        #self.readVolume()
        self.ui.slVolume.setValue(int(c_sound_default_level))

        # Starte VMs im Autostart
        if c_autostart_vms != '':
            vms = c_autostart_vms.split(",")
            for vm in vms:
                #print ("start vm:" + vm)
                Popen("vlstartvbmachine vb/%s" % (vm.strip()), shell=True)

        self.app.exec_()

    def close_app(self):
        self.run_cmd_stdout("killall devmon", argShell=True)
        self.run_cmd_stdout("sudo killall lightdm", argShell=True)

    def build_items(self):
        model = self.ui.tvPrograms.model()
        model.clear()

        model.setHorizontalHeaderLabels(["Icon", "Name"])

        # VMs
        #self.add_program_item("vlstartvbmachine vb/kubuntu-test", "Ubuntu 16.04", self.create_media_path("linux.png"))
        #self.add_program_item("vlstartvbmachine vb/kubuntu-test", "Windows 10", self.create_media_path("windows.png"))
        vbhome = ""
        f = open(self.create_media_path("scripts/common"))
        for line in f.readlines():
            if line.startswith("VBHOME"):
                vbhome = line.split("=")[1].strip()
                break
        f.close()

        if DEV_D == True:
            vbhome = "vm/vb"

        if exists(vbhome):
            for item in listdir(vbhome):
                if isdir(vbhome + "/" + item):
                    #print(basename(vbhome), item)
                    ico = "windows.png" if item.find("windows") != -1 or item.find("win") != -1 else "linux.png"
                    self.add_program_item("vlstartvbmachine %s/%s" % (basename(vbhome), item), item.capitalize(), self.create_media_path(ico))

        # Statische Items
        if c_program_teamviewer == "yes": self.add_program_item(c_program_teamviewer_cmd, "Teamviewer", self.create_media_path("teamviewer.png"))
        if c_program_terminal == "yes": self.add_program_item(c_program_terminal_cmd, "Terminal", self.create_media_path("terminal.png"))
        if c_program_browser == "yes": self.add_program_item(c_program_browser_cmd, "Browser", self.create_media_path("browser.png"))

        # Externe Programme hinzufügen
        if exists(base_path_etc + "startmenustudentgui.static"):
            f = open(base_path_etc + "startmenustudentgui.static", "r")
            for line in f.readlines():
                if line.startswith("#"): continue
                param = line.split(",")
                if len(param) == 3:
                    self.add_program_item(param[1].strip(), param[0].strip(), self.create_media_path("default.png") if param[2].strip() == "default" else param[2].strip())

            f.close()

        if exists(base_path_etc + "startmenu.d"):
            for item in listdir(base_path_etc + "startmenu.d"):
                if isfile(base_path_etc + "startmenu.d" + "/" + item):
                    f = open(base_path_etc + "startmenu.d" + "/" + item, "r")
                    for line in f.readlines():
                        if line.startswith("#"): continue
                        param = line.split(",")
                        if len(param) == 3:
                            self.add_program_item(param[1].strip(), param[0].strip(), self.create_media_path("default.png") if param[2].strip() == "default" else param[2].strip())
                        elif len(param) == 4:
                            self.add_program_item(param[1].strip(), param[0].strip(), self.create_media_path("default.png") if param[2].strip() == "default" else param[2].strip(), param[3])

                    f.close()

        # Beenden
        self.add_program_item("quit", "Beenden", self.create_media_path("exit.png"))

    def add_program_item(self, cmd, text, icon="default.png", passhash=""):
        model = self.ui.tvPrograms.model()

        item1 = QStandardItem()
        item1.setIcon(QIcon(icon))
        item1.setData(cmd)
        item1.setData(passhash, self.ITEM_DATA_PASSWORD)

        item2 = QStandardItem()
        item2.setText(text)
        font = item2.font()
        font.setPixelSize(18)
        item2.setFont(font)

        row = model.rowCount()
        model.setItem(row, 0, item1)
        model.setItem(row, 1, item2)

    def on_btnStart_clicked(self):
        model = self.ui.tvPrograms.model()
        selmodel = self.ui.tvPrograms.selectionModel()
        sellist = selmodel.selectedRows()

        if len(sellist) != 1:
            return

        item = model.itemFromIndex(sellist[0])
        passhash = item.data(self.ITEM_DATA_PASSWORD)

        if passhash != "":
            input_pass, ok = QInputDialog.getText(self.ui, "Passwort wird benötigt", "Passwort:", QLineEdit.Password, "")
            if ok == True:
                hash = hashlib.sha256(input_pass.encode('utf-8')).hexdigest()
                if hash != passhash:
                    QMessageBox.warning(self.ui, "Passwort nicht korrekt", "Es wurde kein korrektes Passwort angegeben.")
                    return
            else:
                return

        if item.data() == "quit":
            self.speak("Desktop wird beendet.")
            #self.app.quit()
            Popen("sudo shutdown -h now", shell=True)
            return

        self.speak("%s wird gestartet" % model.item(item.row(), 1).text())
        if "vlstartvbmachine" in item.data():
            (ret, retval) = self.run_cmd_stdout(item.data(), argShell=True)
            if "VBoxManage: error" in retval:
                QMessageBox.critical(self.ui, "Fehler bei VM-Start", retval)
        else:
            Popen(item.data(), shell=True)

    def create_media_path(self, file):
        return base_path_media + file

    def speak(self, text):
        if(c_sound == "yes"):
            Popen("espeak -vmb-de6 -s 110 -p 45 '%s'" % text, shell=True)

    def readVolume(self):
        (ret, out) = self.run_cmd_stdout("amixer -D pulse sget Master", argShell=True) if DEV_D == True else self.run_cmd_stdout("amixer sget Master", argShell=True)
        m = re.search('.*\[([0-9]{1,3})%\].*', out)
        slevel = 80 if m == None else re.search('.*\[([0-9]{1,3})%\].*', out).group(1)
        self.ui.slVolume.setValue(int(slevel))

    def setVolume(self, val):
        if DEV_D == True:
            self.run_cmd_stdout("amixer -D pulse sset Master %s%%" % val, argShell=True)
        else:
            self.run_cmd_stdout("amixer sset Master %s%%" % val, argShell=True)

    def volumeChanged(self):
        self.setVolume(self.ui.slVolume.value())

    def run_cmd_stdout(self, command, argShell=False):
        p = Popen(command, stdout=PIPE, shell=argShell)
        ret = p.wait()
        return (ret, p.stdout.read().decode('UTF-8'))

    def updateBeamerStatus(self):
        if exists("/tmp/beamer"):
            self.ui.btnBeamer.setText("Beamer ausschalten (%s)" % c_beamer_output)
        else:
            self.ui.btnBeamer.setText("Beamer einschalten (%s)" % c_beamer_output)

    def beamerToggle(self):
        self.run_cmd_stdout("/usr/bin/toggle_beamer %s" % c_beamer_output, argShell=True)
        self.updateBeamerStatus()

    def umountUSB(self):
        self.run_cmd_stdout("devmon -u --no-gui", argShell=True)
        QMessageBox.information(self.ui, "USB-Laufwerke aushängen", "USB-Laufwerke wurden ausgehängt, das Laufwerk kann nun entfernt werden.")

    def copyCD(self):
        self.win_cdburn = ieduCopyCD(self.ui, base_path_media)

    def aboutInfo(self):
        (ret, out) = self.run_cmd_stdout("apt show iedu-client", argShell=True)
        out = out.replace("<", "&lt;").replace(">", "&gt;")
        out = re.sub(r'APT-Sources: .*', '', out)
        out = re.sub(r'\n', '<br>', out)
        (uret, uout) = self.run_cmd_stdout("uname -a", argShell=True)
        QMessageBox.about(self.ui, "Über i-EDU", "<b>Paketinformationen:</b> "
                                                           "<p><b>Supportinformation:</b> <a href='http://i-edu.at'>www.i-edu.at</a>, support@i-edu.at</p> "
                                                           "<p><b>System:</b> %s</p>"
                                                           "<p>%s</p>" % (uout, out))


if __name__ == '__main__':
    MainMenu()
