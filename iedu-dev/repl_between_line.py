#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

# Replaces all content in file between begin and end

import sys
import os.path
import re

file = sys.argv[1]
begin = sys.argv[2]
end = sys.argv[3]

if os.path.isfile(file):
    fp = open(file)
    lines = ''.join(fp.readlines())
    fp.close()
    nl = re.sub(r"%s.*%s" % (begin, end), "", lines, flags=re.DOTALL)
    fw = open(file, 'w')
    fw.write(nl)
    fw.close()

else:
    print("File %s does not exist" % file)