import json

from PyQt5.QtCore import QMimeData, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from .fonction import *

class ListeModel(QStandardItemModel):
    def mimeTypes(self):
        return [MIME_TYPE_LISTE]

    def mimeData(self, indexes):
        lignes = sorted(set(index.row() for index in indexes))
        data = []
        for lig in lignes:
            row_data = {}
            for col in range(self.columnCount()):
                header = self.headerData(col, Qt.Horizontal)
                item = self.item(lig, col)
                row_data[header] = item.text() if item else ""
            data.append(row_data)

        payload = {
            "source_nom_liste": self.dlg.nom_liste,  # identifiant unique
            "entites": data
        }
        print("liste SOURCE 1 :", self.dlg.nom_liste)
        mime = QMimeData()
        mime.setData(MIME_TYPE_LISTE, json.dumps(payload).encode("utf-8"))
        return mime

    # activer le drop sur la liste cible
    def dropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat(MIME_TYPE_LISTE):
            return False

        payload = json.loads(bytes(data.data(MIME_TYPE_LISTE)).decode("utf-8"))
        entites = payload["entites"]
        source_nom_liste = payload["source_nom_liste"]

        # si déplacement dans la meme fenêtre on ne fait rien
        if source_nom_liste == self.dlg.nom_liste:
            return True

        # Ajouter les lignes au model cible
        for e in entites:
            self.ajoute_ligne(e)

        # Supprimer les lignes dans le DialogListe source
        for dlg in self.dlg.parent.List_dialogliste:
            # vérifier que c'est la liste source
            if dlg.nom_liste == source_nom_liste:
                # Ne jamais supprimer si source ou cible est la liste "Sélection"
                if source_nom_liste != NOM_LISTE_SELECTION and self.dlg.nom_liste != NOM_LISTE_SELECTION:
                    dlg.remove_ligne(entites)
                    break
        return True

    def ajoute_ligne(self, ligne_complete):

        # =============================================
        # Colonnes actuelles du modèle
        headers = [self.dlg.model.headerData(c, Qt.Horizontal) for c in range(self.columnCount())]

        # Ajouter de nouvelles colonnes si nécessaire
        for key in ligne_complete.keys():
            if key not in headers:
                self.setColumnCount(self.columnCount() + 1)
                self.setHeaderData(self.columnCount() - 1, Qt.Horizontal, key)
                headers.append(key)
        # ============================================

        # Vérifier si la ligne existe déjà dans le model
        # valable pour la liste selection car on peut ajouter plusieurs fois la meme entité
        # vu qu'on ne la supprime pas de la liste selection
        layer = str(ligne_complete.get("Layer"))
        ident = str(ligne_complete.get("id"))
        for row in range(self.rowCount()):
            row_layer = self.item(row, 0).text()
            row_id = self.item(row, 1).text()
            if row_layer == layer and row_id == ident:
                # La ligne existe déjà → on ne fait rien
                return

        # Créer les items dans l'ordre des colonnes
        items = []
        for header in headers:
            value = ligne_complete.get(header, "")
            items.append(QStandardItem(str(value)))

        self.appendRow(items)
        if self.dlg and self.dlg.dialog:
            table = self.dlg.dialog.tableView
            table.resizeColumnsToContents()
            table.horizontalHeader().setStretchLastSection(True)


        # items = [QStandardItem(str(value)) for value in ligne_complete.values()]
        # self.appendRow(items)

        # Redimensionner les colonnes après ajout
        if self.dlg and self.dlg.dialog:
            table = self.dlg.dialog.tableView
            table.resizeColumnsToContents()
            table.horizontalHeader().setStretchLastSection(True)

        # si c'est la liste sélection, on ajoute la ligne à la selection qgis
        if self.dlg.nom_liste == NOM_LISTE_SELECTION:
            layers = QgsProject.instance().mapLayersByName(ligne_complete["Layer"])
            layer = layers[0]
            layer.selectByIds([int(ligne_complete["id"])], QgsVectorLayer.AddToSelection)

        # =========maj du json=================
        self.maj_json_ligne(ligne_complete)

        # Mettre à jour le compteur dans le parent (facultatif)
        if hasattr(self.dlg.parent, "maj_nb_entites"):
            self.dlg.parent.maj_nb_entites(self.dlg.nom_liste)

    def maj_json_ligne(self, ligne_complete):
        # chargement du json
        fichier_json = os.path.join(get_dossier_listes(), f"{self.dlg.nom_liste}.json")
        with open(fichier_json, "r", encoding="utf-8") as f:
            dico_json = json.load(f)

        layer = ligne_complete.get("Layer")
        idents = int(ligne_complete.get("id"))
        if layer not in dico_json:
            dico_json[layer] = []

        # récrire le dico en évitant les doublons
        if idents not in dico_json[layer]:
            dico_json[layer].append(idents)

        # Réécrire le JSON
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(dico_json, f, indent=2, ensure_ascii=False)