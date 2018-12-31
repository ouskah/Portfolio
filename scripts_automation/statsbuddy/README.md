# Statsbuddy & rapports statistiques automatisés

**Scripts :**


- Contient un __slackbot__ (_statsbuddy.py_) qui transmet des alertes statistiques (KPI) hebdomadaires.

- Contient un script (_updash.py_) qui met automatiquement à jour le spreadsheet comparatif (semaine passée vs semaine actuelle)

- Contient un script hebdomadaire (_spreadweek.py_) qui met automatiquement à jour le spreadsheet hebdomadaire

- Contient un script mensuel (_spreadmonth.py_) qui met automatiquement à jour le spreadsheet mensuel

# Documentation Google APIs (Google Cloud Platform) :


**Etapes à suivre pour l'utilisation des API de Google :**

- 1 - Créer un projet
- 2 - Créer un credential (Service account key)
- 3 - Donner les droits "owner" au projet
- 4 - Télécharger le credential et le placer dans le fichier parent du notebook/script en question
- 5 - Partager le spreedsheet à l'adresse mail donnée par le credential

**N.B : pour chaque spreadsheet crée, le partager à l'adresse mail indiquée dans la section "Service accounts"
de IAM & admin de Google Cloud Platform.**

Sources :

- https://stackoverflow.com/questions/38949318/google-sheets-api-returns-the-caller-does-not-have-permission-when-using-serve

- https://github.com/burnash/gspread

- https://github.com/PyMySQL/PyMySQL/

**Marche à suivre :**

Installer les librairies nécessaires via la commande :

<pre>$ pip install -r requirements.txt</pre>

Lancement en mode manuel :

- Lancer le script _statsbuddy.py_ via le terminal

<pre>$ python statsbuddy.py</pre>

Lancement en mode automatisé :

- Cron le script via crontab pour qu'il soit lancé à un moment précis (tous les lundi à 10h par exemple).

N.B :

(Facultatif) penser à vérifier que le spreadsheet comparatif soit à jour (si besoin run le script _updash.py_ via le terminal).
