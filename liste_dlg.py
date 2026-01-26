import json
import os
from copy import deepcopy

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QMenu
from qgis.core import QgsProject

from .filtre import *
from .constantes import *
from .liste_model import ListeModel


class DialogListe(QObject):
    drag_started = pyqtSignal(object, list)
    def __init__(self,plugin_parent=None):
        super().__init__()
        # dictionnaire des layer contenu dans une liste
        self.nom_liste = None
        self.dico_layer_id_from_liste = {}
        self.dialog = None
        self.dlg_attr = None
        self.dico_json = None
        self.model = None
        self.dialogs_liste = []
        self.parent = plugin_parent

    def start_drag(self):
        selection = self.get_selected_entites()  # [{"layer":..., "id":...}, ...]
        self.drag_started.emit(self, selection)

    def init_tableview(self):
        layers,champs = self.get_structure_layer()
        champs = ["Layer","id"] + list(champs)

        # on passe par la class derivée pour gerer le drag&drop
        # self.model = QStandardItemModel()
        self.model = ListeModel()
        self.model.dlg = self

        # evenement d'ajout - supprssion dans le model
        self.model.rowsInserted.connect(self.update_label_nb_entite)
        self.model.rowsRemoved.connect(self.update_label_nb_entite)

        self.model.setColumnCount(len(champs))

        self.model.setHorizontalHeaderLabels(champs)
        self.dialog.tableView.setModel(self.model)
        self.dialog.tableView.resizeColumnsToContents()
        # colonne "Layer" et "id"
        self.dialog.tableView.setColumnWidth(0, 100)
        self.dialog.tableView.setColumnWidth(1, 50)
        self.dialog.tableView.verticalHeader().setDefaultSectionSize(10)
        self.dialog.tableView.setSortingEnabled(True)

    def update_label_nb_entite(self):
        if getattr(self, "dialog", None) and hasattr(self.dialog, "label_nb_entite"):
            try:
                self.dialog.label_nb_entite.setText(f"Nombre d'entités = {self.model.rowCount()}")
            except RuntimeError:
                pass

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
        # selected_indexes = selection_model.selectedRows()
        # for index in selected_indexes:
        for ligne in range(self.model.rowCount()):
            # ligne = index.row()
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

    # entites : liste de dico des champs
    def remove_ligne(self, entites = None):
        print("remove_ligne")
        # Charger le JSON existant
        fichier_json = os.path.join(DOSSIER_LISTE, f"{self.nom_liste}.json")
        if os.path.exists(fichier_json):
            with open(fichier_json, "r", encoding="utf-8") as f:
                dico_json = json.load(f)
        else:
            dico_json = {}

        # ============================
        # Si aucune entité n'est passée, supprimer les lignes sélectionnées
        if entites is None:
            entites = []
            selection_model = self.dialog.tableView.selectionModel()
            for index in selection_model.selectedRows():
                ligne = index.row()
                layer = self.model.item(ligne, 0).text()
                ident = int(self.model.item(ligne, 1).text())
                entites.append({"Layer": layer, "id": ident})

        for ligne in reversed(range(self.model.rowCount())):
            row_layer = self.model.item(ligne, 0).text()
            row_id = int(self.model.item(ligne, 1).text())

            for e in entites:
                e_layer = str(e.get("Layer") or e.get("layer") or "")
                if e_layer == row_layer and int(e.get("id", 0)) == row_id:
                    print(e.get("id", 0))
                    self.model.removeRow(ligne)
                    # 🔹 mettre à jour le JSON
                    if row_layer in dico_json and row_id in dico_json[row_layer]:
                        dico_json[row_layer].remove(row_id)
                        if not dico_json[row_layer]:
                            del dico_json[row_layer]
                    break
        self.dialog.tableView.viewport().update()
        # self.dialog.tableView.reset()
        print("nombre de ligne = ",self.model.rowCount())
        # ============================



        # headers = [self.model.headerData(col, Qt.Horizontal) for col in range(self.model.columnCount())]
        # for ligne in reversed(range(self.model.rowCount())):
        #     # construire un dict pour la ligne actuelle
        #     row_data = {headers[col]: self.model.item(ligne, col).text() for col in range(self.model.columnCount())}
        #     for e in entites:
        #         # comparer toutes les colonnes
        #         if all(str(e.get(h, "")) == row_data[h] for h in headers):
        #             self.model.removeRow(ligne)
        #
        #             # 🔹 mettre à jour le JSON
        #             layer = row_data.get("Layer") or row_data.get("layer")
        #             ident = int(row_data.get("id", 0))
        #             if layer in dico_json and ident in dico_json[layer]:
        #                 dico_json[layer].remove(ident)
        #                 # si plus d'ids pour ce layer, supprimer la clé
        #                 if not dico_json[layer]:
        #                     del dico_json[layer]
        #             break  # ligne supprimée, passer à la suivante

        # Réécrire le JSON
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(dico_json, f, indent=2, ensure_ascii=False)

        # Mettre à jour self.dico_json pour que get_sel_in_list() soit correct
        self.dico_json = dico_json

        # mettre à jour le compteur dans le parent (TableWidget)
        if hasattr(self.parent, "maj_nb_entites"):
            self.parent.maj_nb_entites(self.nom_liste)


    def open_liste(self):
        print("open_liste")
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
        # self.dialogs_liste.append(self.dialog)
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.dialog.destroyed.connect(lambda _=None, dlg=self: self.parent.dlg_liste.remove(dlg)
        )
        # self.dialog.destroyed.connect(lambda _, dlg = self.dialog:self.dialogs_liste.remove(dlg))

        self.dialog.setWindowTitle(self.parent.get_nom_list_sel())

        # recuperation des données de la liste sélectionnée
        # nom_liste = self.parent.get_nom_list_sel()
        self.nom_liste = self.parent.get_nom_list_sel()
        self.dico_json = self.parent.get_dico_from_json(self.nom_liste)

        # initialisation du tableview (creation des colonnes en fonction des champs des layers du json)
        self.init_tableview()

        self.get_sel_in_list()
        self.dialog.show()