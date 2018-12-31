from config import *

import pandas as pd
import pymysql.cursors

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from packforall.mois import *
from packforall.statsfonctions import *

###################################################################################################
#            ETAPE 1 : EXTRACTIONS DE DONNEES VIA AUTOMATISATION DES REQUETES SQL                 #
###################################################################################################

def month_extract(date=last_month):
    # -------------------------  Première database ------------------------------------------------

    # On crée ici une liste qui regroupe les variables que l'on souhaite requêter
    liste_labels_db_1 = ['total inscrits']
    # On crée une deuxième liste vide qui va contenir les réponses à nos questions
    nb_all_db_1 = []
    # On se connecte à la première database
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                db=db_1,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # On crée ici notre liste de requêtes à envoyer à la base
            sql_all = [
            "SELECT COUNT(*) FROM {}.nom_table ".format(db_1),
            ]
            # Pour chaque requête on l'exécute et stock le résultat dans la liste nb_all_db_1
            for sql in sql_all:
                cursor.execute(sql)
                result = cursor.fetchone()
                nb_all_db_1.append(list(result.values())[0])
    # On cloture la session
    finally:
        connection.close()

    # On créer le dataframe de la database 1
    df_db_1 = pd.DataFrame({x:y for x,y in zip(liste_labels_db_1, nb_all_db_1)}, index=['resultats'])

    #------------------------------  Deuxième database -----------------------------------------------

    # On crée ici une liste qui regroupe les variables que l'on souhaite requêter
    liste_labels_db_2 = ['download par mois', 'iOS', 'Android', 'inscriptions par mois',
                         'desinscriptions par mois', 'Monthly Active Users', 'sessions']
    # On crée une deuxième liste vide qui va contenir les réponses à nos questions
    nb_all_db_2 = []

    # On se connecte à la deuxième database
    connection2 = pymysql.connect(host=host,
                            user=user,
                            password=password,
                            db=db_2,
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection2.cursor() as cursor:
            # Exemples de requêtes réalisées (ici anonymisées comme pour le script spreadweek.py) 
            sql_all2 = [
                ### Inscriptions par mois

                """SELECT COUNT(*) FROM {0}.nom_table AS t1
                WHERE MONTH(t1.nom_colonne_1) = {1}
                AND t1.nom_colonne_2 = 'nom_valeur' """.format(db_2, last_month),

                ### Desinscriptions par mois

                """SELECT COUNT(*) FROM {0}.nom_table AS t1
                WHERE MONTH(t1.nom_colonne_1) = {1}
                AND t1.nom_colonne_2 = 'nom_valeur' """.format(db_2, last_month),
                # etc...

                ]

            for sql in sql_all2:
                cursor.execute(sql)
                result = cursor.fetchone()
                nb_all_db_2.append(round(list(result.values())[0]))

    finally:
        connection2.close()


    # On créer le dataframe de la database 2
    df_db_2 = pd.DataFrame({x:y for x,y in zip(liste_labels_db_2, nb_all_db_2)},
                                       index=['resultats'], columns=liste_labels_db_2)

    # On renvoie nos deux dataframes
    return df_db_1, df_db_2

df1, df2 = month_extract(last_month)


###################################################################################################
#            ETAPE 2 : ECRITURE AUTOMATISEE DU GOOGLE SPREADSHEET MENSUEL                         #
###################################################################################################


def write_month_report(df1, df2):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gcpt, scope)

    gc = gspread.authorize(credentials)
    # Ouverture du spreadsheet via sa clef
    spreadsheet_key = ''
    wks = gc.open_by_key(spreadsheet_key)

    # liste des feuilles du worksheet
    worksheet_list = wks.worksheets()

    # 2 variables permettant de lier les mois avec les index des feuilles du spreadsheet
    liste_mois = ['08', '09', '10', '11', '12']
    liste_sheets = [1, 2, 3, 4, 5]

    selecte_column = 'G'

    for num_mois, sheet in zip(liste_mois, liste_sheets):
        if current_month == num_mois:
            if len(worksheet_list) > 1:
                # On selectionne la feuille précedente
                try:
                    ws_before = wks.get_worksheet(sheet-1)
                except:
                    # Si pas de sheet précédente on sélectionne par défaut la première sheet
                    ws_before = wks.get_worksheet(0)
                # On sélectionne la sheet du mois actuel
                ws = wks.get_worksheet(sheet)

                # On remplit la colonne E par les valeurs du mois précédent

                ######################################################
                # On selectionne les valeurs du mois précédent
                cell_list_before = ws_before.range('G1:G41')

                # On selectionne les valeurs du mois actuel
                cell_list_last = ws.range('E1:E41')

                # Permutation => On affecte à la colonne E du mois actuel,
                # les valeurs de la colonne G du mois précédent
                for before, now in zip(cell_list_before, cell_list_last):
                    now.value = before.value
                ######################################################

                # On met à jour la colonne E du mois actuel
                ws.update_cells(cell_list_last)


    # modifier les valeurs (par colonne)
    list_nb = [7, 8, 9, 10, 11, 20, 21]

    # print le nombre d'utilisateurs
    ws.update_acell('{}6'.format(selecte_column), str(df1.loc['resultats'][0]))

    all_cell_wanted = ["{}{}".format(selecte_column,x) for x in list_nb]
    ct_index = [x for x in range(0, len(df2.columns))]

    # Ratio session/MAU
    ws.update_acell('{}22'.format(selecte_column), "{}".format(ratio(int(df2['sessions'][0]),
                    int(df2['Monthly Active Users'][0]))))

    for cell,i in zip(all_cell_wanted, ct_index):
        ws.update_acell(cell, str(df2.loc['resultats'][i]))

    # B étant la deuxième colonne (que l'on vient de modifier) on affiche ces values (type = list)
    values_list = ws.col_values(9)

    return #values_list

write_month_report(df1, df2)
