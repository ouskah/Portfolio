# Partie à transferer en SQL via le .format(date_debut, date_fin)
import datetime

def date(format="%Y%m%d"):
    return datetime.datetime.utcnow().strftime(format)

# On sélectionne le mois actuel
current_month = date()[4:6]

# On sélectionne le mois dernier
last_month_int = int(current_month) - 1

# On convertit le mois dernier de int to str
last_month = str(last_month_int)


date_fit = '2018-{}-{}'.format(date()[4:6], date()[6:8])

