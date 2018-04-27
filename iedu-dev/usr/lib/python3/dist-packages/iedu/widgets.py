#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from iedu.config import *
from iedu.network import ieduNetworkHelper

class ieduListView(QListView):
    dropItems = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent):
        super(ieduListView, self).__init__(parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-qabstractitemmodeldatalist"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        bytearray = event.mimeData().data('application/x-qabstractitemmodeldatalist')
        data_items = self.decode_data(bytearray)
        self.dropItems.emit(data_items)

    def decode_data(self, bytearray):
        data = []

        ds = QDataStream(bytearray)
        while not ds.atEnd():

            item = {}
            row = ds.readInt32()
            column = ds.readInt32()

            map_items = ds.readInt32()
            for i in range(map_items):
                key = ds.readInt32()

                value = QVariant()
                ds >> value
                item[Qt.ItemDataRole(key)] = value

            data.append(item)

        return data

class ieduNICComboBoxDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.insertItem(cb.count(), QIcon(ieduConfig.create_media_path("gui-icons/nic.png")), "Keine", "")
        for interface, data in ieduNetworkHelper.get_net_interfaces().items():
            cb.insertItem(cb.count(), QIcon(ieduConfig.create_media_path("gui-icons/nic.png")), "%s (%s)" % (interface, data["ip"]), interface)

        return cb

    def setEditorData(self, editor, index):
        editor.setCurrentIndex(editor.findData(index.data()))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentData(), Qt.EditRole)