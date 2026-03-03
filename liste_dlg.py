import json
import time
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QMenu, QMessageBox
from pyexpat import features

from qgis._core import QgsCoordinateTransform
from qgis._gui import QgsAttributeTableFilterModel
from qgis.gui import QgsGui
from qgis.core import QgsExpression, QgsFeatureRequest
from scipy.linalg.interpolative import id_to_svd

from .fonction import *
from .filtre import *
from .constantes import *
from .liste_model import ListeModel




class DialogListe(QObject):
    drag_started = pyqtSignal(object, list)
    def __init__(self,plugin_parent=None):
        super().__init__()
        # dictionnaire des layers contenu dans une liste
        self.dlgfiltre = None
        self.nom_liste = None
        self.dico_layer_cleabs_from_liste = {}
        self.dialog = None
        self.dlg_attr = None
        self.dico_json = None
        self.model = None
        self.parent = plugin_parent
        self.colonne_filtre = set()

    def start_drag(self):
        selection = self.get_selected_entites()  # [{"layer":..., "id":...}, ...]
        self.drag_started.emit(self, selection)

    def init_tableview(self):
        # on passe par la classe dérivée pour gérer le drag&drop
        self.model = ListeModel()
        self.model.dlg = self

        # événement d'ajout — suppression dans le model
        self.model.rowsInserted.connect(self.on_update_label_nb_entite)
        self.model.rowsRemoved.connect(self.on_update_label_nb_entite)
        # self.model.rowsInserted.connect(lambda: self.dialog.tableView.resizeColumnsToContents())
        # self.dialog.tableView.resizeColumnsToContents()

        layers,champs = self.get_structure_layer()
        if champs:
            champs = ["Layer","id"] + list(champs)
        self.model.setColumnCount(len(champs))
        self.model.setHorizontalHeaderLabels(champs)
        self.dialog.tableView.setModel(self.model)

        self.dialog.tableView.verticalHeader().setDefaultSectionSize(10)
        self.dialog.tableView.setSortingEnabled(True)

    def on_update_label_nb_entite(self):
        self.dialog.label_nb_entite.setText(f"Nombre d'entités = {self.model.rowCount()}")

    def on_show_menu_supp(self, position):
        selection_model = self.dialog.tableView.selectionModel()
        select_ligne = {index.row() for index in selection_model.selectedRows()}  # set de lignes sélectionnées
        if not select_ligne:
            return  # aucune sélection

        menu = QMenu()
        enlever_ligne = menu.addAction("Enlever de la liste")
        zoom_selection = menu.addAction("Zoomer sur les entités sélectionnées")
        open_tableattributaire = menu.addAction("Ouvrir la table attributaire des entités sélectionnées")
        action = menu.exec_(self.dialog.tableView.viewport().mapToGlobal(position))

        # ================================
        # suppression d'une ligne
        if action == enlever_ligne:
            # supprime la ligne sélectionnée et réécrit le json , TOUTES listes sélectionnées
            self.remove_ligne()

        # ================================
        # ZOOM sur les lignes sélectionnées
        elif action == zoom_selection:
            # pour gérer le zoom par lot
            dico_layer_list_ident = {}
            all_extents = None
            for ligne in select_ligne:
                id_layer = self.model.index(ligne, 0)
                layer_name = self.model.data(id_layer)
                id_ident = self.model.index(ligne, 1)
                ident = self.model.data(id_ident)
                layers = QgsProject.instance().mapLayersByName(layer_name)
                layer = layers[0]
                if layer not in dico_layer_list_ident:
                    dico_layer_list_ident[layer] = []
                dico_layer_list_ident[layer].append(int(ident))

                # faire clignoter l'entité
                feature = layer.getFeature(int(ident))
                clignoter_feature(layer,feature , self.parent.iface.mapCanvas(), duree=3000, intervalle=300)

            # Calculer l’étendue combinée
            project_crs = QgsProject.instance().crs()
            for layer, liste_ident in dico_layer_list_ident.items():
                request = QgsFeatureRequest().setFilterFids(liste_ident)

                # transformateur si nécessaire
                layer_crs = layer.crs()
                xform = None
                if layer_crs != project_crs:
                    xform = QgsCoordinateTransform(layer_crs, project_crs, QgsProject.instance())

                for f in layer.getFeatures(request):
                    geom = f.geometry()
                    if geom is None:
                        continue
                    if xform:
                        geom.transform(xform)  # transforme dans le CRS du projet
                    if all_extents is None:
                        all_extents = geom.boundingBox()
                    else:
                        all_extents.combineExtentWith(geom.boundingBox())

            # Zoomer une seule fois
            if all_extents:
                all_extents.grow(5)  # tampon
                self.parent.iface.mapCanvas().setExtent(all_extents)
                self.parent.iface.mapCanvas().refresh()

        # ================================
        # Ouvrir la table attributaire des entités sélectionnées
        elif action == open_tableattributaire:
            self.on_open_table_attribut(ligne ="selected")
        # mise à jour du nombre d'entités dans le tablewidget parent
        nom_liste = self.parent.get_nom_list_sel()
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
                liste_champ.add(field.name())
        return layer_name,liste_champ

    def is_dico_cles_absolue(self,dico):
        values = dico.values()
        # vérifier que chaque sous-liste contient uniquement des int → liste d'identifiants)
        if all(all(isinstance(item, int) for item in sublist) for sublist in values):
            return False
        # vérifier que chaque sous-liste contient uniquement des str → clés absolues)
        elif all(all(isinstance(item, str) for item in sublist) for sublist in values):
            return True
        else:
            return None



    def get_sel_in_list(self):
        all_rows = []
        # on ne récupère que les champs à partir de la 3ieme colonne (donc sauf "layer et "id")
        champs_entete = [
                str(self.model.headerData(col, Qt.Horizontal, Qt.DisplayRole))
                for col in range(2,self.model.columnCount())
            ]
        # si liste "selection" on vide le tableview avant de remplir (pour éviter les doublons)
        if self.nom_liste == NOM_LISTE_SELECTION:
            self.model.removeRows(0, self.model.rowCount())

        # test si le json contient des entiers → liste d'identifiants
        # ou des chaines de caractères → liste de clés absolues
        res = self.is_dico_cles_absolue(self.dico_json)
        if res:
            dico_ident =self.parent.transform_dico_cleabs_to_ident(self.dico_json)
            # récrire le json avec les identifiants pour éviter de refaire la transformation à chaque ouverture de la liste
            fichier_json = os.path.join(get_dossier_listes(), f"{self.nom_liste}.json")
            with open(fichier_json, "w", encoding="utf-8") as f:
                json.dump(dico_ident, f, indent=2, ensure_ascii=False)
        # liste d'identifiants
        elif not res:
            pass
        else :
            QMessageBox.warning(self.dialog, "Format JSON non supporté", "Le format du JSON n'est pas supporté."
                                                                         " Le json doit contenir\n\n- uniquement des entiers (identifiants)\nou\n"
                                                                         "- uniquement des chaînes de caractères (clés absolues).")

        for layer_name, ids_sel in self.dico_json.items():
            layers = QgsProject.instance().mapLayersByName(layer_name)
            if not layers:
                continue
            layer = layers[0]

            row_items = [QStandardItem(layer_name)]
            row_items[0].setFlags(row_items[0].flags() & ~Qt.ItemIsEditable)

            for ident in ids_sel:
                feature = layer.getFeature(ident)
                if not feature.isValid():
                    continue
                row_items = []
                item_layer = QStandardItem(layer_name)
                item_layer.setFlags(item_layer.flags() & ~Qt.ItemIsEditable)
                row_items.append(item_layer)
                item_ident = QStandardItem(str(ident))
                item_ident.setFlags(item_ident.flags() & ~Qt.ItemIsEditable)
                row_items.append(item_ident)
                for champ in champs_entete:
                    # si le champ existe
                    if feature.fields().indexOf(champ) != -1:
                        valeur = feature.attribute(champ)
                        item = QStandardItem("" if valeur is None else str(valeur))
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    else:
                        item = QStandardItem("")
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    row_items.append(item)
                # ajout de la ligne complète
                self.model.appendRow(row_items)
            self.dialog.tableView.resizeColumnsToContents()

    # menu popup ou toutes les lignes
    def on_open_table_attribut(self,ligne="All"):
        select_ligne = []
        if ligne == "selected":
            selection_model = self.dialog.tableView.selectionModel()
            select_ligne = {index.row() for index in selection_model.selectedRows()}
        elif ligne == "All":
            select_ligne = range(self.model.rowCount())
        elif isinstance(ligne, int):
            select_ligne = [ligne]

        dico_layer_listident = {}
        for index in select_ligne:
            layer_name = self.model.item(index, 0).text()
            ident = self.model.item(index, 1).text()
            layers = QgsProject.instance().mapLayersByName(layer_name)
            layer = layers[0]
            if layer not in dico_layer_listident:
                 dico_layer_listident[layer] = []
            dico_layer_listident[layer].append(int(ident))

        for layer, list_id in dico_layer_listident.items():
            expr_str = f"@id IN ({', '.join(str(fid) for fid in list_id)})"
            self.parent.iface.showAttributeTable(layer, expr_str)

    def apply_selected_filter(self,layer):
        mgr = QgsGui.instance().attributeTableManager()
        if not mgr:
            return
        # Récupérer la table ouverte pour cette couche
        tbl = mgr.table(layer)
        if tbl:
            tbl.setFilterMode(tbl.ShowSelected)

    def on_show_filtre(self):
        self.dlgfiltre = DialogFiltre(self)
        self.dlgfiltre.open_dialog()

        self.colonne_filtre = self.dlgfiltre.get_checked_columns()
        self.apply_column_filter()

        # sauvegarder la configuration du filtre dans le plugin parent
        self.parent.colonne_filtre_par_liste[self.nom_liste] = self.colonne_filtre

    def apply_column_filter(self):
        if not self.model:
            return
        for col in range(self.model.columnCount()):
            entete = self.model.headerData(col, Qt.Horizontal)
            if entete in self.colonne_filtre:
                self.dialog.tableView.hideColumn(col)
            else:
                self.dialog.tableView.showColumn(col)

    # entites : liste de dico des champs
    def remove_ligne(self, entites = None):
        # Charger le JSON existant
        fichier_json = os.path.join(get_dossier_listes(), f"{self.nom_liste}.json")
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
                layer_name = self.model.item(ligne, 0).text()
                ident = int(self.model.item(ligne, 1).text())
                entites.append({"Layer": layer_name, "id": ident})

        for ligne in reversed(range(self.model.rowCount())):
            row_layer = self.model.item(ligne, 0).text()
            row_id = int(self.model.item(ligne, 1).text())

            for e in entites:
                e_layer = str(e.get("Layer") or e.get("layer") or "")
                if e_layer == row_layer and int(e.get("id", 0)) == row_id:
                    self.model.removeRow(ligne)

                    # si c'est la liste sélection on désélectionne la ligne
                    if self.nom_liste == NOM_LISTE_SELECTION:
                        layers = QgsProject.instance().mapLayersByName(row_layer)
                        layer = layers[0]
                        layer.selectByIds([row_id], QgsVectorLayer.RemoveFromSelection)

                    # 🔹 mettre à jour le JSON
                    if row_layer in dico_json and row_id in dico_json[row_layer]:
                        dico_json[row_layer].remove(row_id)
                        if not dico_json[row_layer]:
                            del dico_json[row_layer]
                    break
        self.dialog.tableView.viewport().update()

        # Réécrire le JSON
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(dico_json, f, indent=2, ensure_ascii=False)

        # Mettre à jour self.dico_json pour que get_sel_in_list() soit correct
        self.dico_json = dico_json

        # mettre à jour le compteur dans le parent (TableWidget)
        self.parent.maj_nb_entites(self.nom_liste)

    def open_liste(self):
        # récuperation des données de la liste sélectionnée
        self.nom_liste = self.parent.get_nom_list_sel()
        self.dico_json = self.parent.get_dico_from_json(self.nom_liste)

        # vérifier si la liste est déjà ouverte
        for dlg in self.parent.List_dialogliste:
            if dlg.nom_liste == self.nom_liste and dlg.dialog is not None and dlg.dialog.isVisible():
                # passe la fenetre en premier plan
                dlg.dialog.raise_()
                # donne le focus
                dlg.dialog.activateWindow()
                return

        self.dialog = QDialog()
        loadUi(os.path.join(os.path.dirname(__file__), "liste.ui"), self.dialog)
        self.dialog.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # slot
        self.dialog.pushButtonOpenTableAttribut.clicked.connect(lambda :self.on_open_table_attribut(ligne ="All"))
        self.dialog.tableView.doubleClicked.connect(lambda index : self.on_open_table_attribut(ligne = index.row()))
        self.dialog.pushButtonHide.clicked.connect(self.on_show_filtre)

        # menu contextuel
        self.dialog.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dialog.tableView.customContextMenuRequested.connect(self.on_show_menu_supp)

        # gestion d'ouverture de plusieurs dialog liste
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.dialog.destroyed.connect(lambda _=None, dlg=self: self.parent.List_dialogliste.remove(dlg))

        self.dialog.setWindowTitle(self.parent.get_nom_list_sel())

        # initialisation du tableview (creation des colonnes en fonction des champs des layers du json)
        self.init_tableview()

        self.get_sel_in_list()

        # restauration du filtre si déjà défini
        self.colonne_filtre = self.parent.colonne_filtre_par_liste.get(self.nom_liste, set())

        # appliquer le filtre
        self.apply_column_filter()

        self.dialog.show()
