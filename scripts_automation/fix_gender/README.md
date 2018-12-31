# Fix Gender

Court script en python qui permet d'estimer le genre d'un individu à partir de son prénom.
Il peut être utilisé pour imputer les valeurs de la variable de genre d'une base de donnée à partir du prénom d'un individu
(cela permet de diminuer la proportion de valeurs nulles d'une base de donnée).

### Requirements

Installer le module Gender Guesser via pip (lien du module : https://pypi.org/project/gender-guesser/)

<pre> pip install gender-guesser </pre>

### Usage

Run le script en ligne de commande via python en ajoutant en argument le prénom d'un individu :

<pre> python fix_gender.py John </pre>

Affiche :

<pre>
1
Temps d'exécution : 0.306 seconds
</pre>
