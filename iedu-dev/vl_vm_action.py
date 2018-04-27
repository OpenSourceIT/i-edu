#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import sys
import os
import time

from subprocess import Popen, PIPE
from os.path import isdir, basename, exists, isfile
from os import listdir

if len(sys.argv) != 3:
    print("Es wurde nicht die richtige Anzahl an Argumenten übergeben")
    sys.exit(1)

action = sys.argv[1]
vm = sys.argv[2]

#VLIZEDLAB_BASE = "etc"
VLIZEDLAB_BASE = "/etc/vlizedlab"
VM_USB_FILTER_FILE = VLIZEDLAB_BASE + "/vm_usb_filters"
VM_USB_FILTER_D = VLIZEDLAB_BASE + "/vm_usb_filter.d"

VM_SETTING = VLIZEDLAB_BASE + "/vm_setting.d/vm-" + vm

ACTIONS = ["config", "usb"]

USB_MODES = ["off", "usb", "usbehci", "usbxhci"]

if action not in ACTIONS:
    print("Die gesetzte ACTION <%s> wurde nicht definiert, verfügbar: %s" % (action, ", ".join(ACTIONS)))
    sys.exit(1)

if action == "usb":
    idx = 0
    if exists(VM_USB_FILTER_FILE):
        with open(VM_USB_FILTER_FILE, "r") as f:
            for line in f.readlines():
                if line.startswith("#"):
                    continue

                usbe = line.split(",")
                if len(usbe) != 3:
                    continue

                if usbe[0] == vm:
                    strexe = "VBoxManage --nologo usbfilter add %s --target %s --name 'usb-device-%s-%s' --vendorid %s" % (idx, vm, vm, idx, usbe[1])
                    if usbe[2].strip() != "":
                        strexe += " --productid %s" % usbe[2].strip()

                    idx += 1

                    print(strexe)
                    p = Popen(strexe, shell=True)
                    p.wait()

    if exists(VM_USB_FILTER_D):
        for item in listdir(VM_USB_FILTER_D):
            if isfile(VM_USB_FILTER_D + "/" + item):
                f = open(VM_USB_FILTER_D + "/" + item, "r")
                for line in f.readlines():
                    if line.startswith("#"):
                        continue

                    usbe = line.split(",")
                    if len(usbe) != 3:
                        continue

                    if usbe[0] == vm:
                        strexe = "VBoxManage --nologo usbfilter add %s --target %s --name 'usb-device-%s-%s' --vendorid %s" % (idx, vm, vm, idx, usbe[1])
                        if usbe[2].strip() != "":
                            strexe += " --productid %s" % usbe[2].strip()

                        idx += 1

                        print(strexe)
                        p = Popen(strexe, shell=True)
                        p.wait()

                f.close()

elif action == "config":
    if exists(VM_SETTING):
        # Default settings
        network = "nat"
        macaddr = ""
        bridgeadapter = "enp1s0"
        usbmode = "usbehci"
        accelerate2dvideo = "on"
        accelerate3d = "off"
        monitorcount = "1"

        with open(VM_SETTING, "r") as f:
            for line in f.readlines():
                if line.startswith("#"):
                    continue

                conf = line.strip().split("=")
                if len(conf) != 2 or conf[1] == "":
                    continue

                if conf[0] == "network":
                    network = conf[1].strip()
                elif conf[0] == "macaddr":
                    macaddr = conf[1].strip()
                elif conf[0] == "bridgeadapter":
                    bridgeadapter = conf[1].strip()
                elif conf[0] == "accelerate2dvideo":
                    accelerate2dvideo = conf[1].strip()
                elif conf[0] == "accelerate3d":
                    accelerate3d = conf[1].strip()
                elif conf[0] == "monitorcount":
                    monitorcount = conf[1].strip()
                elif conf[0] == "usbmode":
                    usbmodetmp = conf[1].strip()
                    if usbmodetmp in USB_MODES:
                        usbmode = usbmodetmp
                    else:
                        print ("Der Wert <%s> für usbmode ist nicht bekannt, moegliche Werte: %s" % (usbmodetmp, ", ".join(USB_MODES)))

        # Parameter setzen
        strmac = ""
        if macaddr != "":
            strmac = "--macaddress1 %s " % macaddr

        if network == "bridged":
            strexe = "VBoxManage --nologo modifyvm %s --nic1 %s --cableconnected1 on --bridgeadapter1 %s %s" % (vm, network, bridgeadapter, strmac)
            print(strexe)
            p = Popen(strexe, shell=True)
            p.wait()
        else:
            strexe = "VBoxManage --nologo modifyvm %s --nic1 %s --cableconnected1 on %s" % (vm, network, strmac)
            print(strexe)
            p = Popen(strexe, shell=True)
            p.wait()

        if usbmode != "off":
            strexe = ""
            if usbmode == "usb":
                strexe = "VBoxManage --nologo modifyvm %s --usb on" % (vm)
            else:
                strexe = "VBoxManage --nologo modifyvm %s --usb on --%s on" % (vm, usbmode)

            print(strexe)
            p = Popen(strexe, shell=True)
            p.wait()

        strexe = "VBoxManage --nologo modifyvm %s --accelerate2dvideo %s --accelerate3d %s --monitorcount %s" % (vm, accelerate2dvideo, accelerate3d, monitorcount)
        print(strexe)
        p = Popen(strexe, shell=True)
        p.wait()

    else:
        print("VM-Konfiguration wurde nicht gefunden.")