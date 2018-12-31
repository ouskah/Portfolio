import pymysql.cursors
import pickle
import os
from bs4 import BeautifulSoup

import config

#################### Partie "module" importée (copy-paste) du script commentateur.py #######################

###############################################################################
#                    REECRITURE DU FICHIER HTML                               #
#      DE DOCUMENTATION AVEC AJOUT DE LA DESCRIPTION D'UNE TABLE              #
###############################################################################

def overwrite_desc(dico, base, docpath):
	"""Overwrite les descriptions (commentaires du label d'une table) de tables
	d'une base MySQL"""
	dico = dico
	if dico is None:
		pass
	else:
		soup = BeautifulSoup(open(docpath), "html.parser")
		str_page_html = soup.decode()
		liste_page_html_split = str_page_html.split("\n")
		for i, l in enumerate(liste_page_html_split):
			for tab, desc in dico.items():
				if "__" in tab:
					split_tab = tab.split("__")
					escaped_tab = "\\__".join(split_tab)
					pattern = '<p id="{}">'.format(escaped_tab)
				else:
					pattern = '<p id="{}">'.format(tab)
				if pattern in l:
					desc_index = i+1
					ligne_desc = liste_page_html_split[desc_index]
					if tab in dico.keys():
						if liste_page_html_split[desc_index+1] != "<p></p>":
							liste_page_html_split[desc_index] = "<h3 id=\"description-\">Description:</h3><p>{}</p>".format(dico[tab])
						else:
							print("deuxième condition !")
							liste_page_html_split[desc_index] = ligne_desc[:4] + " {}".format(dico[tab]) + ligne_desc[4:]
					else:
						pass
		full_html = "\n".join(liste_page_html_split)
		with open("db_{}/doc_de_la_base_{}.html".format(base, base), "w") as fichier:
			fichier.write(full_html)
		print("Fichier mis à jour !")
		return
		
##################################################################################################################
#                                                                                                                #
####################### Début du script ##########################################################################
stop = " "
while stop != "q":
	# A partir d'une selection de base on importe toutes les commentaires que l'on a généré
	def import_nested_dict_desc():
		liste_bases = [db_1, db_2, db_3, db_4]
		print(" ")
		print("Liste des bases : ")
		print("_________________")
		print(" ")
		# On affiche la liste des bases
		for b in liste_bases:
			print("- "+b)
		print(" ")	
		end_list = {}
		base = input("Choisis une base : ")
		print(" ")
		if base == db_1:
			one_path_desc = "db_{}/backups_table_description".format(db_1)
		elif base == db_2:
			one_path_desc = "db_{}/backups_table_description".format(db_2)
		elif base == db_3:
			one_path_desc = "db_{}/backups_table_description".format(db_3)
		elif base == db_4:
			one_path_desc = "db_{}/backups_table_description".format(db_4)
		else:
			print("chemin incorrect")
		# Si des commentaires ont déjà été modifiés on importe le dictionnaire modifié.
		# Dans le cas contraire on importe le dictionnaire par défaut.
		try:
			# On récupère le dictionnaire des descriptions modifiées
			chemin_desc = os.path.join(one_path_desc, 'modif_{}_simple_dict_desc.pkl'.format(base))
			with open(chemin_desc, 'rb') as fichier_desc:
				simple_dict_desc = pickle.load(fichier_desc)
		except:
			chemin_desc = os.path.join(one_path_desc, "{}_tables_desc_dict.pkl".format(base))
			with open(chemin_desc, 'rb') as fichier_desc:
				simple_dict_desc = pickle.load(fichier_desc)
		print(" ")
		CGOLD = '\033[93m'
		CBLUE = '\033[94m'
		CEND = '\033[0m'
		print(CBLUE + "Les descriptions sont en bleu " + CEND)
		print(CGOLD + "Les tables sont en jaune " + CEND + "\n")
		liste_desc = simple_dict_desc
		liste_desc_commented = []
		for i, cc in enumerate(liste_desc.items()):
			if cc[1] == '':
				pass
			else:
				# Ajout de la couleur à la description commentée de la table séléctionnée
				end_list["Descriptions {}".format(i + 1) + CGOLD + " | table : {} | ".format(cc[0]) + CEND] = cc[1]
				table = cc[0]
				liste_desc_commented.append(cc[0])
		return end_list, base, table, one_path_desc, CBLUE, CGOLD, CEND, liste_desc_commented, simple_dict_desc

	# Appel de la première fonction qui réalise l'import du fichier pickle de la base concernée
	# - simple_dict_desc = dictionnaire des commentaires modifiés
	# - base = base modifiée
	# - one_path_desc = chemin vers le dossier de la base choisie
	# - CBLUE, CEND = code couleurs
	# - liste_desc_commented = liste des colonnes qui ont été commentées
	# - dictionnaire de tous les commentaires crées
	modif_nested_dict, base, table, one_path_desc, CBLUE, CGOLD, CEND, liste_desc_commented, simple_dict_desc = import_nested_dict_desc()

	# On affiche toutes les requêtes que l'on vient d'importer
	for k,v in modif_nested_dict.items():
		print("- {} :\n".format(k) + CBLUE + "{}\n".format(v) + CEND)


	def modifier_dict_desc(base, table, one_path_desc, nested_dict):
		# TO DO : il faut importer le dico des desc modifiées
		choix_desc = input("Choisir le numéro de la description de table à changer : ")
		# Liste des labels des descriptions modifiés
		liste_labels_desc_modif = [x for x in modif_nested_dict.keys()]

		liste_number_table_desc = [x + 1 for x in range(0,len(liste_labels_desc_modif))]

		# Liste des descriptions modifiés
		liste_desc_modif = [x for x in modif_nested_dict.values()]
		label_de_desc = ""
		description = ""
		# On incite l'utilisateur à entrer un numéro de commentaire valide
		while int(choix_desc) not in liste_number_table_desc:
			choix_desc = input("Numéro de description incorrect ! Entrez un autre numéro : ")
		# Première boucle permettant de récupérer le label et le contenu d'un commentaire modifié
		# en fonction du choix de l'utilisateur
		for label, desc in modif_nested_dict.items():
			if "description {}".format(choix_desc) in label:
				label_de_desc = label
				description = desc
			else:
				pass
		print(" ")
		# On demande à l'utilisateur d'entrer une nouvelle description pour remplacer l'ancienne
		nouvelle_desc = input("Entrez votre nouvelle description : ")

		# On sauvegarde les modification dans un nouveau fichier .pkl
		chemin = os.path.join(one_path_desc, 'modif_{}_simple_dict_desc.pkl'.format(base))
		# On overwrite notre nested dictionnary afin de mettre à jour l'ensemble des descriptions
		for tab, mtab in zip(liste_desc_commented, liste_labels_desc_modif):
			if ("Descriptions {}".format(choix_desc) + CGOLD + " | table : {} | ".format(tab) + CEND) == mtab:
				nested_dict[table] = nouvelle_desc
			else:
				pass
		# On écrit le nouveau fichier modifié afin de garder une "backup" de l'original
		# On a donc une version du fichier original et une autre qui est actualisée
		with open(chemin, 'wb') as fichier:
			pickle.dump(nested_dict, fichier)
		return nested_dict

	nested_dico2 = modifier_dict_desc(base, table, one_path_desc, simple_dict_desc)
	overwrite_desc(nested_dico2, base, "db_{0}/doc_de_la_base_{0}.html".format(base))
	print(" ")
	stop = input("Continuer les modifications ?\n(taper q pour quitter ou une autre touche pour continuer) ")