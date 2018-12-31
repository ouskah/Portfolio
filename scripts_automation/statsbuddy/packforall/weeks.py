# Partie à transferer en SQL via le .format(date_debut, date_fin)
import datetime

def date(format="%Y%m%d"):
    return datetime.datetime.utcnow().strftime(format)


date_fin = '2018-{}-{}'.format(date()[4:6], date()[6:8])


# A : trick pour incrémenter les dates et les convertir en str pour le filtrage après
date_int = int(date()) - 7
date_str = str(date_int)

# B : date pour le mois suivant (si date_debut = "30" ou "31") (même logique qu'en A mais en plus rapide)
date_mois_suivant = '{}'.format(int(date()) + 100)

# Conditions pour rendre les dates dynamiques et correctes dans toutes les situations (sauf année ici)
if date_fin[6:8] == '30':
    date_debut = '2018-{}-{}'.format(date_mois_suivant[4:6], ('06'))
    
elif date_fin[6:8] == '31':
    date_debut = '2018-{}-{}'.format(date_mois_suivant[4:6], ('07'))
    
else:
    date_debut = '2018-{}-{}'.format(date_str[4:6], (date_str[6:8]))
    
    
# Test de variables dynamiques d'un mois sur l'autre Variables dynamiques = date_debut et date_fin 
# date_debut = '2018-08-28'
# date_fin = '2018-09-03'


# print(date_debut)
# print(date_fin)


########### Permet de convertir les dates de la période en une phrase synthétique plus lisible ##################################################

liste_mois = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
mois_labs = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "decembre"]

mixmois = [(x,y) for x,y in zip(liste_mois, mois_labs)]

for i, m in enumerate(mixmois):

    if (date_debut[5:7] == date_fin[5:7]) and date_debut[5:7] == m[0]:

        mois_identiques = m[1]
        period_clean = "pour la période du {0} {1} au {2} {1} {3}".format(date_debut[8:10], mois_identiques, date_fin[8:10], date_fin[:4])

    if (date_fin[5:7] != date_debut[5:7]) and date_fin[5:7] == m[0]:

        mois_diff = m[1]
        period_clean = "pour la période du {0} {1} au {2} {3} {4}".format(date_debut[8:10], mixmois[i-1][1], date_fin[8:10], mois_diff, date_fin[:4])

# print(period_clean)
