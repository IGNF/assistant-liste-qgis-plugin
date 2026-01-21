import os

from PyQt5.QtCore import Qt, QObject, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from qgis.core import QgsProject

from .filtre import *

class DialogListe(QObject):
    def __init__(self,plugin_parent=None):
        super().__init__()
        self.dlg_liste = None
        self.dlg_attr = None
        self.dico_json = None
        self.model = None
        self.dialogs_liste = []
        self.parent = plugin_parent

    def init_tableview(self):
        layers,champs = self.get_structure_layer()
        champs = ["Layer","id"] + list(champs)
        self.model = QStandardItemModel()
        self.model.setColumnCount(len(champs))

        self.model.setHorizontalHeaderLabels(champs)
        self.dlg_liste.tableView.setModel(self.model)
        self.dlg_liste.tableView.resizeColumnsToContents()
        # colonne "layer" et "id"
        self.dlg_liste.tableView.setColumnWidth(0, 100)
        self.dlg_liste.tableView.setColumnWidth(1, 50)
        self.dlg_liste.tableView.verticalHeader().setDefaultSectionSize(10)
        self.dlg_liste.tableView.setSortingEnabled(True)

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

        # precision : le range commence à  et non à 0, car on a ajouté une colonne "layer" et "id" en premiere colonne
        champs_entete = [
            self.model.headerData(col, Qt.Horizontal)
            for col in range(2,self.model.columnCount())
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
                item = QStandardItem(str(ident))
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

    def open_table_attribut(self):
        dico_layer_id = {}
        selection_model = self.dlg_liste.tableView.selectionModel()
        # récupérer les indexes sélectionnés
        selected_indexes = selection_model.selectedRows()
        for index in selected_indexes:
            ligne = index.row()
            # 1ere colonne des lignes sélectionnées --> "layer"
            layer = self.model.item(ligne, 0).text()
            # 2ieme colonne des lignes sélectionnées --> "id"
            ident = self.model.item(ligne,1).text()
            # si le layer n'est pas encore dans le dictionnaire, on crée une entrée vide
            if layer not in dico_layer_id:
                dico_layer_id[layer] = []

            dico_layer_id[layer].append(ident)

        # on commence par tout deselectionner
        self.parent.deselectionne_all()

        # pour chaque layer du dico on sélectionne les entites
        # puis on ouvre la table attributaire de selection
        project = QgsProject.instance()
        layer = None
        for layer_name,ident in dico_layer_id.items():
            layers = project.mapLayersByName(layer_name)
            layer = layers[0]
            # transformation des id en entier
            layer.selectByIds([int(fid) for fid in ident])
            self.parent.iface.showAttributeTable(layer)

        # IMPORTANT : le zomm ne se fait que sur les objet du dernier layer trouvé
        self.parent.iface.setActiveLayer(layer)
        self.parent.iface.actionZoomToSelected().trigger()

    def hide_colonne(self):
        # self.dlg_liste.tableView.hideColumn(1)
        self.filtre = DialogFiltre(self)
        self.filtre.open_dialog()

        colonne_filtre = self.filtre.get_checked_columns()

        # on masque les entêtes des colonnes qui sont dans le filtre
        for col in range(self.model.columnCount()):
            entete_colonne = self.model.headerData(col, Qt.Horizontal)
            if entete_colonne in colonne_filtre:
                self.dlg_liste.tableView.hideColumn(col)
            else:
                self.dlg_liste.tableView.showColumn(col)

    def open_liste(self):
        self.dlg_liste = QDialog()
        loadUi(os.path.join(os.path.dirname(__file__), "liste.ui"), self.dlg_liste)
        self.dlg_liste.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # slot
        self.dlg_liste.pushButtonOpenTableAttribut.clicked.connect(self.open_table_attribut)
        self.dlg_liste.pushButtonHide.clicked.connect(self.hide_colonne)

        # gestion d'ouverture de plusieurs dialog liste
        self.dialogs_liste.append(self.dlg_liste)
        self.dlg_liste.setAttribute(Qt.WA_DeleteOnClose)
        self.dlg_liste.destroyed.connect(lambda _, dlg = self.dlg_liste:self.dialogs_liste.remove(dlg))
        self.dlg_liste.setWindowTitle(self.parent.get_nom_list_sel())

        # recuperation des données de la liste sélectionnée
        nom_liste = self.parent.get_nom_list_sel()
        self.dico_json = self.parent.get_dico_from_json(nom_liste)

        # initialisation du tableview (creation des colonnes en fonction des champs des layers du json)
        self.init_tableview()

        self.get_sel_in_list()
        self.dlg_liste.show()