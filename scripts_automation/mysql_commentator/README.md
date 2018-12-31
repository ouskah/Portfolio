# MySQL Commentator (documentation des databases )

**Résumé :**

- 1 seul script (ou 4 max si on souhaite corriger des commentaires ou descriptions de tables ou encore mettre à jour le schéma d'un fichier de documentation d'une base) à run 

- 1 plugin à installer sur MySQL Workbench

**Prérequis :**

- **Installer les librairies requises** en ligne de commande via la commande : 

<pre>$ pip install requirements.txt</pre>

- **Respecter l'architecture du dossier mysql_commentator** pour ne pas briser les logiques de paths

- Dans le script _commentateur.py_, **modifier les logs pour MySQL Workbench** en ajoutant les vôtres

## Etape 1 : écriture d'un fichier de documentation d'une base

Lancer le script de plugin MySQL avec _mysql-workbench-plugin-doc-generating\_database.py_ :

Source : script modifié et cloné à partir du repository suivant : https://github.com/letrunghieu/mysql-workbench-plugin-doc-generating

**Marche à suivre :**

 - 1 - Aller dans l'onglet **Scripting** de MySQL Workbench et séléctionner le fichier du script via l'option **Install Plugin/Module...**

 - 2 - Fermer et relancer MySQL Workbench

 - 3 - Aller dans l'onglet **Database** et séléctionner l'option "Reverse Engineer..."

 - 4 - Suivre les étapes et séléctionner une base à schématiser

 - 5 - Une fois les étapes terminées cliquer sur l'icône **EER Diagram** pour afficher le diagramme

 - 6 - Aller pour terminer dans l'onglet **Tools** et séléctionner la sous-option **Generate Markdown documentation from a model** de l'option **Utilities**

 - 7 - Enfin pour terminer **coller** la doc générée dans un fichier en markdown (dans le dossier il s'agit du fichier base.md), que vous pourrez convertir en **fichier HTML** par la suite.

 Via atom : ctrl + shift + M pour affichier la visionneuse et ensuite click droit "Save as HTML" à partir d'elle (ou cf un autre IDE)

**N.B :**

- Pour afficher du markdown via atom : ctrl + shift + M

- Pour afficher du HTML via atom : ctrl + shift + H

**Convention de nommage des fichiers docs :**

=> **doc\_de\_la\_base\_** + nomdelabase

Exemple :

=> doc_de_la_base_db_1.html pour la database db_1

## Etape 2 : overwrite un fichier de documentation via l'ajout de commentaires de descriptions

### Fichiers : 4 scripts :

 - commentateur.py => Commentes les colonnes de toutes les tables de tes bases de données
 - modificateur.py => Modifies les commentaires que tu as déjà réalisés
 - modificateur_desc.py => Modifies les descriptions des tables que tu as déjà réalisés
 - update_html_doc.py => Met à jour le fichier de documentation d'une base de donnée

#### 1 - Lancer le script _commentateur.py_

Interface en ligne de commande qui permet d'entrer des commentaires pour chaque colonne de la table d'une base
ainsi que des descriptions pour chacune des tables d'une base.
Cette interface permet de choisir la base, et la table que l'on souhaite commenter.

#### 2 - Si nécessaire lancer le script _modificateur.py_

Interface en ligne de commande qui permet de modifier des commentaires qui ont été préalablement ajoutés.
Ici aussi il est possible de choisir la base, ainsi que la table dont on souhaite modifier le(s) commentaire(s)
(le choix du commentaire à modifier se fait en fonction de son numéro)

#### 3 - Si nécessaire lancer le script _modificateur_desc.py_

Interface en ligne de commande qui permet de modifier des descriptions de tables qui ont été préalablement ajoutés.
Ici aussi il est possible de choisir la base dont on souhaite modifier le(s) description(s)
(le choix de la description à modifier se fait en fonction de son numéro)

#### 4 - Si le schéma d'une des bases a changé entre-temps, lancer le script _update_html_doc.py_

Interface réduite en ligne de commande qui permet d'actualiser la documentation de la base d'un fichier de doc souhaité.
(Script nécessaire lorsque le schéma d'une base est modifié/évolue)

N.B :

Cette-dernière étape nécessite l'importation/création d'un nouveau fichier HTML de la documentation de la base concernée. 
Le fichier doit suivre la convention de nommage suivante :

<pre>"new_doc_de_la_base_{nom_de_la_base}.html".format(nom_de_la_base)</pre>

Il suffit juste ensuite de lancer le script _update_html_doc.py_ pour mettre à jour le fichier de documentation.
Le fichier mis à jour suis la convention de nommage suivante : 

<pre>"updated_doc_de_la_base_{nom_de_la_base}.html".format(nom_de_la_base)</pre>

