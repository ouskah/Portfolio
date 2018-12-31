import config

import pymysql.cursors
import pickle
import os
from bs4 import BeautifulSoup


###############################################################################
#              REECRITURE DU FICHIER HTML DE DOCUMENTATION                    #
#          AVEC AJOUT DES COMMENTAIRES DE COLONNES D'UNE TABLE                #
###############################################################################

def overwrite_comments(dico, base, docpath):
	dico = dico
	soup = BeautifulSoup(open(docpath), "html.parser")
	str_page_html = soup.decode()
	liste_page_html_split = str_page_html.split("\n")
	for i, l in enumerate(liste_page_html_split):
		for tab, col in dico[base].items():
			if "__" in tab:
				split_tab = tab.split("__")
				escaped_tab = "\\__".join(split_tab)
				pattern = '<p id="{}">'.format(escaped_tab)
			else:
				pattern = '<p id="{}">'.format(tab)
			if pattern in l:
				nouvel_index_all_cols = i + 13
				nouvel_index_one_col = nouvel_index_all_cols + 2
				for idx,cc in enumerate(col.items()):
					index_com = nouvel_index_one_col + 4
					ligne_com = liste_page_html_split[index_com]
					# Structure permettant d'éviter les doublons 
					if liste_page_html_split[index_com] != "<td></td>":
						liste_page_html_split[index_com] = "<td>{}</td>".format(cc[1])
					else:
						liste_page_html_split[index_com] = ligne_com[:4] + " {}".format(cc[1]) + ligne_com[4:]

					nouvel_index_one_col += 7
					index_com += 7

	full_html = "\n".join(liste_page_html_split)


	with open("db_{0}/doc_de_la_base_{0}.html".format(base), "w") as fichier:
		fichier.write(full_html)
	return dico

##################################################################################################################
#                                                                                                                #
####################### Début du script ##########################################################################

stop = " "
while stop != "q":
	# A partir d'une selection de base on importe toutes les commentaires que l'on a généré
	def import_nested_dict_comments():
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
			one_path = "db_{}/backups_col_comments".format(db_1)
		elif base == db_2:
			one_path = "db_{}/backups_col_comments".format(db_2)
		elif base == db_3:
			one_path = "db_{}/backups_col_comments".format(db_3)
		elif base == db_4:
			one_path = "db_{}/backups_col_comments".format(db_4)
		else:
			print("chemin incorrect")
		# Si des commentaires ont déjà été modifiés on importe le dictionnaire modifié.
		# Dans le cas contraire on importe le dictionnaire par défaut.
		try:
			# On récupère le dictionnaire des commentaires modifiés 
			chemin = os.path.join(one_path, 'modif_{}_nested_dict_comments.pkl'.format(base))
			with open(chemin, 'rb') as fichier:
				nested_dict = pickle.load(fichier)
		except:
			# Sinon on récupère simplement le dictionnaire des commentaires ajoutés
			chemin = os.path.join(one_path, '{}_nested_dict.pkl'.format(base))
			with open(chemin, 'rb') as fichier:
				nested_dict = pickle.load(fichier)

		# Choisir la table dont on va récupérer les commentaires des colonnes déjà commentées 	
		table = input("Choisis une table : ")
		print(" ")
		CGOLD = '\033[93m'
		CBLUE = '\033[94m'
		CEND = '\033[0m'
		print(CBLUE + "Les commentaires sont en bleu " + CEND)
		print(CGOLD + "Les colonnes sont en jaune " + CEND + "\n")
		liste_comments = nested_dict[base][table]
		liste_col_commented = []
		for i, cc in enumerate(liste_comments.items()):
			if cc[1] == '':
				pass
			else:
				# Ajout de la couleur à la colonne commentée de la table séléctionnée
				end_list["commentaire {}".format(i + 1) + CGOLD + " | colonne : {} | ".format(cc[0]) + CEND] = cc[1]
				liste_col_commented.append(cc[0])
		return end_list, base, table, one_path, CBLUE, CGOLD, CEND, liste_col_commented, nested_dict

	# Appel de la première fonction qui réalise l'import du fichier pickle de la base concernée
	# - modif_nested_dict = dictionnaire des commentaires modifiés
	# - base = base modifiée
	# - one_path = chemin vers le dossier de la base choisie
	# - CBLUE, CEND = code couleurs
	# - liste_col_commented = liste des colonnes qui ont été commentées
	# - dictionnaire de tous les commentaires crées 
	modif_nested_dict, base, table, one_path, CBLUE, CGOLD, CEND, liste_col_commented, nested_dict = import_nested_dict_comments()

	# On affiche toutes les requêtes que l'on vient d'importer
	for k,v in modif_nested_dict.items():
		print("- {} :\n".format(k) + CBLUE + "{}\n".format(v) + CEND)

	# Modifier un commentaire déjà réalisé
	def modifier_nested_dict_comments(modif_nested_dict, base, table, one_path, nested_dict):
		# On demande à l'utilisateur de choisir le commentaire qu'il souhaite modifier
		choix_com = input("Choisir le numéro de commentaire à changer : ")

		# Liste des labels des commentaires modifiés
		liste_labels_com_modif = [x for x in modif_nested_dict.keys()]
		# Liste des numéros des commentaires
		liste_number_com = [x + 1 for x in range(0,len(liste_labels_com_modif))]
		# Liste des commentaires modifiés
		liste_com_modif = [x for x in modif_nested_dict.values()]
		label_du_comment = ""
		commentaire = ""
		# On incite l'utilisateur à entrer un numéro de commentaire valide
		while int(choix_com) not in liste_number_com:
			choix_com = input("Numéro de commentaire incorrect ! Entrez un autre numéro : ")
		# Première boucle permettant de récupérer le label et le contenu d'un commentaire modifié
		# en fonction du choix de l'utilisateur
		for label, com in modif_nested_dict.items():
			if "commentaire {}".format(choix_com) in label:
				label_du_comment = label
				commentaire = com
			else:
				pass
		print(" ")
		# On demande à l'utilisateur d'entrer un nouveau commentaire pour remplacer l'ancien
		nouveau_comment = input("Entrez votre nouveau commentaire : ")

		# On sauvegarde les modification dans un nouveau fichier .pkl
		chemin = os.path.join(one_path, 'modif_{}_nested_dict_comments.pkl'.format(base))
		# On overwrite notre nested dictionnary afin de mettre à jour l'ensemble des commentaires
		for col, mcol in zip(liste_col_commented, liste_labels_com_modif):
			if ("commentaire {}".format(choix_com) + CGOLD + " | colonne : {} | ".format(col) + CEND) == mcol:
				nested_dict[base][table][col] = nouveau_comment
			else:
				pass
		# On écrit le nouveau fichier modifié afin de garder une "backup" de l'original
		# On a donc une version du fichier original et une autre qui est actualisée
		with open(chemin, 'wb') as fichier:
			pickle.dump(nested_dict, fichier) 
		return nested_dict

	nested_dico = modifier_nested_dict_comments(modif_nested_dict, base, table, one_path, nested_dict)
	# On met à jour le fichier de documentation de la base séléctionnée
	overwrite_comments(nested_dico, base, "db_{0}/doc_de_la_base_{0}.html".format(base))
	print(" ")
	stop = input("Continuer les modifications ?\n(taper q pour quitter ou une autre touche pour continuer) ")

