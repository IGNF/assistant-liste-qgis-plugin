<table>
<colgroup>
<col style="width: 21%" />
<col style="width: 78%" />
</colgroup>
<tbody>
<tr>
<td rowspan="2"><img src="images/image3.jpeg"
style="width:1.38681in;height:1.47153in"
alt="logo_IGN_pour_lettre" /></td>
<td style="text-align: center;"><p><strong>Manuel utilisateur du plugin
« Assistant listes »</strong></p>
<p><strong>V0.1.0</strong></p></td>
</tr>
<tr>
<td style="text-align: center;"></td>
</tr>
</tbody>
</table>



| Version |    Date    | Modifié par    | Historique des modifications |
|:-------:|:----------:|----------------|------------------------------|
|  0.1.0  | 05/02/2026 | Gérôme PECHEUR | Création                     |

**Sommaire**

[1 Prérequis](#prérequis)

[2 Résumé](#résumé)

[3 Installation](#installation)

[4 Présentation du gestionnaire de listes](#présentation-du-gestionnaire-de-listes)

[5 Présentation d’une liste](#présentation-dune-liste)

[6 Création de listes](#création-de-listes)

[7 Ajout d’éléments dans une liste](#ajout-déléments-dans-une-liste)

[7.1 Via : <img src="images/image4.png"
style="width:0.67847in;height:0.18264in" />](#via)

[7.2 Via : « glissé & déposé »](#via-glissé-déposé)

[7.2.1 D’une liste A vers la liste « sélection » :](#dune-liste-a-vers-la-liste-sélection)

[7.2.2 De la liste « Sélection » vers une liste A](#de-la-liste-sélection-vers-une-liste-a)

[7.2.3 D’une liste A vers une liste B](#dune-liste-a-vers-une-liste-b)

[8 Suppression d’éléments dans une liste](#suppression-déléments-dans-une-liste)

[8.1 Via le menu contextuel](#via-le-menu-contextuel)

[8.2 Via : « glissé & déposé »](#via-glissé-déposé-1)

[9 Ouverture de la table attributaire](#ouverture-de-la-table-attributaire)

# Prérequis

Version de QGIS : 3.40 ou supérieur.

Le plugin « maitre » doit être installé préalablement.

# Résumé

Ce plugin permet de gérer des listes d’entités de géométries différentes
(création, suppression)

# Installation

Ouvrir QGIS.

Allez dans **Extensions/Installer/Gérer les extensions**, cliquez sur
**Installer depuis un ZIP**, sélectionner le fichier ZIP puis cliquez
sur **Installer le plugin**.

<img src="images/image5.png"
style="width:6.83889in;height:1.525in" />

# Présentation du gestionnaire de listes

<img src="images/image6.png"
style="width:1.81281in;height:2.14783in" />

Par défaut ce gestionnaire de liste intègre une liste spéciale
« Sélection »

Cette liste est mise à jour à chaque changement de sélection dans QGIS.

<img src="images/image7.png"
style="width:1.98261in;height:0.19022in" /> : Création d’une nouvelle
liste (renseigner un nom puis appuyer sur entrée)

<img src="images/image8.png"
style="width:0.25208in;height:0.26944in" /> : Suppression de toutes les
listes

<img src="images/image9.png"
style="width:0.25208in;height:0.26944in" /> : Suppression de toutes les
listes vides.

<img src="images/image10.png"
style="width:0.26944in;height:0.26944in" /> : Suppression de la liste
sélectionnée.

<img src="images/image11.png"
style="width:0.67847in;height:0.18264in" /> : Sélection dans QGIS de
toutes les entités de la liste sélectionnée.

<img src="images/image4.png"
style="width:0.67847in;height:0.18264in" /> : Ajout dans la liste de
toutes les entités sélectionnées dans QGIS.

<img src="images/image12.png"
style="width:0.26944in;height:0.21736in" /> : Importation d’une liste
(identifiants ou cleabs)

<img src="images/image13.png"
style="width:0.26111in;height:0.19097in" /> : exporter la liste
sélectionnée (le format peut être : identifiants ou cleabs)

![](images/image2.png) : A propos de … (historique des versions et
visualisation de cette documentation)

<img src="images/image14.png"
style="width:1.93043in;height:2.2752in" />

Gestionnaire configuré avec plusieurs listes.

Pour ouvrir une liste il faut faire un « double-clic » sur la liste
désirée.

# Présentation d’une liste

<img src="images/image15.png"
style="width:4.4in;height:2.02639in" />

# Création de listes

> <img src="images/image7.png"
> style="width:2.04348in;height:0.19606in" />
>
> La nouvelle liste ne doit pas se nommer « Sélection » ni être déjà
> présente dans le gestionnaire.

# Ajout d’éléments dans une liste

## Via : <img src="images/image4.png"
style="width:0.67847in;height:0.18264in" />

Ajoute dans la liste toutes les entités sélectionnées dans QGIS (le
contenu de la liste est vidée avant ajout)

## Via : « glissé & déposé »

> On peut effectuer un « glisser & déposé » de lignes d’une liste vers
> une autre liste.
>
> On peut sélectionner plusieurs lignes.

### D’une liste A vers la liste « sélection » : 

- Une ou plusieurs lignes sont ajoutées à la liste « Sélection », les
  entités correspondantes sont également ajoutées à la sélection de
  QGIS.

- La liste « A » n’est pas modifiée (la ou les lignes de la liste
  d’origine ne sont pas supprimées).

### De la liste « Sélection » vers une liste A

- Une ou plusieurs lignes sont ajoutées à la liste « A »

- La liste « Sélection » n’est pas modifiée.

### D’une liste A vers une liste B

- La ou les ligne sont supprimées de la liste « A »

- La ou les ligne sont ajoutées de la liste « B »

# Suppression d’éléments dans une liste

## Via le menu contextuel

- On sélectionne une ou plusieurs lignes d’une liste

- Un « clic droit » fait apparaitre un menu contextuel :

<img src="images/image16.png"
style="width:2.37391in;height:0.4702in" />

Cas de la liste « Sélection » :

- La ou les lignes sont supprimées de la liste et <span class="mark">la
  sélection dans QGIS est actualisée</span> ;

Cas d’une liste quelconque :

- La ou les lignes sont supprimées de la liste

## Via : « glissé & déposé »

> Le glissé & déposé de la liste « A » vers la liste « B » ajoute les
> lignes dans la liste « B » et supprime les lignes dans la liste « A »

# Ouverture de la table attributaire

Via le menu contextuel il est possible d’ouvrir la table attributaire
QGIS correspondant à la ligne sélectionnées (= entités)

Si plusieurs lignes correspondent à des entités appartenant à
différentes couches, une table attributaire sera ouverte pour chaque
couche.
