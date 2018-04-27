#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import sys
import subprocess
import json
import re

dev = sys.argv[1]
devs = dev.split("/")
devname = devs[len(devs)-1]

print("automount_usb2vb für Gerät %s" % devname)

m = re.search("^([a-z]*)[1-9]{1,3}", devname)
if m != None:
    devname = m.group(1)
    print("Root-Device ist nun %s" % devname)

runningvm = ""
p = subprocess.Popen("VBoxManage list runningvms", stdout=subprocess.PIPE, shell=True)
p.wait()
outvboxrun = p.stdout.read().decode('UTF-8')
m = re.search("^\"([^ ]*)\" .*", outvboxrun)
if m != None:
    runningvm = m.group(1)
else:
    print("Keine laufende VM gefunden")
    sys.exit(0)

print(runningvm)

p = subprocess.Popen("lsblk -J -o name,serial,model", stdout=subprocess.PIPE, shell=True)
p.wait()
lsblkjson = p.stdout.read().decode('UTF-8')
lsblk = json.loads(lsblkjson)
usbserial = ""
for blkdev in lsblk["blockdevices"]:
    if blkdev["name"] == devname:
        usbserial = blkdev["serial"]
        break

if usbserial == "":
    print("Seriennummer für USB-Gerät nicht gefunden")
    sys.exit(0)

p = subprocess.Popen("VBoxManage list usbhost", stdout=subprocess.PIPE, shell=True)
p.wait()
outVboxUSBList = p.stdout.readlines()
curUUID = ""
for line in outVboxUSBList:
    line = line.strip().decode('UTF-8')

    if curUUID != "":
        if line.startswith('SerialNumber:'):
            m = re.search("SerialNumber:[ ]+(.+)$", line)
            if m != None:
                vbserial = m.group(1)
                if vbserial == usbserial:
                    break

    if line.startswith('UUID:'):
        m = re.search("UUID:[ ]+([0-9a-z\-]+)$",line)
        if m != None:
            curUUID = m.group(1)

    if line.startswith("Current State:"):
        curUUID = ""

if curUUID == "":
    print("Virtuablox USB-UUID wurde nicht gefunden für Serial %s" % usbserial)
    sys.exit(0)

vbusbexe = "VBoxManage controlvm %s usbattach %s" % (runningvm, curUUID)
p = subprocess.Popen(vbusbexe, stdout=subprocess.PIPE, shell=True)
p.wait()

print(vbusbexe)