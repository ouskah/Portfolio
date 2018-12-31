"""Script permettant d'actualiser un fichier de documentation d'une base, lorsque celle-ci a évoluée (ajout de tables etc...)
permet d'éviter de tout recommencer à zéro
"""

import pickle
import os
from bs4 import BeautifulSoup

# On demande à l'utilisateur de choisir la base du doc qu'il souhaite actualiser
base = input("Actualiser la doc de la base : ")

# Nouvelle version de la doc de la base
docpath = "db_{0}/new_doc_de_la_base_{0}.html".format(base)
soup = BeautifulSoup(open(docpath), "html.parser")
str_page_html = soup.decode()
liste_page_html_split = str_page_html.split("\n")

# Ancienne version de la doc de la base
docpath_2 = "db_{0}/doc_de_la_base_{0}.html".format(base)
soup_2 = BeautifulSoup(open(docpath_2), "html.parser")
str_page_html_2 = soup_2.decode()
liste_page_html_split_2 = str_page_html_2.split("\n")

# Nouvelle liste qui va stocker le doc actualisé
doc_actualise = []

# Loop qui actualise la doc
for d1, d2 in zip(liste_page_html_split, liste_page_html_split_2):
	if d1 == d2:
		doc_actualise.append(d1)
	else:
		doc_actualise.append(d2)

full_html = "\n".join(doc_actualise)
# On réécrit un nouveau fichier de doc qui est maintenant actualisée
with open("db_{0}/updated_doc_de_la_base_{0}.html".format(base), "w") as fichier:
	fichier.write(full_html)