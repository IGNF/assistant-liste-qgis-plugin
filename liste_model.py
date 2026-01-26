import json

from PyQt5.QtCore import QMimeData, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from .constantes import *


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

        # si deplacement dans la meme fentre on faite rien
        if source_nom_liste == self.dlg.nom_liste:
            return True

        # Ajouter les lignes au model cible
        for e in entites:
            self.ajoute_ligne(e)

        # Supprimer les lignes dans le DialogListe source
        for dlg in self.dlg.parent.dlg_liste:
            if dlg.nom_liste == source_nom_liste:
                dlg.remove_ligne(entites)
                break
        return True

    def ajoute_ligne(self, ligne_complete):
        items = [QStandardItem(str(value)) for value in ligne_complete.values()]
        self.appendRow(items)

        # =========maj du json=================
        self.maj_json_ligne(ligne_complete)

        # Mettre à jour le compteur dans le parent (facultatif)
        if hasattr(self.dlg.parent, "maj_nb_entites"):
            self.dlg.parent.maj_nb_entites(self.dlg.nom_liste)



    def maj_json_ligne(self, ligne_complete):
        # chargement du json
        fichier_json = os.path.join(DOSSIER_LISTE, f"{self.dlg.nom_liste}.json")
        with open(fichier_json, "r", encoding="utf-8") as f:
            dico_json = json.load(f)

        layer = ligne_complete.get("Layer")
        ident = int(ligne_complete.get("id"))
        if layer not in dico_json:
            dico_json[layer] = []

        # récrire le dico en évitant les doublons
        if ident not in dico_json[layer]:
            dico_json[layer].append(ident)

        # Réécrire le JSON
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(dico_json, f, indent=2, ensure_ascii=False)