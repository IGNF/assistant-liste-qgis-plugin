import subprocess

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMessageBox
from qgis._gui import QgsHighlight
from qgis.core import QgsVectorLayer,QgsProject,QgsExpression, QgsFeatureRequest
from .constantes import *


def afficheDoc():
    fichier = os.path.join(os.path.dirname(__file__), "assistant_liste.pdf")
    if not os.path.isfile(fichier):
        QMessageBox.warning(None,"Information","La documentation est introuvable")
    else:
        subprocess.Popen(['start', '', fichier], shell=True)
def get_dossier_listes() -> str:
    """
        Retourne le chemin du dossier des listes.
        :return: str
        """
    project = QgsProject.instance()
    chemin_projet = project.fileName()
    dossier_projet = os.path.dirname(chemin_projet)
    dossier_listes = os.path.join(dossier_projet, "LISTES")
    return dossier_listes

def get_cleabs_from_ids(layer : QgsVectorLayer,ids : list[int]) -> list:
    """
        Retourne la liste des clés absolues correspondant aux ids donnés.
        :param layer: QgsVectorLayer
        :param ids: list[int]
        :return: list[int]
        """
    list_cleabs = []
    entites = layer.getFeatures(ids)
    for entite in entites:
        list_cleabs.append(entite[CLEABS])
    return list_cleabs

def get_ids_from_cleabs(layer : QgsVectorLayer,cleabs_list : list[str]) -> list:
    """
        Retourne la liste des ids correspondant aux cleabs donées
        :param layer: QgsVectorLayer
        :param cleabs_list: Liste des valeurs à rechercher dans le champ CLEABS
        :return: list[int]
        """
    # ids = [feature.id() for feature in layer.getFeatures() if feature[CLEABS] in cleabs]
    if not cleabs_list:
        return []

    # exemple : "cleabs" IN ('TRONROUT0000000010822670', 'TRONROUT0000000294135247')
    expr = QgsExpression(f'"{CLEABS}" IN ({", ".join(f"\'{v}\'" for v in cleabs_list)})')
    request = QgsFeatureRequest(expr)
    ids = [feat.id() for feat in layer.getFeatures(request)]
    return ids

def get_column_values(layer_name, nom_colonne):
    """
    Retourne une liste de toutes les valeurs d'une colonne pour une couche donnée.
    :param layer_name: Nom de la couche (str)
    :param nom_colonne: Nom du champ/colonne (str)
    :return: Liste des valeurs de la colonne
    """
    project = QgsProject.instance()
    layers = project.mapLayersByName(layer_name)
    if not layers:
        print(f"La couche '{layer_name}' n'existe pas.")
        return []
    layer = layers[0]
    # Vérifier que le champ existe
    if layer.fields().indexOf(nom_colonne) == -1:
        print(f"Le champ '{nom_colonne}' n'existe pas dans la couche '{layer_name}'.")
        return []
    # Récupérer toutes les valeurs
    values = [feat[nom_colonne] for feat in layer.getFeatures()]
    return values


def get_feature_by_cleabs(layer, cleabs_value):
    """
    layer : QgsVectorLayer
    cleabs_value : valeur du champ CLEABS à rechercher
    """
    expr = QgsExpression(f'"{CLEABS}" = \'{cleabs_value}\'')
    request = QgsFeatureRequest(expr)

    features = [f for f in layer.getFeatures(request)]
    return features


def clignoter_feature(layer, feature, canvas, duree=1000, intervalle=300):
    """
    layer : QgsVectorLayer contenant la feature
    feature : QgsFeature à faire clignoter
    canvas : QgsMapCanvas
    duree : durée totale du clignotement en ms
    intervalle : intervalle entre visible/invisible en ms
    """
    highlight = QgsHighlight(canvas, feature.geometry(), layer)
    highlight.setColor(Qt.red)
    highlight.setWidth(3)

    # pour clignoter
    timer = QTimer()
    compteur = 0
    max_count = duree // intervalle

    def toggle():
        nonlocal compteur
        highlight.setVisible(not highlight.isVisible())
        compteur += 1
        if compteur >= max_count:
            highlight.hide()
            timer.stop()

    timer.timeout.connect(toggle)
    timer.start(intervalle)