from config import *

import pandas as pd
import pymysql.cursors

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from packforall.statsfonctions import *

###################################################################################################
#            ETAPE 1 : EXTRACTIONS DE DONNEES VIA AUTOMATISATION DES REQUETES SQL                 #
###################################################################################################

def week_extract(datetime1, datetime2):
    """ Fonction permettant d'automatiser la réalisation de requêtes SQL vers 1 ou plusieurs
    database(s)
    - datetime1 = la première partie de l'intervalle de temps sélectionné (sous format str)
    - datetime2 = la seconde partie de l'intervalle de temps sélectionné (sous format str)
    """
    
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
            # Pour chaque requête on l'exécute et stock le résultat dans la liste nb_all
            for sql in sql_all:
                cursor.execute(sql)
                result = cursor.fetchone()
                nb_all_db_1.append(list(result.values())[0])

    # On clôture la session
    finally:
        connection.close()

    # On créer le dataframe de la première database
    df_db_1 = pd.DataFrame({x:y for x,y in zip(liste_labels_db_1, nb_all_db_1)}, index=['resultats'])


    #------------------------------  Deuxième database -----------------------------------------------

    # On crée ici une liste qui regroupe les variables que l'on souhaite requêter
    liste_labels_db_2 = ['download par semaine', 'iOS', 'Android', 'download organique',
                       'inscriptions par semaine', 'desinscriptions par semaine',
                       'Weekly Active Users', 'sessions', 'engagement(nb interactions)',
                       'nombre de users avec au moins une interaction']
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
            # Exemples de requêtes réalisées (ici anonymisées)
            sql_all2 = [
                ### Download par semaine
                """ SELECT COUNT(*) FROM {0}.nom_table AS t1
                WHERE t1.nom_colonne_1 BETWEEN {1} AND {2}
                AND t1.nom_colonne_2 = 'nom_valeur' """.format(db_2, datetime1, datetime2),

                ### Download iOS
                """SELECT COUNT(*) FROM {0}.nom_table AS t1
                WHERE t1.nom_colonne_1 BETWEEN {1} AND {2}
                AND t1.nom_colonne_2 = nom_valeur
                AND t1.nom_colonne_3 LIKE 'nom_valeur' """.format(db_2, datetime1, datetime2),
                # etc ....
            ]
            for sql in sql_all2:
                cursor.execute(sql)
                result = cursor.fetchone()
                nb_all_db_2.append(round(list(result.values())[0]))

    finally:
        connection2.close()

    # On créer le dataframe de la Database 2
    df_db_2 = pd.DataFrame({x:y for x,y in zip(liste_labels_db_2, nb_all_db_2)}, index=['resultats'])

    return df_db_1, df_db_2

df1, df2 = week_extract(datetime1, datetime2)

###################################################################################################
#            ETAPE 2 : REMPLISSAGE AUTOMATIQUE DU GOOGLE SPREADSHEET HEBDOMADAIRE                 #
###################################################################################################

def write_weekly_report(df1, df2):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gcpt, scope)

    gc = gspread.authorize(credentials)
    # Ouverture du spreadsheet via sa clef
    spreadsheet_key = ''
    wks = gc.open_by_key(spreadsheet_key)

    # Acceder au spreadsheet
    ws = wks.get_worksheet(0)

    col_labels = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

    liste_colonnes = ws.range('B3:I3')

    # Index
    col_index = [2,3,4,5,6,7,8,9]

    # On définit les variables qui stockeront les labels de last and before_last columns
    last_col_lab = None
    before_last_col_lab = None

    # Boucle qui permet de récupérer le label de la dernière colonne et de l'avant dernière du rapport
    # de manière actualisée
    for i, x, y in zip(col_index, liste_colonnes, col_labels):
        if x.value == "":
            before_last_col_lab = col_labels[i-3]
            last_col_lab = col_labels[i-2]
            break
        else:
        	pass

    all_cell_wanted = ['11', '12', '13', '18', '24', '25', '28', '30', '33', '38']

    all_cell_wanted_2 = ["{0}{1}".format(last_col_lab, number) for number in all_cell_wanted]

    ct_index = [x for x in range(0, len(df2.columns))]

#######################################################################################################

    # Complete values
    ws.update_acell('{}3'.format(last_col_lab), str(df1.loc['resultats'][0]))
    ws.update_acell('{}15'.format(last_col_lab), 'NA')
    ws.update_acell('{}21'.format(last_col_lab), '0')

    # Evolution 1
    val1 = ws.acell('{}3'.format(before_last_col_lab)).value # D3
    val1_opti = ''.join(val1.split())
    ws.update_acell('{}4'.format(last_col_lab), "{}%".format(str(taux_variation(df1.loc['resultats'][0], int(val1_opti)))))

    # Evolution 2
    val2 = ws.acell('{}18'.format(before_last_col_lab)).value # D18
    val2_opti = ''.join(val2.split())
    ws.update_acell('{}19'.format(last_col_lab), "{}%".format(str(taux_variation(df2['download organique'][0], int(val2_opti)))))

    # Evolution 3
    val3 = ws.acell('{}33'.format(before_last_col_lab)).value # D33
    val3_opti = ''.join(val3.split())
    ws.update_acell('{}34'.format(last_col_lab), "{}%".format(str(taux_variation(df2['engagement(nb interactions)'][0], int(val3_opti)))))

    # Part inscrits/installs
    ws.update_acell('{}26'.format(last_col_lab), "{}%".format(p_inscrits_installs(int(df2['inscriptions par semaine'][0]),
                        int(df2['download par semaine'][0]))))

    # Ratio session/user
    ws.update_acell('{}31'.format(last_col_lab), "{}%".format(ratio(int(df2['sessions'][0]), int(df2['Weekly Active Users'][0]))))

    # Ratio intéractions/sessions
    ws.update_acell('{}35'.format(last_col_lab), "{}%".format(ratio(int(df2['engagement(nb interactions)'][0]), int(df2['sessions'][0]))))

    # Ratio intéractions/users
    ws.update_acell('{}36'.format(last_col_lab), "{}%".format(ratio(int(df2['engagement(nb interactions)'][0]), int(df2['Weekly Active Users'][0]))))


    # Proportion de users qui n'ont réalisés aucunes intéractions
    ws.update_acell('{}39'.format(last_col_lab),
                    "{}%".format(
                        p_users(int(df2['nombre de users avec au moins une interaction'][0]),
                        int(df2['Weekly Active Users'][0]))))

    for cell,i in zip(all_cell_wanted_2, ct_index):
        ws.update_acell(cell, str(df2.loc['resultats'][i]))

    return

write_weekly_report(df1, df2)
