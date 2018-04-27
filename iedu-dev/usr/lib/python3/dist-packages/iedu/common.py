#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#
import subprocess

from subprocess import Popen, PIPE
from os.path import isdir, exists, isfile
from os import listdir

from iedu.config import *

class ieduCommonHelper():
    @staticmethod
    def run_cmd_stdout(command, argShell=False):
        p = Popen(command, stdout=PIPE, shell=argShell)
        ret = p.wait()
        return (ret, p.stdout.read().decode('UTF-8'))

    @staticmethod
    def run_cmd(command, argShell=False):
        try:
            return subprocess.call(command.split(" ") if argShell == False else command, shell=argShell)
        except:
            return False

    @staticmethod
    def availVMs():
        vms = []
        if exists(VM_ROOT):
            for item in listdir(VM_ROOT):
                if isdir(VM_ROOT + "/" + item):
                    vms += [item]

        return vms