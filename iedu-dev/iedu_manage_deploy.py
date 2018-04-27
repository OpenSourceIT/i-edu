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
import re

from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from paramiko import *
from os import listdir
from netaddr import IPNetwork
from time import sleep

from iedu.config import *
from iedu.network import ieduNetworkHelper
from iedu.common import ieduCommonHelper
from iedu.widgets import ieduNICComboBoxDelegate

from iedu_manage_progress import ieduManageProgress

logging.getLogger("paramiko").setLevel(logging.INFO)
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ieduConfig = ieduConfig()

class ieduManageDeploy():

    parent_win = 0
    clients = {}

    DEFAULT_CONFIGS = ["init.sh", "exec.sh"]
    DEFAULT_DATA_TYPES = {
        "all": "VM-Dateien und Konfigurationen",
        "config": "Nur Konfigurationen"
    }

    def __init__(self, parent, clients):
        self.ui = QMainWindow(parent, Qt.Dialog)
        self.widget = uic.loadUi(ieduConfig.create_media_path("iedu_manage_deploy.ui"))  # type: QDialog
        self.ui.setCentralWidget(self.widget)
        self.ui.setWindowModality(Qt.WindowModal)
        self.ui.setMinimumSize(self.widget.width(), self.widget.height())
        self.ui.setWindowTitle(parent.windowTitle() + " - Ausrollen")

        self.lvHosts = self.widget.lvHosts # type: QTreeView
        self.lvHosts.setModel(QStandardItemModel(self.ui))
        self.lvHosts.setItemDelegateForColumn(1, ieduNICComboBoxDelegate())
        self.lvVMs = self.widget.lvVMs  # type: QListView
        self.lvVMs.setModel(QStandardItemModel(self.ui))
        self.lvConfigs = self.widget.lvConfigs  # type: QListView
        self.lvConfigs.setModel(QStandardItemModel(self.ui))

        #self.cbNetworks = self.widget.cbNetworks  # type: QComboBox
        self.cbDataTypes = self.widget.cbDataTypes  # type: QComboBox

        self.btnCancel = self.widget.btnCancel  # type: QPushButton
        self.btnCancel.clicked.connect(self.on_btnCancel_clicked)
        self.btnDeploy = self.widget.btnDeploy  # type: QPushButton
        self.btnDeploy.clicked.connect(self.on_btnDeploy_clicked)

        self.parent_win = parent

        # Testdata
        """
        clients["10.69.99.142"] = {}
        clients["10.69.99.142"]["name"] = "testlocal1"
        clients["10.69.99.142"]["bgcolor"] = QColor("#44ffff")

        clients["10.69.99.141"] = {}
        clients["10.69.99.141"]["name"] = "testlocal2"
        clients["10.69.99.141"]["bgcolor"] = QColor("#44ffff")
        """

        self.clients = clients

        self.initClients()
        #self.initNetwork()
        self.initVMs()
        self.initConfigs()
        self.initDataTypes()

        self.computeDeployRoadmap()

        #
        self.lvHosts.model().itemChanged.connect(self.on_lvHosts_itemChanged)

        self.ui.show()

    def initClients(self):
        mHosts = self.lvHosts.model()
        mHosts.clear()

        mHosts.setHorizontalHeaderLabels(["Client", "NIC", "NIC-Netzwerk"])
        self.lvHosts.header().resizeSection(0, 350)
        self.lvHosts.header().resizeSection(1, 200)

        networks = ieduNetworkHelper.get_net_interfaces()

        for clientip, clientdata in self.clients.items():
            item1 = QStandardItem()
            item1.setText("%s (%s)" % (clientdata["name"], clientip))
            item1.setData(clientip)
            item1.setData(clientdata["bgcolor"], Qt.BackgroundColorRole)
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/host.png")))
            item1.setCheckable(True)
            item1.setEditable(False)
            item1.setCheckState(Qt.Checked)

            row = mHosts.rowCount()
            mHosts.setItem(row, 0, item1)
            foundRolloutNIC = False

            for interface, data in networks.items():
                if data["ip"] == "":
                    continue

                if IPNetwork(data["fqip"]) == IPNetwork(clientip + "/" + data["cidr"]):
                    item2 = QStandardItem()
                    item2.setText("%s" % (interface))
                    item2.setData(interface)
                    mHosts.setItem(row, 1, item2)
                    item3 = QStandardItem()
                    item3.setText("%s" % (data["fqip"]))
                    item3.setData(interface)
                    item3.setEditable(False)
                    mHosts.setItem(row, 2, item3)
                    foundRolloutNIC = True
                    break

            if foundRolloutNIC == False:
                item2 = QStandardItem()
                item2.setText("")
                item2.setData("")
                mHosts.setItem(row, 1, item2)
                item3 = QStandardItem()
                item3.setText("Kein NIC gefunden")
                item3.setData("")
                item3.setEditable(False)
                mHosts.setItem(row, 2, item3)

    def initNetwork(self):
        self.cbNetworks.clear()

        for interface, data in ieduNetworkHelper.get_net_interfaces().items():
            self.cbNetworks.insertItem(self.cbNetworks.count(), QIcon(ieduConfig.create_media_path("gui-icons/nic.png")), "%s (%s)" % (interface, data["ip"]), interface)

    def initVMs(self):
        mVMs = self.lvVMs.model()
        mVMs.clear()

        for vm in ieduCommonHelper.availVMs():
            item1 = QStandardItem()
            item1.setText(vm)
            item1.setData(vm)
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/vm.png")))
            item1.setCheckable(True)

            row = mVMs.rowCount()
            mVMs.setItem(row, 0, item1)

    def initConfigs(self):
        mConfigs = self.lvConfigs.model()
        mConfigs.clear()

        for config in self.DEFAULT_CONFIGS:
            item1 = QStandardItem()
            item1.setText(config)
            item1.setData(config)
            item1.setIcon(QIcon(ieduConfig.create_media_path("gui-icons/config.png")))
            item1.setCheckable(True)
            item1.setCheckState(Qt.Checked)

            row = mConfigs.rowCount()
            mConfigs.setItem(row, 0, item1)

    def initDataTypes(self):
        self.cbDataTypes.clear()

        for type, desc in self.DEFAULT_DATA_TYPES.items():
            self.cbDataTypes.insertItem(self.cbDataTypes.count(), QIcon(ieduConfig.create_media_path("gui-icons/data.png")), "%s (%s)" % (desc, type), type)

        self.cbDataTypes.setCurrentIndex(self.cbDataTypes.findData("all"))

    def computeDeployRoadmap(self):
        networks = ieduNetworkHelper.get_net_interfaces()
        network_vm_assignment = {}
        model = self.lvHosts.model()  # type: QStandardItemModel
        ic = 0
        while ic < model.rowCount():
            item = model.item(ic, 0)  # type: QStandardItem
            if item.checkState() == Qt.Checked:
                for interface, data in networks.items():
                    if data["ip"] == "":
                        continue

                    if IPNetwork(data["fqip"]) == IPNetwork(item.data() + "/" + data["cidr"]):
                        if interface in network_vm_assignment:
                            network_vm_assignment[interface].append(item.data())
                        else:
                            network_vm_assignment[interface] = []
                            network_vm_assignment[interface].append(item.data())

                        break

            ic += 1

        return network_vm_assignment

    def on_lvHosts_itemChanged(self, item):
        if item.column() != 1:
            return

        mHosts = self.lvHosts.model() # type: QStandardItemModel
        descItem = mHosts.item(item.row(), 2)
        networks = ieduNetworkHelper.get_net_interfaces()
        foundRolloutNIC = False
        for interface, data in networks.items():
            if data["ip"] == "":
                continue

            print(interface, item.text(), "--------")
            if interface == item.text():
                item.setData(interface)
                descItem.setText("%s" % (data["fqip"]))
                foundRolloutNIC = True
                break

        if foundRolloutNIC == False:
            descItem.setText("Kein NIC gefunden")
            item.setText("")
            item.setData("")

    def on_btnCancel_clicked(self):
        self.ui.hide()

    def on_btnDeploy_clicked(self):
        # Collect data

        iedu_client_deploy = self.computeDeployRoadmap()

        iedu_vms = []
        model = self.lvVMs.model()
        ic = 0
        while ic < model.rowCount():
            item = model.item(ic, 0)  # type: QStandardItem
            if item.checkState() == Qt.Checked:
                iedu_vms.append(item.data())

            ic += 1

        iedu_configs = []
        model = self.lvConfigs.model()
        ic = 0
        while ic < model.rowCount():
            item = model.item(ic, 0)  # type: QStandardItem
            if item.checkState() == Qt.Checked:
                iedu_configs.append(item.data())

            ic += 1

        iedu_data_type = self.cbDataTypes.currentData()

        if len(iedu_client_deploy) == 0:
            QMessageBox.warning(self.ui, self.ui.windowTitle(), "Sie muessen einen Client auswaehlen!")
            return

        if len(iedu_vms) == 0:
            QMessageBox.warning(self.ui, self.ui.windowTitle(), "Sie muessen eine VM zum verteilen auswaehlen!")
            return

        print(iedu_client_deploy)
        print(iedu_vms)
        print(iedu_configs)
        print(iedu_data_type)

        self.win_status = ieduManageProgress(self.ui)
        self.win_status.showProgressBar()

        # Start worker thread
        self.deploy_thread = QThread()
        self.deploy_thread.setTerminationEnabled(True)
        self.deploy_worker = ieduManageDeployWorker()
        self.win_status.abort.connect(self.deploy_worker.abort)
        self.deploy_worker.setData(self.deploy_thread, iedu_client_deploy, iedu_vms, iedu_configs, iedu_data_type)
        self.deploy_worker.moveToThread(self.deploy_thread)
        self.deploy_thread.started.connect(self.deploy_worker.process)
        self.deploy_worker.started.connect(self.win_status.started)
        self.deploy_worker.finished.connect(self.deploy_thread.quit)
        self.deploy_worker.finished.connect(self.win_status.finished)
        self.deploy_worker.hostupdate.connect(self.win_status.updateClientStatus)
        self.deploy_worker.logupdate.connect(self.win_status.appendLog)
        self.deploy_worker.progressmax.connect(self.win_status.setProgressMax)
        self.deploy_worker.progressupdate.connect(self.win_status.setProgressUpdate)
        self.deploy_worker.progressreset.connect(self.win_status.resetProgressbar)
        self.deploy_thread.start()

class ieduManageDeployWorker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    hostupdate = pyqtSignal(str, str, str)
    logupdate = pyqtSignal(str)
    progressmax = pyqtSignal(int)
    progressupdate = pyqtSignal(int)
    progressreset = pyqtSignal()

    iedu_client_deploy = {}
    iedu_vms = []
    iedu_configs = []
    iedu_data_type = ""

    cur_nic = ""
    proc = QProcess()
    thread = QThread()

    def setData(self, thread, client_deploy, vms, configs, type):
        self.thread = thread
        self.iedu_client_deploy = client_deploy
        self.iedu_vms = vms
        self.iedu_configs = configs
        self.iedu_data_type = type

    def process(self):

        self.logupdate.emit("Starte Verteilungs-Thread")
        self.started.emit()

        # Generate udpcastlist
        for interface, clients in self.iedu_client_deploy.items():
            self.cur_nic = interface
            self.progressreset.emit()
            if self.iedu_data_type == "all":

                readyClients = 0
                for cclient in clients:
                    self.hostupdate.emit(cclient, ieduManageProgress.STATUS["INFO"], "Starte udpcast")
                    print(cclient)

                    try:
                        client = SSHClient()
                        client.load_system_host_keys()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        client.connect(cclient, username="root", port=22)
                        stdin, stdout, stderr = client.exec_command('killall vludpreceiveVMs udp-receiver; exec vludpreceiveVMs >/tmp/udpcast.log 2>&1')
                        client.close()
                        self.hostupdate.emit(cclient, ieduManageProgress.STATUS["OK"], "UDPcast-Client erfolgreich gestartet.")
                        readyClients += 1

                    except Exception as inst:
                        self.hostupdate.emit(cclient, ieduManageProgress.STATUS["ERROR"], "UDPcast-Client nicht erfolgreich gestartet. (%s)" % inst)
                        print(inst)

                if readyClients > 0:
                    totalfilesize = 0
                    f = open("/vm/udpcastlist", "w+")
                    for vm_import in self.iedu_vms:
                        if exists(VM_ROOT + vm_import):
                            for item in listdir(VM_ROOT + vm_import):
                                if isfile(VM_ROOT + vm_import + "/" + item):
                                    if item.endswith("sh") or item.endswith("vdi"):
                                        if item.endswith("sh") and item not in self.iedu_configs:
                                            continue

                                        f.write("vb/%s/%s\n" % (vm_import, item))
                                        totalfilesize += os.path.getsize(VM_ROOT + vm_import + "/" + item)

                    f.close()
                    self.progressmax.emit(totalfilesize/1024)

                    self.logupdate.emit("UDPcast-Prozess  wird gestartet für Interface %s" % interface)
                    self.proc = QProcess()
                    self.proc.readyReadStandardOutput.connect(self.procUDPCastRead)
                    self.proc.finished.connect(self.procUDPCastFinished)
                    self.proc.started.connect(self.procUDPCastStarted)
                    # QT >= 5.6 only
                    #self.proc.errorOccurred.connect(self.procUDPCastErrorOccurred)
                    self.proc.readyReadStandardError.connect(self.procUDPCastError)
                    self.proc.start("bash -c \"cd /vm; tar -cv udpcastlist `cat udpcastlist` | udp-sender --nokbd --full-duplex --min-receivers=%s --interface %s\"" % (readyClients, interface))
                    self.proc.waitForFinished(-1)
                else:
                    self.logupdate.emit("Keine Clients für UDPcast-Prozess für Interface %s bereit, UDPcast wird nicht gestartet" % interface)

            elif self.iedu_data_type == "config":

                for cclient in clients:
                    self.hostupdate.emit(cclient, ieduManageProgress.STATUS["INFO"], "Starte Configverteilung")

                    try:
                        client = SSHClient()
                        client.load_system_host_keys()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        client.connect(cclient, username="root", port=22)
                        csftp = client.open_sftp()

                        for vm_import in self.iedu_vms:
                            if exists(VM_ROOT + vm_import):
                                for item in listdir(VM_ROOT + vm_import):
                                    if isfile(VM_ROOT + vm_import + "/" + item):
                                        if item.endswith("sh"):
                                            if item not in self.iedu_configs:
                                                continue

                                            filestr = VM_ROOT + vm_import + "/" + item
                                            csftp.put(filestr, filestr)
                                            client.exec_command('chown student:student ' + filestr)
                                            client.exec_command('chmod +x ' + filestr)

                        client.exec_command('/opt/puppetlabs/bin/puppet agent --test > /tmp/puppetrundeploy')

                        client.close()
                        self.hostupdate.emit(cclient, ieduManageProgress.STATUS["OK"], "Configverteilung erfolgreich.")
                    except Exception as inst:
                        self.hostupdate.emit(cclient, ieduManageProgress.STATUS["ERROR"], "Configverteilung nicht erfolgreich (%s)" % inst)

                self.logupdate.emit("Configverteilung abgeschlossen für Interface %s" % interface)

        self.logupdate.emit("Beende Verteilungs-Thread")
        self.finished.emit()

    def abort(self):
        print("abort process")
        self.logupdate.emit("Prozess wird abgebrochen")
        self.proc.terminate()
        sleep(2)
        self.proc.kill()

        self.thread.quit()
        self.thread.terminate()

    def procUDPCastStarted(self):
        self.logupdate.emit("UDPcast Prozess gestartet für Interface %s" % self.cur_nic)

    def procUDPCastErrorOccurred(self, error):
        self.logupdate.emit("Ein Fehler ist aufgetreten für den UDPcast Prozess für Interface %s, Fehlercode: %s" % (self.cur_nic, error))

    def procUDPCastRead(self):
        self.logupdate.emit("UDPcast: %s" % self.proc.readAllStandardOutput())

    def procUDPCastError(self):
        out = str(self.proc.readAllStandardError(), encoding='utf-8')
        self.logupdate.emit("UDPcast: %s" % out)

        m = re.search("bytes= ([ 0-9]*)K", out)
        if m != None:
            btransfer = int(m.group(1).replace(" ", ""))
            self.progressupdate.emit(btransfer)

    def procUDPCastFinished(self, exitcode, exitstatus):
        self.logupdate.emit("UDPcast-Verteilung abgeschlossen für Interface %s" % self.cur_nic)