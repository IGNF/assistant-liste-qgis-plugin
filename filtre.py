import os

from qgis.PyQt.QtCore import Qt, QObject
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.uic import loadUi

from .mapping_version import *


class DialogFiltre(QObject):
    def __init__(self,parent=None):
        super().__init__()
        self.parent = parent
        self.dlg_filtre = None
        self.model = None
        self.all_is_checked = False

    def ini_list_view(self):
        # je check ou pas les colonnes en fct des colonnes masquées du dialog (donc apes filtre)
        entete_colonne = []
        for col in range(self.parent.model.columnCount()):
            if not self.parent.dialog.tableView.isColumnHidden(col):
                entete_colonne.append(self.parent.model.headerData(col, Horizontal))

        layer,champs = self.parent.get_structure_layer()
        self.model = QStandardItemModel()
        for champ in champs:
            item = QStandardItem(champ)
            item.setCheckable(True)
            item.setEditable(False)
            if champ in entete_colonne:
                item.setCheckState(Checked)
            self.model.appendRow(item)
        self.dlg_filtre.listView.setModel(self.model)

    def sel_all_colonnes(self):
        etat = Checked if not self.all_is_checked else Unchecked
        # if etat == Checked:
        #     self.dlg_filtre.pushButton_sel_all.setText("Rien")
        # else:
        #     self.dlg_filtre.pushButton_sel_all.setText("Tout")

        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            item.setCheckState(etat)

        self.all_is_checked = not self.all_is_checked
        self.dlg_filtre.pushButton_sel_all.setText("Rien" if self.all_is_checked else "Tout")

    def get_checked_columns(self):
        """Retourne la liste des colonnes cochées"""
        list_checked = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.checkState() == Unchecked:
                list_checked.append(item.text())
        self.dlg_filtre.close()
        return list_checked


    def open_dialog(self,parent = None):
        self.dlg_filtre = QDialog(parent)
        loadUi(os.path.join(os.path.dirname(__file__), "filtre.ui"), self.dlg_filtre)
        self.dlg_filtre.setWindowFlags(WindowCloseButtonHint | WindowStaysOnTopHint)
        self.dlg_filtre.setWindowTitle("Filtrer les colonnes visibles")

        self.dlg_filtre.pushButton_sel_all.setText("Rien")

        # slot
        self.all_is_checked = True
        self.dlg_filtre.pushButton_sel_all.clicked.connect(self.sel_all_colonnes)
        self.dlg_filtre.pushButton_appliquer.clicked.connect(self.get_checked_columns)

        self.ini_list_view()

        self.dlg_filtre.exec()

