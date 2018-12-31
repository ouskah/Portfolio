from config import gcpt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(gcpt, scope)

def maj_dashboard(credentials):
	""" Fonction permettant de mettre à jour le spreadsheet comparatif intermédiaire """ 
    gc = gspread.authorize(credentials)
    # Acceder au spreadsheet 1
    spreadsheet_key_1 = ''
    wks1 = gc.open_by_key(spreadsheet_key_1)
    ws1 = wks1.get_worksheet(0)
    # Acceder au spreadsheet 2
    spreadsheet_key_2 = ''
    wks2 = gc.open_by_key(spreadsheet_key_2)
    ws2 = wks2.get_worksheet(0)
    # Liste des colonnes en fonction de la valeur de la 3ème row
    liste_colonnes = ws1.range('B3:I3')
    # Labels des colonnes
    col_labels = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    # Index
    col_index = [2,3,4,5,6,7,8,9]
    # On définit les variables qui stockeront les labels de last and before_last columns
    last_col_lab = None
    before_last_col_lab = None
    # Boucle qui permet de récupérer le label de la dernière colonne et de l'avant dernière du rapport
    # de manière actualisée
    for i, x, y in zip(col_index, liste_colonnes, col_labels):
        if x.value == "":
            before_last_col_lab = col_labels[i-4]
            last_col_lab = col_labels[i-3]
            break
        else:
            pass
    # Etape 1 : On selectionne les colonnes before/after du spreadsheet 1
    cell_list_ws1_before = ws1.range('{0}3:{0}40'.format(before_last_col_lab))
    cell_list_ws1_after = ws1.range('{0}3:{0}40'.format(last_col_lab))
    # Etape 2 : On selectionne les colonnes before(B)/after(C) du spreadsheet 2
    cell_list_ws2_before = ws2.range('B3:B40')
    cell_list_ws2_after = ws2.range('C3:C40')

    # Mise à jour du second spreadsheet
    for x, y in zip(cell_list_ws1_before, cell_list_ws2_before):
        y.value = x.value
        for x1, y1 in zip(cell_list_ws1_after, cell_list_ws2_after):
            y1.value = x1.value
    ws2.update_cells(cell_list_ws2_before)
    ws2.update_cells(cell_list_ws2_after)
    # Debugging (on renvoie l'avant dernière et la dernière colonne)
    return #before_last_col_lab, last_col_lab

maj_dashboard(credentials)