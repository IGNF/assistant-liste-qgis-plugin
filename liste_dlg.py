import json
import os
from copy import deepcopy

from PyQt5.QtWidgets import QDialog, QMenu
from qgis.core import QgsProject

from .filtre import *
from .constantes import *

class DialogListe(QObject):
    def __init__(self,plugin_parent=None):
        super().__init__()
        # dictionnaire des layer contenu dans une liste
        self.dico_layer_id_from_liste = {}
        self.dialog = None
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
        self.dialog.tableView.setModel(self.model)
        self.dialog.tableView.resizeColumnsToContents()
        # colonne "layer" et "id"
        self.dialog.tableView.setColumnWidth(0, 100)
        self.dialog.tableView.setColumnWidth(1, 50)
        self.dialog.tableView.verticalHeader().setDefaultSectionSize(10)
        self.dialog.tableView.setSortingEnabled(True)


    def show_menu_supp(self, position):
        selection_model = self.dialog.tableView.selectionModel()
        select_ligne = {index.row() for index in selection_model.selectedRows()}  # set de lignes sélectionnées
        if not select_ligne:
            return  # aucune sélection

        nom_liste = self.parent.get_nom_list_sel()
        dico_entite_avant_supp = self.parent.get_dico_from_json(nom_liste)

        menu = QMenu()
        delete_action = menu.addAction("Supprimer ou les ligne(s)")
        action = menu.exec_(self.dialog.tableView.viewport().mapToGlobal(position))

        dico_entite_to_suppr = {}
        for ligne in select_ligne:
            id_layer = self.model.index(ligne, 0)
            layer_name = self.model.data(id_layer)
            id_index = self.model.index(ligne, 1)
            id_value = self.model.data(id_index)
            # créer la liste si la clé n'existe pas encore
            if layer_name not in dico_entite_to_suppr:
                dico_entite_to_suppr[layer_name] = []
            dico_entite_to_suppr[layer_name].append(int(id_value))

        dico_entite_apres_suppr = deepcopy(dico_entite_avant_supp)
        for layer_name,ids_to_suppr in dico_entite_to_suppr.items():
            if layer_name in dico_entite_apres_suppr:
                dico_entite_apres_suppr[layer_name] = [
                    item for item in dico_entite_apres_suppr[layer_name] if item not in ids_to_suppr]

        if action == delete_action:
            # réécriture du json avec le nouveau dictionnaire
            nom_liste = self.parent.get_nom_list_sel()
            fic_liste = os.path.join(DOSSIER_LISTE, f"{nom_liste}.json")
            with open(fic_liste, "w", encoding="utf-8") as f:
                json.dump(dico_entite_apres_suppr, f, indent=2, ensure_ascii=False)

            # suppression des lignes
            for row in sorted(select_ligne, reverse=True):
                self.model.removeRow(row)

            # si c'est la liste "selection" on deselectionne en plus
            # if nom_liste == NOM_LISTE_SELECTION:
            #     project = QgsProject.instance()
            #     layer = None
            #     for layer_name, ident in self.dico_layer_id_from_liste.items():
            #         layers = project.mapLayersByName(layer_name)
            #         layer = layers[0]
            #     layer.selectByIds([int(fid) for fid in ident])
            #     print(dico_entite_apres_suppr.values())

            # mise à jour du nombre d'entités dans le tablewidget parent
            self.parent.maj_nb_entites(nom_liste)
            self.dialog.label_nb_entite.setText(f"Nombre d'entités = {self.model.rowCount()}")

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
        print("get_sel_in_list")
        if not self.dialog:
            return
        project = QgsProject.instance()
        # vider le model avant insertion
        self.model.removeRows(0, self.model.rowCount())

        # precision : le range commence à 2 et non à 0, car on a ajouté une colonne "layer" et "id" en premiere colonne
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

            self.dialog.label_nb_entite.setText(f"Nombre d'entités = {self.model.rowCount()}")

    def open_table_attribut(self):
        selection_model = self.dialog.tableView.selectionModel()
        # récupérer les indexes sélectionnés
        selected_indexes = selection_model.selectedRows()
        for index in selected_indexes:
            ligne = index.row()
            # 1ere colonne des lignes sélectionnées --> "layer"
            layer = self.model.item(ligne, 0).text()
            # 2ieme colonne des lignes sélectionnées --> "id"
            ident = self.model.item(ligne,1).text()
            # si le layer n'est pas encore dans le dictionnaire, on crée une entrée vide
            if layer not in self.dico_layer_id_from_liste:
                self.dico_layer_id_from_liste[layer] = []

            self.dico_layer_id_from_liste[layer].append(ident)

        # on commence par tout deselectionner
        self.parent.deselectionne_all()

        # pour chaque layer du dico on sélectionne les entites
        # puis on ouvre la table attributaire de selection
        project = QgsProject.instance()
        layer = None
        for layer_name,ident in self.dico_layer_id_from_liste.items():
            layers = project.mapLayersByName(layer_name)
            layer = layers[0]
            # transformation des id en entier
            layer.selectByIds([int(fid) for fid in ident])
            self.parent.iface.showAttributeTable(layer)

        # IMPORTANT : le zomm ne se fait que sur les objet du dernier layer trouvé
        self.parent.iface.setActiveLayer(layer)
        self.parent.iface.actionZoomToSelected().trigger()

    def show_filtre(self):
        print("show_filtre")
        self.filtre = DialogFiltre(self)
        self.filtre.open_dialog()

        colonne_filtre = self.filtre.get_checked_columns()

        # on masque les entêtes des colonnes qui sont dans le filtre
        for col in range(self.model.columnCount()):
            entete_colonne = self.model.headerData(col, Qt.Horizontal)
            if entete_colonne in colonne_filtre:
                self.dialog.tableView.hideColumn(col)
            else:
                self.dialog.tableView.showColumn(col)

    def open_liste(self):
        self.dialog = QDialog()
        loadUi(os.path.join(os.path.dirname(__file__), "liste.ui"), self.dialog)
        self.dialog.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # slot
        self.dialog.pushButtonOpenTableAttribut.clicked.connect(self.open_table_attribut)
        self.dialog.pushButtonHide.clicked.connect(self.show_filtre)

        # menu contextuel
        self.dialog.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dialog.tableView.customContextMenuRequested.connect(self.show_menu_supp)

        # gestion d'ouverture de plusieurs dialog liste
        self.dialogs_liste.append(self.dialog)
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.dialog.destroyed.connect(lambda _, dlg = self.dialog:self.dialogs_liste.remove(dlg))
        self.dialog.setWindowTitle(self.parent.get_nom_list_sel())

        # recuperation des données de la liste sélectionnée
        nom_liste = self.parent.get_nom_list_sel()
        self.dico_json = self.parent.get_dico_from_json(nom_liste)

        # initialisation du tableview (creation des colonnes en fonction des champs des layers du json)
        self.init_tableview()

        self.get_sel_in_list()
        self.dialog.show()