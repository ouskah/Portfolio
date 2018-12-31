# On import les credentials et modules nécessaires, via notre module updash.py
from updash import *
from packforall.weeks import *
from config import st

##################################################################################################################################################
#                           ETAPE 1 : IMPORT & COMPARAISON DES DONNEES DU SPREADSHEET DE RAPPORT DE PERFORMANCES HEBOMADAIRES                    #
##################################################################################################################################################

def acces_dashboard(credentials):
    """ Fonction permettant de lire les données du spreadsheet 2.
    -Elle compare chaque valeur du spreadsheet et crée un message personnalisé pour chaque tendance rencontrée
    (hausse ou baisse d'un KPI en l'occurrence)
    """
    # On se connecte avec nos logs de Google Cloud Platform
    gc = gspread.authorize(credentials)
    # On ouvre le worksheet selon l'id contenue dans son URL
    spreadsheet_key = ''
    wks = gc.open_by_key(spreadsheet_key)
    # Acceder au fichier spreadsheet
    ws = wks.get_worksheet(0)

    # Pour prendre en compte le pourcentage et le retirer s'il existe
    liste_chaines = [ws.acell('B4').value, ws.acell('C4').value, ws.acell('B19').value,
                     ws.acell('C19').value, ws.acell('B29').value, ws.acell('C29').value,
                     # avant c'était B34 et C34
                     ws.acell('B35').value, ws.acell('C35').value]

    liste_nouvelles_chaines = []

    for chaine in liste_chaines:
        chara = '%'
        if chara in chaine:
            new_chaine = chaine.replace("%", "")
            liste_nouvelles_chaines.append(new_chaine)

    # A partir de cette section on selectionne les valeurs que l'on souhaite comparer à chaque fois

    # TOTAL DES USERS INSCRITS (évolution =  taux de variation)
    tti_comp1 = round(float(liste_nouvelles_chaines[0]),1)
    tti_comp2 = round(float(liste_nouvelles_chaines[1]),1)


    # DDL / WEEK (évolution = taux de variation)
    ddl_comp1 = round(float(liste_nouvelles_chaines[2]),1)
    ddl_comp2 = round(float(liste_nouvelles_chaines[3]),1)


    # WAU = Weekly Active Users (évolution = taux de variation)
    wau_comp1 = round(float(liste_nouvelles_chaines[4]),1)
    wau_comp2 = round(float(liste_nouvelles_chaines[5]),1)


    # Engagement = nombre total d'intéractions (évolution = taux de variation)
    engage_comp1 = round(float(liste_nouvelles_chaines[6]),1)
    engage_comp2 = round(float(liste_nouvelles_chaines[7]),1)


    # Dictionnaire vide qui va contenir nos messages
    messages = {'message_tti': None, 'message_ddl': None, 'message_wau': None, 'message_engage': None, 'message_duo_gagnant': None}

    ############ VERSION 1 : MESSAGE ACTUEL SIMPLE

    # 'switch case like' produisant un message adapté aux statistiques descriptives
    # Les sections if correspondent aux cas des baisses de performances, alors que les else concernent les hausses de perfs réalisées
    if tti_comp1 > tti_comp2:
        message_tti_baisse = '''Nombre total d\'inscrits en baisse : {}% !'''.format(tti_comp2)
        messages['message_tti'] = message_tti_baisse
    else:
        message_tti_hausse = '''Augmentation du nombre total d\'inscrits : {}% !'''.format(tti_comp2)
        messages['message_tti'] = message_tti_hausse

    if ddl_comp1 > ddl_comp2:
        message_ddl_baisse = '''Alerte ! Baisse drastique de {}% des téléchargements hebdomadaires.'''.format(ddl_comp2)
        messages['message_ddl'] = message_ddl_baisse
    else:
        message_ddl_hausse = '''Nice ! Hausse de {}% des téléchargements hebdomadaires.'''.format(ddl_comp2)
        messages['message_ddl'] = message_ddl_hausse

    if wau_comp1 > wau_comp2:
        message_wau_baisse = '''Attention, baisse des Weekly Active Users de {}% !'''.format(wau_comp2)
        messages['message_wau'] = message_wau_baisse
    else:
        message_wau_hausse = '''Cool ! Augmentation des Weekly Active Users de {}% !'''.format(wau_comp2)
        messages['message_wau'] = message_wau_hausse

    if engage_comp1 > engage_comp2:
        message_engage_baisse = '''Nombre total des intéractions en baisse de {}% !'''.format(engage_comp2)
        messages['message_engage'] = message_engage_baisse
    else:
        message_engage_hausse = '''Nombre total des intéractions en hausse de {}% !'''.format(engage_comp2)
        messages['message_engage'] = message_engage_hausse

    # Partie "gamifiée" :
    # 1 - Duo gagnant
    if ((wau_comp1 < wau_comp2) and (engage_comp1 < engage_comp2)):
    	message_duo_gagnant = '''plus d'utilisateurs actifs par semaine (+ {}%) et plus d'intéractions (+ {}%), les astres sont alignés ! '''.format(wau_comp2, engage_comp2)
    	messages['message_duo_gagnant'] = message_duo_gagnant
    # TO DO : inclure d'autres KPIs "gamifiés"

    return messages


############ VERSION 2 : MESSAGE ACTUEL + COMPARAISON AVEC LA PERIODE PRECEDENTE

    # if tti_comp1 > tti_comp2:
    #     message_tti_baisse = '''Nombre total d\'inscrits en baisse : {}% ! Taux précédent : {}%'''.format(tti_comp2, tti_comp1)
    #     messages['message_tti'] = message_tti_baisse
    # else:
    #     message_tti_hausse = '''Augmentation du nombre total d\'inscrits : {}% ! Taux précédent : {}%'''.format(tti_comp2, tti_comp1)
    #     messages['message_tti'] = message_tti_hausse

    # if ddl_comp1 > ddl_comp2:
    #     message_ddl_baisse = '''Alerte ! Baisse drastique de {}% des téléchargements hebdomadaires. Taux précédent : {}%'''.format(ddl_comp2, ddl_comp1)
    #     messages['message_ddl'] = message_ddl_baisse
    # else:
    #     message_ddl_hausse = '''Alerte ! Super hausse de {}% des téléchargements hebdomadaires. Taux précédent : {}%'''.format(ddl_comp2, ddl_comp1)
    #     messages['message_ddl'] = message_ddl_hausse

    # if wau_comp1 > wau_comp2:
    #     message_wau_baisse = '''Attention, baisse des Weekly Active Users de {}% ! Taux précédent : {}%'''.format(wau_comp2, wau_comp1)
    #     messages['message_wau'] = message_wau_baisse
    # else:
    #     message_wau_hausse = '''Cool ! Augmentation des Weekly Active Users de {}% ! Taux précédent : {}%'''.format(wau_comp2, wau_comp1)
    #     messages['message_wau'] = message_wau_hausse

    # if engage_comp1 > engage_comp2:
    #     message_engage_baisse = '''Nombre total des intéractions en baisse de {}% ! Taux précédent : {}%'''.format(engage_comp2, engage_comp1)
    #     messages['message_engage'] = message_engage_baisse
    # else:
    #     message_engage_hausse = '''Nombre total des intéractions en hausse de {}% ! Taux précédent : {}%'''.format(engage_comp2, engage_comp1)
    #     messages['message_engage'] = message_engage_hausse

    # return messages

messages = acces_dashboard(credentials)

##################################################################################################################################################
#                                                  ETAPE 2 : CREATION DU SLACKBOT                                                                #
##################################################################################################################################################

""" Création de notre statsbuddy ! Système d'alerting qui renvoit un message personnalisé en fonction des performances réalisées par des campagnes
marketings.
Options possibles :
- intégration d'emojis aux messages personnalisés
- ajout de pièces jointes aux messages personnalisés (graphiques, liens, etc...)
"""

from slackclient import SlackClient

# Notre liste de messages
liste_messages = messages

# On séléctionne un message à mettre en valeur :

message = "Salut à tous, je suis de retour (avec une bonne nouvelle) on a encore " + liste_messages['message_duo_gagnant'] + " ({})".format(period_clean) + """\n On continue comme ça ! :+1: \n\n
1 - Pour plus d\'infos allez jeter un coup oeil à ce bilan comparatif ! : \n ==> https://docs.google.com/spreadsheets/d/ \n
2 - Pour un rapport plus exhaustif voir le lien suivant : \n ==> https://docs.google.com/spreadsheets/d/ \n\n
Bonne fin de journée ! A la semaine prochaine :) """


def slack_message(message, channel_id):
    token = st
    sc = SlackClient(token)
    sc.api_call('chat.postMessage', channel=channel_id,
                text=message, username='Stats buddy',
                icon_emoji=':un_emoji:')
# N.B :
# Pour voir les messages affichés avant de lancer le bot commenter l'appel slack_message()
# et décommenter celui ci-dessous :
# print(liste_messages)
slack_message(message, channel_id)

# print(messages)

# Liste des channels :
# https://api.slack.com/methods/channels.list/test