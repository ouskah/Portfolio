# Module permmettant la manipulation des datas (import CSV & construction de dataframes)
import pandas as pd
# Module permettant de réaliser les call API (ici vers l'API GRAPH de facebook)
import requests
# Module permettant de paralléliser la fonction principale d'écriture sur le spreadsheet 
from multiprocessing.dummy import Pool as ThreadPool 
# Module permettant de manipuler des Google sheets (via Google Cloud Platform)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# Import des variables tfbp et gcpt
from config import tfbp, gcpt

#############################################################################################################################
#                        PARTIE 1 : Data classification (construction des KPI)                                              #
#############################################################################################################################

# L'extraction se fait via facebook for developers (Créer une app et un jeton d'accès de Page)
token_de_page = tfbp

#---------------- Partie où l'on défini les KPI que l'on souhaite extraire --------------------------

# La liste des KPI (et des paramètres de timelines) disponibles via call API  
# Voir le lien suivant => https://developers.facebook.com/docs/graph-api/reference/v3.2/insights

# I - Listes des KPI (une pour les posts et une pour les vidéos) 
liste_kpi_labels_posts = [
# A - Partie posts
# Portée (total)
'page_posts_impressions',
'page_posts_impressions_paid',
'page_posts_impressions_organic',
# Portée (unique)
'page_posts_impressions_unique',
'page_posts_impressions_paid_unique',
'page_posts_impressions_organic_unique',
# Nombre total d'intéractions : (like + commentaires + partages)
'page_post_engagements',
# Nombre de clics sur un lien
'page_consumptions_by_consumption_type', 
# Autre KPI possible : 'page_engaged_users' 
# => Nombre de personnes qui interagissent avec votre Page. L’interaction comprend tout type de clic.
]

liste_kpi_labels_videos = [
# B - Partie vidéos
# Nombre de vues 3s (total)
'page_video_views',
'page_video_views_paid',
'page_video_views_organic',
# Nombre de vues 3s (unique)
'page_video_views_unique',
# Nombre de vue 10s (total / unique)
'page_video_views_10s',
'page_video_views_10s_paid',
'page_video_views_10s_organic',
# Nombre de vue 10s (unique)
'page_video_views_10s_unique',
# Nombre de clicks sur une vidéo
'page_consumptions_by_consumption_type',
]

liste_kpi_resultats_posts = []

liste_kpi_resultats_videos = []

# II - Configuration des options temporelles

# Option 1 = déterminer une période ciblée via des datetime
date_periode_since_until = 'since=2018-12-02&until=2018-12-10'

# Option 2 = se baser sur une période preétablie (1 semaine) pour alimenter un cron hebdomadaire par exemple
date_periode_preset = 'date_preset=last_7d'


def extract_kpi_posts(kpi):
	""" Fonction pour les posts permettant d'automatiser les call API via le module request """
	# Construction de l'URL vers 1 KPI ciblé :
	# - On peut ici définir la métrique qui nous intéresse après la partie insights de l'URL
	# - On peut aussi cibler une période de temps précise en l'ajoutant juste après la métrique que l'on a choisi 
    #  (sans oublier le "?" qui fait la liaison)
	url_kpi = "https://graph.facebook.com/v3.2/430621253640291/insights/{0}?{1}&access_token={2}".format(kpi,
                                                                                                         date_periode_since_until,
                                                                                                         token_de_page)
	# Réalisation d'un call vers 1 KPI ciblé
	request_kpi = requests.get(url_kpi).json()
	# Crée une boucle via list comprehension et sum les valeurs
	if kpi == 'page_consumptions_by_consumption_type':
		kpi_extracted = sum([x['value']['link clicks'] for x in request_kpi['data'][0]['values']])
	else:
		kpi_extracted = sum([x['value'] for x in request_kpi['data'][0]['values']])
	return kpi_extracted


def extract_kpi_video(kpi):
	""" Fonction pour les vidéos permettant d'automatiser les call API via le module request """
	# Construction de l'URL vers 1 KPI ciblé
	url_kpi = "https://graph.facebook.com/v3.2/430621253640291/insights/{0}?{1}&access_token={2}".format(kpi,
                                                                                                         date_periode_since_until,
                                                                                                         token_de_page)
	# Premier call vers 1 KPI ciblé
	request_kpi = requests.get(url_kpi).json()
	# Crée une boucle via list comprehension et sum les valeurs
	if kpi == 'page_consumptions_by_consumption_type':
		kpi_extracted = sum([x['value']['video play'] for x in request_kpi['data'][0]['values']])
	else:
		kpi_extracted = sum([x['value'] for x in request_kpi['data'][0]['values']])
	return kpi_extracted


# Première boucle pour les KPI des posts
for kpi_label_p in liste_kpi_labels_posts:
	kpi_extracted_p = extract_kpi_posts(kpi_label_p)
	liste_kpi_resultats_posts.append(kpi_extracted_p)
# Deuxième boucle pour les KPI des vidéos
for kpi_label_vid in liste_kpi_labels_videos:
	kpi_extracted_vid = extract_kpi_video(kpi_label_vid)
	liste_kpi_resultats_videos.append(kpi_extracted_vid)

# Premier dataframe pour les KPI des posts
df_kpis_p = pd.DataFrame({x:y for x,y in zip(liste_kpi_labels_posts, liste_kpi_resultats_posts)}, index=['kpis'])
# Deuxième dataframe pour les KPI des vidéos
df_kpis_vid = pd.DataFrame({x:y for x,y in zip(liste_kpi_labels_videos, liste_kpi_resultats_videos)}, index=['kpis'])
# print(df_kpis_p)
# print(df_kpis_vid)

################################################################################################################################
#                                   PARTIE 2 : ECRITURE SUR LE GOOGLE SPREADSHEET                                              #
################################################################################################################################

def write_weekly_fb_report(df_kpis):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(gcpt, scope)
    # Connexion
    gc = gspread.authorize(credentials)
    # Accèder au spreadsheet par sa clef : 
    # (définie dans l'url du spreadsheet après la partie suivante : https://docs.google.com/spreadsheets/d/LA_CLEF/...)
    spreadsheet_key = ''
   	# Ouverture du spreadsheet via sa clef
    wks = gc.open_by_key(spreadsheet_key)
    # Acceder au spreadsheet
    ws = wks.get_worksheet(0)
    # Ajouter les lettres des colonnes du spreadsheet qui correspondent au segment temporel que l'on souhaite retracer 
    # (exemple : de décembre à juillet)
    col_labels = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    # Sélection de la rangée de colonnes qui nous intéressent pour maintenir le script ( = correspond au segment temporel choisi)
    liste_colonnes = ws.range('B3:I3')
    # Indexation
    col_index = [int(i+2) for i, x in enumerate(col_labels)]
    # On définit les variables qui stockeront les labels de last and before_last columns
    last_col_lab = None
    before_last_col_lab = None
    # Boucle qui permet de récupérer le label de la dernière colonne et de l'avant dernière du rapport de manière actualisée
    for i, x, y in zip(col_index, liste_colonnes, col_labels):
        # Condition permettant de calculer les taux de variations et de vérifier que l'on puisse continuer à écrire sur le spreadsheet
        if x.value == "":
            before_last_col_lab = col_labels[i-3]
            last_col_lab = col_labels[i-2]
            break
        else:
            pass
    # Cellules correspondants aux KPI dont on souhaite automatiser l'écriture 
    # (dépend ici de deux dataframes différents, un pour les posts et un pour les vidéos)
    # N.B => Ne pas oublier d'actualiser les numéros des cellules des deux listes suivantes 
    # lorsque le spreadsheet subit des modifications directes via Google drive
    if df_kpis is df_kpis_p:
    	all_cell_wanted = ['3', '5', '6', '8', '10', '11', '13', '18']
    elif df_kpis is df_kpis_vid:
    	all_cell_wanted = ['22', '24', '25', '27', '29', '31', '32', '34', '36']
    else:
    	print("Dataframe incorrect !")

    all_cell_wanted_2 = ["{}{}".format(last_col_lab, number) for number in all_cell_wanted]

    ct_index = [x for x in range(0, len(df_kpis.columns))]
         
    for cell,i in zip(all_cell_wanted_2, ct_index):
        ws.update_acell(cell, str(df_kpis.loc['kpis'][i]))
    # Debugging (au cas où l'impression se ferait dans une mauvaise colonne par exemple)
    return #before_last_col_lab

# Liste qui regroupe nos dataframes
dfs = [df_kpis_p, df_kpis_vid]
# Pool de threads qui utilisent 3 cores
pool = ThreadPool(3) 
# On multithread l'écriture sur le spreadsheet
results = pool.map(write_weekly_fb_report, dfs)
# Fermeture des threads
pool.close() 
pool.join()