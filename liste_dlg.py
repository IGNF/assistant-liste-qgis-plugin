import os

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from qgis.core import QgsProject

class DialogListe(QObject):
    def __init__(self,plugin_parent=None):
        super().__init__()
        self.dlg_liste = None
        self.dlg_attr = None
        self.dico_json = None
        self.model = None
        self.dialogs_liste = []
        self.parent = plugin_parent

    def init_tableview(self,dlg):
        layers,champs = self.get_structure_layer()
        champs = ["Layer"] + list(champs)
        self.model = QStandardItemModel()
        self.model.setColumnCount(len(champs))

        self.model.setHorizontalHeaderLabels(champs)
        dlg.tableView.setModel(self.model)
        dlg.tableView.resizeColumnsToContents()
        dlg.tableView.setColumnWidth(0, 100)
        dlg.tableView.verticalHeader().setDefaultSectionSize(10)

    def get_structure_layer(self):
        liste_champ = set()
        layer_name = []
        for layer_name in self.dico_json.keys():
            project = QgsProject.instance()
            layer = project.mapLayersByName(layer_name)
            layer = layer[0]

            for field in layer.fields():  # fields() retourne un QgsFields
                # print(f"{layer_name} : {field.name()}")
                liste_champ.add(field.name())
        return layer_name,liste_champ

    def get_sel_in_list(self):
        project = QgsProject.instance()
        # vider le model avant insertion
        self.model.removeRows(0, self.model.rowCount())

        # precision : le range commence à 1 et non à 0, car on a ajouté une colonne "layer" en premiere colonne
        champs_entete = [
            self.model.headerData(col, Qt.Horizontal)
            for col in range(1,self.model.columnCount())
        ]
        # parcourir les entités
        for layer_name, ids_sel in self.dico_json.items():
            layers = project.mapLayersByName(layer_name)
            if not layers:
                continue

            layer = layers[0]

            for ident in ids_sel:
                feature = layer.getFeature(ident)
                if not feature.isValid():
                    continue
                row_items = []
                item = QStandardItem(layer_name)
                row_items.append(item)
                for champ in champs_entete:
                    if feature.fields().indexOf(champ) != -1:
                        valeur = feature.attribute(champ)
                        item = QStandardItem("" if valeur is None else str(valeur))
                    else:
                        item = QStandardItem("")
                    row_items.append(item)
                # 🔥 ajout de la ligne complète
                self.model.appendRow(row_items)

            self.dlg_liste.label_nb_entite.setText(f"Nombre d'entités = {self.model.rowCount()}")

    def open_liste(self):
        self.dlg_liste = QDialog()
        loadUi(os.path.join(os.path.dirname(__file__), "liste.ui"), self.dlg_liste)
        self.dlg_liste.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # gestion d'ouverture de plusieurs dialog liste
        self.dialogs_liste.append(self.dlg_liste)
        self.dlg_liste.setAttribute(Qt.WA_DeleteOnClose)
        self.dlg_liste.destroyed.connect(lambda: self.dialogs_liste.remove(self.dlg_liste))

        self.dlg_liste.setWindowTitle(self.parent.get_nom_list_sel())

        # recuperation des données de la liste sélectionnée
        nom_liste = self.parent.get_nom_list_sel()
        self.dico_json = self.parent.get_dico_from_json(nom_liste)

        # initialisation du tableview (creation des colonnes en fonction des champs des layers du json)
        self.init_tableview(self.dlg_liste)

        self.get_sel_in_list()
        self.dlg_liste.show()