#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

import os
import sys
import configparser

from os.path import isdir, basename, exists, isfile

DEV_D = False
base_path_usr = "/usr/share/iedu-server/"
base_path_etc = "/etc/iedu-server/"
if "IEDU_DEV" in os.environ and os.environ["IEDU_DEV"] == "1":
    base_path_usr = "usr/share/iedu-server/"
    base_path_etc = "etc/iedu-server/"
    DEV_D = True

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

class ieduConfig:

    @staticmethod
    def create_media_path(file):
        return base_path_usr + file