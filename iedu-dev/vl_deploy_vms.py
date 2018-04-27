#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import sys
import socket
import subprocess
import re
import requests
import configparser
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from os import listdir
from os.path import isdir, exists, isfile
from paramiko import *
from sys import argv
import paramiko
import logging
import urllib3

# Globale Variablen
DEV_D = False
base_path_etc = "/etc/iedu-server/"
if(len(argv) > 1 and argv[1] == "dev"):
    base_path_etc = "etc/iedu-server/"
    DEV_D = True

VERSION = "0.5.3"
TITLE = "i-EDU deployment tool " + VERSION
CONFIG_FILE = base_path_etc + "config"

if not exists(CONFIG_FILE):
    print("Konfigurationsdatei (%s) wurde nicht gefunden!" % CONFIG_FILE)
    sys.exit(0)

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

CHECK_INTERNET_IP = config.get("MAIN", "CHECK_INTERNET_IP")
VM_ROOT = config.get("MAIN", "VM_ROOT")
FOREMAN_HOST = config.get("FOREMAN", "FOREMAN_HOST")
FOREMAN_USER = config.get("FOREMAN", "FOREMAN_USER")
FOREMAN_PASS = config.get("FOREMAN", "FOREMAN_PASS")

logging.getLogger("paramiko").setLevel(logging.INFO)
urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    CONSOLE_ROWS, CONSOLE_COLS = subprocess.check_output(['stty', 'size']).split()
except:
    CONSOLE_ROWS = 40
    CONSOLE_COLS = 100

GUI_WIN_WIDTH = 100 if int(CONSOLE_COLS) > 110 else (int(CONSOLE_COLS) - 10)

class Logger:
    def __init__(self):
        self.f = fr = open("proxmox_install.log", "w+")

    def log(self, text):
        self.f.write(text)

    def close(self):
        self.f.close()

#logger = Logger()

# Befehle ausführen
def run_cmd(command, argShell=False):
    try:
        return subprocess.call(command.split(" ") if argShell == False else command, shell=argShell)
    except:
        e = sys.exc_info()[0]
        retval = gui_yesno_box("Fehler", "Befehl <%s> war nicht erfolgreich, Fehlermeldung: %s -- Installation abbrechen?" % (command, e))
        if retval[0] == 1:
            exit(1)

def run_cmd_output(command, argShell=False):
    p = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=argShell)
    ret = p.wait()
    return (ret, p.stdout.read(), p.stderr.read())

def run_cmd_stdout(command, argShell=False):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=argShell)
    ret = p.wait()
    return (ret, p.stdout.read())

def run_cmd_stderr(command, argShell=False):
    p = subprocess.Popen(command, stderr=subprocess.PIPE, shell=argShell)
    ret = p.wait()
    return (ret, p.stderr.read().decode('UTF-8'))

def run_cmd_stdin(command, argShell=False):
    p = subprocess.Popen(command, stdin=subprocess.PIPE, shell=argShell)
    return p

# Oberflächen / GUI
def gui_message_box(title, text):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--msgbox", text, "--title", title, "8", str(GUI_WIN_WIDTH)])

def gui_text_box(file):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--textbox", file, "20", str(GUI_WIN_WIDTH)])

def gui_input_box(title, text, default=""):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--inputbox", text, "8", str(GUI_WIN_WIDTH), default, "--title", title])

def gui_yesno_box(title, text):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--yesno", text, "--title", title, "8", str(GUI_WIN_WIDTH)])

def gui_password_box(title, text):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--passwordbox", text, "8", str(GUI_WIN_WIDTH), "--title", title])

def gui_menu_box(title, text, menu):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--menu", text, "--title", title, "24", str(GUI_WIN_WIDTH), "16"] + menu)

def gui_checklist_box(title, text, checklist):
    ret = run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--checklist", text, "--title", title, "24", str(GUI_WIN_WIDTH), "14"] + checklist)
    return (ret[0], [] if ret[1] == "" else [x.replace('"', "") for x in ret[1].split(" ")])

def gui_radiolist_box(title, text, radiolist):
    return run_cmd_stderr(["whiptail", "--backtitle", TITLE, "--radiolist", text, "--title", title, "24", str(GUI_WIN_WIDTH), "14"] + radiolist)

class gui_progress_box():
    def __init__(self, text, progress):
        self.p = run_cmd_stdin(["whiptail", "--backtitle", TITLE, "--gauge", text, "6", "50", str(progress)])

    def update(self, prog):
        self.p.stdin.write(str(prog) + "\n")

    def finish(self):
        self.p.stdin.close()

def gui_password_verify_box(title, text, text2):
    password = ""
    while password == "":
        retval = gui_password_box(title, text)
        if retval[1] == "":
            continue

        retval2 = gui_password_box(title, text2)
        if retval2[1] == "":
            continue

        if retval[1] == retval2[1]:
            password = retval[1]
        else:
            gui_message_box(title, "Fehler bei der Passworteingabe, die Passwoerter stimmen nicht ueberein!")

    return password

# Sonstige Funktionen
def check_internet():
    try:
        s = socket.create_connection((CHECK_INTERNET_IP, 80), 5)
        return True
    except:
        return False

def check_filesystem():
    try:
        zfsc = run_cmd_output('zfs list')
        if zfsc[2].find('no datasets') != -1:
            return 'standard'
        else:
            return 'zfs'
    except:
        return 'standard'

def check_systemip(show_prefix = True):
    zfsc = run_cmd_stdout("ip addr show vmbr0 | grep 'inet' | grep -v 'inet6' | cut -d' ' -f6", argShell=True)
    if show_prefix == True:
        return zfsc[1].strip()
    else:
        return zfsc[1].strip().split("/")[0]

def get_net_interfaces():
    nets = run_cmd_stdout("ip addr", argShell=True)
    foundeth = False
    cureth = ""
    eths = {}
    for line in nets[1].decode('UTF-8').split("\n"):
        l = line.strip()
        m = re.search("^[0-9]: (.*): .*", l)
        if m != None:
            foundeth = True
            cureth = m.group(1)
            eths[cureth] = {}
            eths[cureth]["ip"] = ""

        if foundeth == True:
            m2 = re.search("^inet (.*)/.*", l)
            if m2 != None:
                eths[cureth]["ip"] = m2.group(1)
                foundeth = False
                cureth = ""

    return eths


def check_systemipnet():
    try:
        zfsc = check_systemip()
        if zfsc == '':
            return ''
        else:
            # Nicht immer true
            ipf = zfsc.split(".")
            return "%s.%s.%s.0/%s" % (ipf[0], ipf[1], ipf[2], ipf[3].split("/")[1])
    except:
        return ''

def file_replace_line(file, findstr, replstr):
    fp = open(file, "r+")
    buf = ""
    for line in fp.readlines():
        if line.find(findstr) != -1:
            line = replstr + "\n"

        buf += line

    fp.close()
    fr = open(file, "w+")
    fr.write(buf)
    fr.close()

def file_create(file, str):
    fr = open(file, "w+")
    fr.write(str + "\n")
    fr.close()

def file_append(file, str):
    fr = open(file, "a")
    fr.write(str + "\n")
    fr.close()

# Installer Start
class Installer():
    def __init__(self):
        self.internet = False
        self.fqdn = socket.getfqdn()
        try:
            self.domain = self.fqdn.split(".")[1] + "." + self.fqdn.split(".")[2]
            self.hostname = socket.gethostname()
        except:
            self.domain = ""
            self.hostname = socket.gethostname()

        # User setting
        self.net_interface = {"int": "", "ip": ""}
        self.client_group = ""
        self.clients = []
        self.vm_imports = []
        self.config_imports = ["init.sh", "exec.sh"]
        self.data_types = {
            "all": "VM-Dateien und Konfigurationen",
            "config": "Nur Konfigurationen"
        }
        self.data_type = "all"

        # Data
        self.avail_VMs = []
        self.avail_clients = {}
        self.avail_configs = ["init.sh", "exec.sh"]

        if exists(VM_ROOT):
            for item in listdir(VM_ROOT):
                if isdir(VM_ROOT + "/" + item):
                    self.avail_VMs += [item]

    def start(self):
        gui_message_box("Installer", "Willkommen beim i-EDU deployment tool!")
        self.internet = check_internet()
        self.step1()

    def step1(self):
        step1_val = gui_menu_box("Schritt 1", "Kontrollieren bzw. konfigurieren Sie die entsprechenden Werte und gehen Sie dann auf 'Weiter'.",
                                    ["Internet", "JA" if self.internet == True else "NEIN",
                                     "Hostname", self.hostname,
                                     "Domain", self.domain,
                                     " ", " ",
                                     "Netzwerkschnittstelle", "Keine" if self.net_interface["int"] == "" else self.net_interface["int"] + " (" + self.net_interface["ip"] + ")",
                                     "Clientgruppe", self.client_group,
                                     "Clients", "%s Clients gewaehlt" % len(self.clients) if len(self.clients) > 0 else "Keine",
                                     "VMs", ",".join(self.vm_imports) if len(self.vm_imports) > 0 else "Keine",
                                     "Configs", ",".join(self.config_imports) if len(self.config_imports) > 0 else "Keine",
                                     " ", " ",
                                     "Datentyp", self.data_type,
                                     " ", " ",
                                     "Weiter", "Verteilung starten"])

        # Abbrechen
        if step1_val[0] == 1 or step1_val[0] == 255:
            exit(0)

        # Eintrag wurde gewählt
        if step1_val[1] == "Netzwerkschnittstelle":
            self.step1_net_interface()

        elif step1_val[1] == "Clientgruppe":
            self.step1_client_group()

        elif step1_val[1] == "Clients":
            self.step1_clients()

        elif step1_val[1] == "Internet":
            check_internet()
            self.step1()

        elif step1_val[1] == "VMs":
            self.step1_vms()

        elif step1_val[1] == "Configs":
            self.step1_configs()

        elif step1_val[1] == "Datentyp":
            self.step1_data_type()

        elif step1_val[1] == "Weiter":
            self.step2()

        else:
            self.step1()

    def step1_data_type(self):
        list = []
        for key, val in self.data_types.items():
            list += [key, val, "ON" if self.data_type == key else "OFF"]

        retval = gui_radiolist_box("Schritt 1: Datentyp", "Waehlen sie den gewuenschten Datentyp zum Transfer", list)
        # Abbrechen
        if retval[0] == 1 or retval[0] == 255:
            self.step1()
            return

        self.data_type = retval[1]
        self.step1()

    def step1_net_interface(self):
        list = []
        eths = get_net_interfaces()
        for key, val in eths.items():
            list += [key, val["ip"] if "ip" in val else "", "ON" if self.net_interface["int"] == key else "OFF"]

        retval = gui_radiolist_box("Schritt 1: Netzwerkschnittstelle", "Waehlen sie die Netzwerkschnittstelle fuer udpcast", list)
        # Abbrechen
        if retval[0] == 1 or retval[0] == 255:
            self.step1()
            return

        self.net_interface["int"] = retval[1]
        self.net_interface["ip"] = eths[retval[1]]["ip"]
        self.step1()

    def step1_client_group(self):
        list = []
        response = requests.get("https://%s/api/hostgroups" % FOREMAN_HOST, verify=False, auth=(FOREMAN_USER, FOREMAN_PASS))
        for hostgroup in response.json()["results"]:
            list += [hostgroup["name"] if hostgroup["parent_name"] == None else hostgroup["parent_name"] + "/" + hostgroup["name"], hostgroup["subnet_name"] if hostgroup["subnet_name"] != None else "", "ON" if self.client_group == hostgroup["name"] else "OFF"]

        retval = gui_radiolist_box("Schritt 1: Clientgruppe", "Waehlen sie die Clientgruppe", list)
        # Abbrechen
        if retval[0] == 1 or retval[0] == 255:
            self.step1()
            return

        self.client_group = retval[1]
        self.step1()

    def step1_clients(self):
        list = []
        response = requests.get("https://%s/api/hosts" % (FOREMAN_HOST), verify=False, auth=(FOREMAN_USER, FOREMAN_PASS), data={"hostgroup_id": self.client_group, "per_page": 100})
        self.avail_clients = response.json()["results"]
        list += ["Alle", "Alle Clients auswaehlen", "OFF"]
        for clients in self.avail_clients:
            list += [clients["ip"], clients["name"], "ON" if clients["ip"] in self.clients else "OFF"]

        retval = gui_checklist_box("Schritt 1: VM-Template-Import", "Waehlen sie die Clients fuer den udpcast Transfer", list)
        # Abbrechen
        if retval[0] == 1 or retval[0] == 255:
            self.step1()
            return

        self.clients = []
        sall = False
        for val in retval[1]:
            if val == "Alle":
                sall = True
            self.clients += [val]

        if sall == True:
            self.clients.clear()
            for clients in self.avail_clients:
                self.clients += [clients["ip"]]

        self.step1()

    def step1_vms(self):
        list = []
        list += ["Alle", "Alle VMs auswaehlen", "OFF"]
        for vm in self.avail_VMs:
            list += [vm, "VM", "ON" if vm in self.vm_imports else "OFF"]

        retval = gui_checklist_box("Schritt 1: VM-Auswahl", "Waehlen sie die VMs fuer den udpcast Transfer", list)
        # Abbrechen
        if retval[0] == 1 or retval[0] == 255:
            self.step1()
            return

        self.vm_imports = []
        sall = False
        for val in retval[1]:
            if val == "Alle":
                sall = True
            self.vm_imports += [val]

        if sall == True:
            self.vm_imports.clear()
            for vm in self.avail_VMs:
                self.vm_imports += [vm]

        self.step1()

    def step1_configs(self):
        list = []
        list += ["Alle", "Alle Configs auswaehlen", "OFF"]
        for config in self.avail_configs:
            list += [config, "Config", "ON" if config in self.config_imports else "OFF"]

        retval = gui_checklist_box("Schritt 1: Config-Auswahl", "Waehlen sie die Configs fuer den udpcast Transfer", list)
        # Abbrechen
        if retval[0] == 1 or retval[0] == 255:
            self.step1()
            return

        self.config_imports = []
        sall = False
        for val in retval[1]:
            if val == "Alle":
                sall = True
            self.config_imports += [val]

        if sall == True:
            self.config_imports.clear()
            for config in self.avail_configs:
                self.config_imports += [config]

        self.step1()

    def step2(self):
        if self.net_interface["int"] == "":
            gui_message_box("Installer", "Sie muessen ein Netzwerkinterface auswaehlen!")
            self.step1()
            return

        if len(self.clients) == 0:
            gui_message_box("Installer", "Sie muessen einen Client auswaehlen!")
            self.step1()
            return

        if len(self.vm_imports) == 0:
            gui_message_box("Installer", "Sie muessen eine VM zum verteilen auswaehlen!")
            self.step1()
            return

        # Generate udpcastlist
        if self.data_type == "all":

            for cclient in self.clients:
                print("Starte udpcast für Client %s" % cclient)

                try:
                    client = SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(cclient, username="root", port=22)
                    stdin, stdout, stderr = client.exec_command('killall vludpreceiveVMs udp-receiver; exec vludpreceiveVMs >/tmp/udpcast.log 2>&1')
                    client.close()
                    print("OK")
                except Exception as inst:
                    print("Fehler::", inst)

            f = open("/vm/udpcastlist", "w+")
            for vm_import in self.vm_imports:
                if exists(VM_ROOT + vm_import):
                    for item in listdir(VM_ROOT + vm_import):
                        if isfile(VM_ROOT + vm_import + "/" + item):
                            if item.endswith("sh") or item.endswith("vdi"):
                                if item.endswith("sh") and item not in self.config_imports:
                                    continue

                                f.write("vb/%s/%s\n" % (vm_import, item))

            f.close()

            run_cmd("cd /vm; tar -cv udpcastlist `cat udpcastlist` | udp-sender --interface %s" % self.net_interface["int"], argShell=True)

        elif self.data_type == "config":

            for cclient in self.clients:
                print("Starte Configverteilung für Client %s" % cclient)

                try:
                    client = SSHClient()
                    client.load_system_host_keys()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.connect(cclient, username="root", port=22)
                    csftp = client.open_sftp()

                    for vm_import in self.vm_imports:
                        if exists(VM_ROOT + vm_import):
                            for item in listdir(VM_ROOT + vm_import):
                                if isfile(VM_ROOT + vm_import + "/" + item):
                                    if item.endswith("sh"):
                                        if item not in self.config_imports:
                                            continue

                                        filestr = VM_ROOT + vm_import + "/" + item
                                        csftp.put(filestr, filestr)
                                        client.exec_command('chown student:student ' + filestr)
                                        client.exec_command('chmod +x ' + filestr)

                    client.exec_command('/opt/puppetlabs/bin/puppet agent --test > /tmp/puppetrundeploy')

                    client.close()
                    print("OK")
                except Exception as inst:
                    print("Fehler::", inst)


i = Installer()
i.start()
#logger.close()