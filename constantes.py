import os
from pathlib import Path


TITRE = "Assistant liste v0.0.1"

NOM_LISTE_SELECTION = "Sélection"
CLEABS = "cleabs"

# Identifier les données pour le drag&drop
# application : données génériques (ni image, ni text... juste générique)
# x- : convention pur dire que ce sont MES données
# liste-entites : nom de MES données
MIME_TYPE_LISTE = "application/x-liste-entites"