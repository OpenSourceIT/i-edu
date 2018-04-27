#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import re
import logging
import urllib3
import requests
import signal

from PyQt5 import uic

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    from iedu.config import *
    from iedu_manage_deploy import ieduManageDeploy
    from iedu_manage_cmd import ieduManageCMD
    from iedu.common import ieduCommonHelper
    from iedu.network import ieduNetworkHelper
except:
    import os
    import sys
    WORK_DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(WORK_DIR + "/usr/lib/python3/dist-packages")
    from iedu.config import *
    from iedu_manage_deploy import ieduManageDeploy
    from iedu_manage_cmd import ieduManageCMD
    from iedu.common import ieduCommonHelper
    from iedu.network import ieduNetworkHelper

logging.getLogger("paramiko").setLevel(logging.INFO)
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ieduConfig = ieduConfig()

class MainMenu:

    DATA_HOSTGROUP_ID = Qt.UserRole + 2
    DATA_HOSTGROUP_COLOR = Qt.UserRole + 3
    DATA_CLIENT_MAC = Qt.UserRole + 4
    HOSTGROUP_COLORS = ["#D7E3E9", "#C0D6E9", "#A9C2EA", "#92A7EB"]

    HOST_STATUS_ONLINE = "ONLINE"
    HOST_STATUS_OFFLINE = "OFFLINE"

    hostcheck_timer = ""
    hostcheck_threads = {}
    hostcheck_workers = {}

    def __init__(self):
        self.app = QApplication(sys.argv)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.ui = uic.loadUi(ieduConfig.create_media_path("iedu_manage_main.ui")) # type: QMainWindow

        geom = QApplication.desktop().availableGeometry()
        self.ui.move((geom.width() - self.ui.width()) / 2, (geom.height() - self.ui.height()) / 2)
        self.ui.setWindowIcon(QIcon(ieduConfig.create_media_path("app.png")))
        QApplication.setWindowIcon(QIcon(ieduConfig.create_media_path("app.png")))

        self.ui.lvHostGroups.setModel(QStandardItemModel(self.ui))
        #self.ui.lvHostGroups.setStyleSheet("QListView:item:selected{border: 1px solid red;}");
        self.ui.lvHosts.setModel(QStandardItemModel(self.ui))
        self.ui.lvHostsSelection.setModel(QStandardItemModel(self.ui))
        self.ui.lvHostsSelection.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.ui.lvHostsSelection.setSelectionRectVisible(True)
        self.ui.lvHostsSelection.dropItems.connect(self.on_lvHostsSelection_dropItems)

        self.ui.mnuFileExit.triggered.connect(self.ui.close)
        self.ui.mnuHelpAbout.triggered.connect(self.aboutInfo)

        self.ui.tbMain.addAction(QIcon(ieduConfig.create_media_path("gui-icons/deploy.png")), "Ausrollen", self.on_actionRollout)
        self.ui.tbMain.addAction(QIcon(ieduConfig.create_media_path("gui-icons/cmd.png")), "Befehl ausführen", self.on_actionSendCMD)
        self.ui.tbMain.addSeparator()
        self.ui.tbMain.addAction(QIcon(ieduConfig.create_media_path("gui-icons/wol.png")), "WOL", self.on_actionWOL)
        self.ui.tbMain.addAction(QIcon(ieduConfig.create_media_path("gui-icons/reboot.png")), "Reboot", self.on_actionReboot)
        self.ui.tbMain.addAction(QIcon(ieduConfig.create_media_path("gui-icons/off.png")), "Ausschalten", self.on_actionShutdown)

        self.ui.lvHostGroups.clicked.connect(self.on_lvHostGroups_clicked)
        self.ui.btnHostgroupRefresh.clicked.connect(self.on_btnHostgroupRefresh_clicked)
        self.ui.btnHostsAddAll.clicked.connect(self.on_btnHostsAddAll_clicked)
        self.ui.btnHostsAddSelected.clicked.connect(self.on_btnHostsAddSelected_clicked)
        self.ui.btnRemoveSelection.clicked.connect(self.on_btnRemoveSelection_clicked)
        self.ui.btnClearSelection.clicked.connect(self.on_btnClearSelection_clicked)
        self.ui.slItemSize.valueChanged.connect(self.on_slItemSize_valueChanged)

        self.build_lvHostgroups()

        self.ui.show()

        self.hostcheck_timer = QTimer()
        self.hostcheck_timer.timeout.connect(self.checkHostStatusAll)
        self.hostcheck_timer.start(30000)

        self.app.exec_()

    def build_lvHostgroups(self):
        mHostGroups = self.ui.lvHostGroups.model()
        mHostGroups.clear()

        try:
            response = requests.get("https://%s/api/hostgroups" % FOREMAN_HOST, verify=False, auth=(FOREMAN_USER, FOREMAN_PASS))
        except Exception as err:
            QMessageBox.warning(self.ui, "Verbindungsfehler Foreman", "Es konnte keine Verbindung zum Server %s aufgebaut werden: \n\n%s" % (FOREMAN_HOST, err))
            return

        i = 0
        colors_avail = len(self.HOSTGROUP_COLORS)
        for hostgroup in response.json()["results"]:
            item1 = QStandardItem()
            hostgroup_name = hostgroup["name"] if hostgroup["parent_name"] == None else hostgroup["parent_name"] + "/" + hostgroup["name"]
            item1.setText(hostgroup_name)
            item1.setData(hostgroup["id"])
            if i < colors_avail:
                item1.setData(QColor(self.HOSTGROUP_COLORS[i]), Qt.BackgroundColorRole)
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/hostgroup.png")))

            row = mHostGroups.rowCount()
            mHostGroups.setItem(row, 0, item1)
            i+=1

    def addItem2HostsSelection(self, text, data, color, mac):
        mHostsSelection = self.ui.lvHostsSelection.model()  # type: QStandardItemModel
        row = mHostsSelection.rowCount()
        rowi = 0
        dup = False
        while rowi < row:
            citem = mHostsSelection.item(rowi)
            if citem.data() == data:
                dup = True

            rowi += 1

        if dup == True:
            return

        item2 = QStandardItem()
        item2.setText(text)
        item2.setData(data)
        item2.setData(color, Qt.BackgroundColorRole)
        item2.setData(mac, self.DATA_CLIENT_MAC)
        item2.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/host.png")))

        mHostsSelection.setItem(row, 0, item2)

    def on_btnHostsAddSelected_clicked(self):
        mHosts = self.ui.lvHosts.model()  # type: QStandardItemModel
        selHosts = self.ui.lvHosts.selectionModel()
        sellist = selHosts.selectedRows()
        for index in sellist:
            item = mHosts.itemFromIndex(index)
            self.addItem2HostsSelection(item.text(), item.data(), item.data(self.DATA_HOSTGROUP_COLOR), item.data(self.DATA_CLIENT_MAC))

    def on_btnRemoveSelection_clicked(self):
        mSelection = self.ui.lvHostsSelection.model()  # type: QStandardItemModel
        selSelection = self.ui.lvHostsSelection.selectionModel()
        sellist = selSelection.selectedRows()
        ci = mSelection.rowCount() - 1
        while ci >= 0:
            for sel in sellist:
                if sel.row() == ci:
                    mSelection.removeRow(ci)
            ci -=1

    def on_btnClearSelection_clicked(self):
        self.ui.lvHostsSelection.model().clear()

    def on_btnHostgroupRefresh_clicked(self):
        self.build_lvHostgroups()

    def on_btnHostsAddAll_clicked(self):
        mHosts = self.ui.lvHosts.model() # type: QStandardItemModel
        itemc = mHosts.rowCount()
        ic = 0
        while ic < itemc:
            item = mHosts.item(ic)
            self.addItem2HostsSelection(item.text(), item.data(), item.data(self.DATA_HOSTGROUP_COLOR))
            ic +=1

    def on_lvHostsSelection_dropItems(self, items):
        for item in items:
            self.addItem2HostsSelection(item[Qt.DisplayRole].value(), item[Qt.UserRole + 1].value(), item[self.DATA_HOSTGROUP_COLOR].value(), item[self.DATA_CLIENT_MAC].value())


    def on_lvHostGroups_clicked(self, index):
        mHostGroups = self.ui.lvHostGroups.model()
        mHosts = self.ui.lvHosts.model()
        item = mHostGroups.item(index.row())
        mHosts.clear()

        try:
            response = requests.get("https://%s/api/hosts" % FOREMAN_HOST, verify=False, auth=(FOREMAN_USER, FOREMAN_PASS), data={"search": "hostgroup_id=%s" % item.data(), "per_page": 100})
        except Exception as err:
            QMessageBox.warning(self.ui, "Verbindungsfehler Foreman", "Es konnte keine Verbindung zum Server %s aufgebaut werden: \n\n%s" % (FOREMAN_HOST, err))
            return

        for client in response.json()["results"]:
            item2 = QStandardItem()
            item2.setText(client["name"])
            item2.setData(client["ip"])
            item2.setData(item.data(), self.DATA_HOSTGROUP_ID)
            item2.setData(item.data(Qt.BackgroundColorRole), self.DATA_HOSTGROUP_COLOR)
            item2.setData(client["mac"], self.DATA_CLIENT_MAC)
            item2.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/host_offline.png")))

            self.checkHostStatus(item2)

            row = mHosts.rowCount()
            mHosts.setItem(row, 0, item2)

    def on_slItemSize_valueChanged(self, val):
        self.ui.lvHosts.setIconSize(QSize(val, val))

    def on_actionRollout(self):
        model = self.ui.lvHostsSelection.model()
        clients = {}

        if self.checkHostsSelectionEmpty():
            return

        for i in range(0, model.rowCount()):
            item = model.item(i)
            clients[item.data()] = {}
            clients[item.data()]["name"] = item.text()
            clients[item.data()]["bgcolor"] = item.data(Qt.BackgroundColorRole)

        self.ui_deploy = ieduManageDeploy(self.ui, clients)

    def on_actionWOL(self):
        model = self.ui.lvHostsSelection.model()

        if self.checkHostsSelectionEmpty():
            return

        for i in range(0, model.rowCount()):
            item = model.item(i)
            ieduNetworkHelper.send_wol_packet(item.data(self.DATA_CLIENT_MAC))

    def on_actionReboot(self):
        model = self.ui.lvHostsSelection.model()

        if self.checkHostsSelectionEmpty():
            return

        for i in range(0, model.rowCount()):
            item = model.item(i)
            ieduNetworkHelper.send_ssh_cmd(item.data(), "reboot")

    def on_actionShutdown(self):
        model = self.ui.lvHostsSelection.model()

        if self.checkHostsSelectionEmpty():
            return

        for i in range(0, model.rowCount()):
            item = model.item(i)
            ieduNetworkHelper.send_ssh_cmd(item.data(), "shutdown -h now")

    def on_actionSendCMD(self):
        model = self.ui.lvHostsSelection.model()
        clients = {}

        if self.checkHostsSelectionEmpty():
            return

        for i in range(0, model.rowCount()):
            item = model.item(i)
            clients[item.data()] = {}
            clients[item.data()]["name"] = item.text()
            clients[item.data()]["bgcolor"] = item.data(Qt.BackgroundColorRole)

        self.ui_cmd = ieduManageCMD(self.ui, clients)

    def checkHostsSelectionEmpty(self):
        model = self.ui.lvHostsSelection.model()

        if model.rowCount() == 0:
            QMessageBox.information(self.ui, "Keine Auswahl", "Es wurden keine Hosts ausgewählt für diese Aktion.")
            return True

        return False

    def aboutInfo(self):
        (ret, out) = ieduCommonHelper.run_cmd_stdout("apt show iedu-server", argShell=True)
        out = out.replace("<", "&lt;").replace(">", "&gt;")
        out = re.sub(r'APT-Sources: .*', '', out)
        out = re.sub(r'\n', '<br>', out)
        (uret, uout) = ieduCommonHelper.run_cmd_stdout("uname -a", argShell=True)
        QMessageBox.about(self.ui, "Über i-EDU", "<b>Paketinformationen:</b> "
                                                           "<p><b>Supportinformation:</b> <a href='http://i-edu.at'>www.i-edu.at</a>, support@i-edu.at</p> "
                                                           "<p><b>System:</b> %s</p>"
                                                           "<p>%s</p>" % (uout, out))

    def checkHostStatus(self, item):
        # Start worker thread
        thcnext = len(self.hostcheck_threads)

        self.hostcheck_threads[thcnext] = QThread()
        self.hostcheck_workers[thcnext] = checkHostStatusWorker()
        self.hostcheck_workers[thcnext].setData(item.text(), item.data())
        self.hostcheck_workers[thcnext].moveToThread(self.hostcheck_threads[thcnext])
        self.hostcheck_threads[thcnext].started.connect(self.hostcheck_workers[thcnext].process)
        self.hostcheck_workers[thcnext].finished.connect(self.hostcheck_threads[thcnext].quit)
        self.hostcheck_workers[thcnext].hoststatusupdate.connect(self.updateHostStatus)
        self.hostcheck_threads[thcnext].start()

    def checkHostStatusAll(self):
        mHosts = self.ui.lvHosts.model()  # type: QStandardItemModel
        items = mHosts.findItems(".*", Qt.MatchRegExp)
        for item in items:
            self.checkHostStatus(item)

    def updateHostStatus(self, host, status):
        mHosts = self.ui.lvHosts.model() # type: QStandardItemModel
        item = mHosts.findItems(host)
        if(len(item) != 1):
            return

        if(status == self.HOST_STATUS_ONLINE):
            item[0].setIcon(QIcon(ieduConfig.create_media_path("gui-icons/host_online.png")))
        else:
            item[0].setIcon(QIcon(ieduConfig.create_media_path("gui-icons/host_offline.png")))


class checkHostStatusWorker(QObject):
    finished = pyqtSignal()
    hoststatusupdate = pyqtSignal(str, str)

    cur_hostname = ""
    cur_ip = ""

    def setData(self, hostname, ip):
        self.cur_hostname = hostname
        self.cur_ip = ip

    def process(self):
        self.proc = QProcess()
        self.proc.start("ping -c1 -W2 %s" % (self.cur_ip))
        self.proc.waitForFinished(-1)
        status = MainMenu.HOST_STATUS_OFFLINE

        if(self.proc.exitCode() == 0):
            status = MainMenu.HOST_STATUS_ONLINE

        self.hoststatusupdate.emit(self.cur_hostname, status)

        self.finished.emit()

if __name__ == '__main__':
    MainMenu()
