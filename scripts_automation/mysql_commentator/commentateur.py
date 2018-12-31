# import des modules nécessaires
# module permettant d'importer et d'enregistrer des objets (permet de réaliser des backups de variables par exemple)
import pickle
# module permettant d'intéragir avec son système d'exploitation
import os
# module permettant d'intéragir avec une base de donnée MySQL (réalisations de requêtes)
import pymysql.cursors
# module permettant de dump un dictionnaire en fichier yaml
import yaml
# module permettant de parser du html
from bs4 import BeautifulSoup

from config import *

###########################################################################################################################################
#                                                DESCRIPTION DU SCRIPT                                                                    #
###########################################################################################################################################

"""
Ce script doit être stocké de préférence dans un dossier distinct car il produit :

- des sauvegardes d'objets qui sont crées et/ou importées à chaque fois que l'utilisateur démarre une session de travail
- un fichier .html qui contient la documentation de la base sélectionnée

"""
# On crée un dossier par database avec 2 sous-dossiers
# On simplifie volontairement la vérification en partant du principe que si le premier dossier à été crée
# les autres l'ont aussi été (et réciproquement)
current_path = os.getcwd()
true_path = os.path.exists("{0}/db_{1}".format(current_path, db_1))
if true_path is False:
    dirnames = ["db_{}".format(x) for x in [db_1, db_2, db_3, db_4]]
    for d in dirnames:
        os.mkdir(d)
        os.mkdir("{}/backups_col_comments".format(d))
        os.mkdir("{}/backups_table_description".format(d))
else:
    pass
############################################################################################
#                           EXTRACTIONS MYSQL                                              #
#                 DESCRIPTIONS DES COLONNES DE LA TABLE D'UNE BASE                         #
############################################################################################

def desc_extract(base=base, table=table):
    """Fonction qui extrait la description de chaque colonne de la table d'une base MYSQL"""
    # dictionnaire de la description d'une table 
    dico = {}
    # On se connecte à une database
    # Remplir vos logs de connexion ici 
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                db=base,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql_all = [
                "DESCRIBE {}.{} ".format(base, table),
            ]
            # Pour chaque requête on l'exécute et stock le résultat dans notre dictionnaire
            for sql in sql_all:
                cursor.execute(sql)
                result = cursor.fetchall()
                dico = result  
    # On cloture la session            
    finally:
        connection.close()
    # On créer une liste contenant les labels des colonnes d'une table
    liste_columns = []
    # On créer la définition de chaque colonne de la base
    list_def_columns = []
    # On construit nos définitions de colonnes pour les futurs ALTER TABLE 
    for x in dico:
        if x['Null'] == 'NO':
            val_null = 'NOT NULL'
        else:
            val_null = 'NULL'
        
        if x['Extra'] == 'auto_increment':
            val_extra = 'auto_increment'
        else:
            val_extra = ''
        # Création de la définition d'une colonne    
        col_def = "{} {} {}".format(x['Type'], val_null, val_extra)
        list_def_columns.append(col_def)
        # Ajout des labels des colonnes de la base en question
        # Cette forme de "filtrage" permet de distinguer les colonnes aux mêmes labels inter-tables
        liste_columns.append(base+"."+table+"|"+x['Field'])

    return list_def_columns, liste_columns, dico, table, base


print("------------------------------------------------------------------------------------------------")
print(">                                MySQL COMMENTATOR                                             <")
print(">______________________________________________________________________________________________<")
print(" ")
liste_bases = [db_1, db_2, db_3, db_4]
#print("-----------------")
print("Liste des bases : ")
print("_________________")
print(" ")
# On affiche la liste des bases
for x in liste_bases:
    print("- "+x)
print(" ")
# On donne à l'utilisateur le choix concernant la base à documenter
choix_base = input("Choix de la base à documenter : ")
# # On donne à l'utilisateur le choix concernant la table à documenter
choix_table = input("Choix de la table à documenter : ")
print(" ")
# Appel de desc_extract
ld, lc, dico, table, base = desc_extract(choix_base, choix_table)

# Colorier en rouge la colonne / en vert la table => https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
print("Code couleurs : \n")
CRED = '\033[91m'
CGREEN = '\033[92m'
CGOLD = '\033[93m'
CEND = '\033[0m'
print(CGREEN + "Table en vert" + CEND)
print(CGOLD + "Colonne de la table en jaune" + CEND)
print(CRED + "Options en rouge" + CEND + "\n")

###############################################################################
#                   SAUVEGARDE & IMPORT D'OBJETS                              #
###############################################################################

# Selection d'un dossier en fonction du nom d'une base (pour définir les paths)
if base == db_1:
    one_path = "db_{}/backups_col_comments".format(db_1)
    one_path_desc = "db_{}/backups_table_description".format(db_1)
elif base == db_2:
    one_path = "db_{}/backups_col_comments".format(db_2)
    one_path_desc = "db_{}/backups_table_description".format(db_2)
elif base == db_3:
    one_path = "db_{}/backups_col_comments".format(db_3)
    one_path_desc = "db_{}/backups_table_description".format(db_3)
elif base == db_4:
    one_path = "db_{}/backups_col_comments".format(db_4)
    one_path_desc = "db_{}/backups_table_description".format(db_4)
else:
    print("chemin incorrect")

def save_nested_dict_pickle(nom_fichier, objet, one_path=one_path):
    """Enregistre la liste des requetes
    N.B : par défaut le path correspond aux backups des colonnes commentées"""
    chemin = os.path.join(one_path, nom_fichier)
    with open(chemin, 'wb') as fichier:
        pickle.dump(objet, fichier)
       
def upload_nested_dict_pickle(file, one_path=one_path):
    """Importe la liste des requetes
    N.B : par défaut le path correspond aux backups des colonnes commentées"""
    chemin = os.path.join(one_path, file)
    if file != None:
    	with open(chemin, 'rb') as fichier:
        	nested_dict = pickle.load(fichier)
    else:
    	nested_dict = {}
    return nested_dict  

#################################################################################
#                               GENERATEUR DE                                   #
#                            DESCRIPTIONS DE TABLES                             #
#################################################################################
	
def desc_generator(base, choix_table=choix_table):
	try:
		dico_table_desc = upload_nested_dict_pickle("{}_tables_desc_dict.pkl".format(base), one_path_desc)
		table_commented = upload_nested_dict_pickle("{}_tables_desc_list.pkl".format(base), one_path_desc)
	except:
		dico_table_desc = {choix_table: None}
		table_commented = []
	if choix_table in table_commented:
		pass
	else:
		desc_tab = input("Ajoutez une description à la table {} : ".format(choix_table))
		print(" ")
		dico_table_desc[choix_table] = desc_tab
		table_commented.append(choix_table)
		save_nested_dict_pickle("{}_tables_desc_dict.pkl".format(base), dico_table_desc, one_path_desc)
		save_nested_dict_pickle("{}_tables_desc_list.pkl".format(base), table_commented, one_path_desc)
	return dico_table_desc

try:
	td = upload_nested_dict_pickle("{}_tables_desc_list.pkl".format(base), one_path_desc)
except:
	td = []

if choix_table not in td:
	dico_table_desc = desc_generator(choix_base)
else:
	dico_table_desc = None
	pass

#################################################################################
#				                GENERATEUR DE                                   #
#                        COMMENTAIRES DE COLONNES D'UNE TABLE                   #
#################################################################################
    
def comment_generator(lc=lc, col_commented=[]):
    """Fonction permettant d'ajouter les commentaires des colonnes d'une table """
    # On stock toutes les colonnes d'une table qui ont été commentées 
    try:
    	dico_1 = upload_nested_dict_pickle("{}_nested_dict.pkl".format(base))
    	col_commented = upload_nested_dict_pickle("{}_col_com.pkl".format(base))
    except:
    	dico_1 = {}
    	col_commented = col_commented
    # On construit notre liste de requêtes via une loop qui itère sur les deux listes (labels)
    for col in lc:
        # split pour ne garder que le nom de la colonne
        col_splited = col.split("|")
        # Vérification : si on a déjà traité une colonne on passe et on en traite une autre
        if col in col_commented:
            pass
        else:
        # L'utilisateur peut commenter chaque colonne une à une
            com_part1 = "Ajoute un commentaire pour la colonne "+CGOLD+"{}".format(col_splited[1])+CEND+" de la table "
            com_part2 = CGREEN+"{}".format(table)+CEND
            com_part3 = " (taper " + CRED + "q" + CEND + " pour faire un break) : \n" 
            comment = input(com_part1+com_part2+com_part3)
            print(" ")
            modif = None
            if comment != "q":
            # On ajoute la possibilité de modifier son précédent commentaire
                while (modif != "e" and modif != ""):
                # Ajout de la possibilité de modifier un commentaire une fois écrit
                    modif_part1 = "Modifier le commentaire précédent ? tapez " + CRED + "e" + CEND
                    modif_part2 = " pour réécrire ou sur la "+ CRED + "touche entrée" + CEND + " pour passer) \n"
                    modif = input(modif_part1+modif_part2)
                    if modif.lower() == "e":
                        comment = input("Modifie le commentaire de la colonne "+CGOLD+"{}".format(col_splited[1])+CEND + \
                        	" de la table "+CGREEN+"{}".format(table)+CEND+": \n")
                        print("Commentaire modifié !")
                    elif modif == "":
                        pass
                    else:
                        print("réponse incorrecte")
                if dico_1 == {}:
                    dico_1 = {base: {table: {col_splited[1]: "{}".format(comment)}}}
                else:
                    try:
                        dico_1[base][table][col_splited[1]] = "{}".format(comment)
                    except:
                        dico_2 = {}
                        dico_2[col_splited[1]] = "{}".format(comment)
                        dico_1[base][table] = dico_2
            # Si l'utilisateur choisit de quitter la boucle on la break
            else:
                break
            col_commented.append(col)           
            # Optionnel : sauvegarde du dictionnaire sous format .yml (dans chacun des répertoires)
            # chemin = os.path.join(one_path, '{}_db_cols_comments.yml'.format(base))
            # with open(chemin, 'w') as fichier:
            #    texte = yaml.dump(dico_1, fichier, default_flow_style=False, encoding='utf-8', allow_unicode=True)

            # sauvegarde de notre liste de colonnes commentées via pickel
            save_nested_dict_pickle("{}_nested_dict.pkl".format(base), dico_1)
			# sauvegarde de notre liste de labels de colonnes déjà traitées via pickel
            save_nested_dict_pickle("{}_col_com.pkl".format(base), col_commented)

    return dico_1, col_commented

# On récupère la liste de requêtes et la liste des colonnes déjà traitées
dico, cc = comment_generator()
print("Sauvegarde des données... A la prochaine ! :) ")


###############################################################################
#                    REECRITURE DU FICHIER HTML                               #
#      DE DOCUMENTATION AVEC AJOUT DE LA DESCRIPTION D'UNE TABLE              #
###############################################################################


def overwrite_desc(dico, base, docpath):
	dico = dico_table_desc
	try:
		tab_temp = upload_nested_dict_pickle("{}_dico_del_simple_desc.pkl".format(base), one_path_desc)
	except:
		tab_temp = []
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
						if liste_page_html_split[desc_index+1] == "<p>{}</p>".format(dico[tab]):
							print("test1")
							pass
						else:
							if tab in tab_temp:
								pass
							else:
								liste_page_html_split[desc_index] = ligne_desc + "<p>{}</p>".format(dico[tab])
								tab_temp.append(tab)
								save_nested_dict_pickle("{}_dico_del_simple_desc.pkl".format(base), tab_temp, one_path_desc)
					else:
						pass
		full_html = "\n".join(liste_page_html_split)
		with open("db_{0}/doc_de_la_base_{0}.html".format(base), "w") as fichier:
			fichier.write(full_html)
		print("Fichier mis à jour !")
		return

overwrite_desc(dico_table_desc, choix_base, "db_{0}/doc_de_la_base_{0}.html".format(choix_base))

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
				nouvel_index_all_cols = i+13
				nouvel_index_one_col = nouvel_index_all_cols+2
				for idx,cc in enumerate(col.items()):
					index_com = nouvel_index_one_col+4
					ligne_com = liste_page_html_split[index_com]
					# Structure permettant d'éviter les doublons
					if liste_page_html_split[index_com] != "<td></td>":
						pass
					else:
						liste_page_html_split[index_com] = ligne_com[:4] + " {}".format(cc[1]) + ligne_com[4:]

					nouvel_index_one_col += 7
					index_com += 7
	full_html = "\n".join(liste_page_html_split)
	with open("db_{0}/doc_de_la_base_{0}.html".format(base), "w") as fichier:
		fichier.write(full_html)
	return dico

# On met à jour le fichier de documentation de la base séléctionnée
dico = overwrite_comments(dico, base, "db_{0}/doc_de_la_base_{0}.html".format(base))