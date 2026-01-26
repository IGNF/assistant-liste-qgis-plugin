import os
TITRE = "Assistant liste v0.0.1"
DOSSIER_LISTE = os.path.join(os.path.dirname(__file__), "LISTES")
NOM_LISTE_SELECTION = "Sélection"

# Identifier les données pour le drag&drop
# application : données generique (ni image, ni text... juste generique)
# x- : convention pur dire que ce sont MES données
# liste-entites : nom de MES données
MIME_TYPE_LISTE = "application/x-liste-entites"