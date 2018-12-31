""" Fonctions de calculs statistiques """

# Calculer un taux de variation arrondi à la deuxième décimale
taux_variation = lambda va,vd: round(((va - vd) / vd) * 100, 2)

# Calculer un ratio arrondi à une décimale
ratio = lambda x,y: round((x / y), 1)

# Proportion de users qui n'ont réalisés aucunes intéractions
""" a = nb users ayants réalisés au moins une intéraction
    b = nb total de users actifs par semaine (Weekly Active Users)
"""
p_users = lambda a,b: round(100 - (a / b) * 100)

# Proportion des inscrits par rapport aux installs
""" a = nb d'inscrits
    b = nb d'installs
"""
p_inscrits_installs = lambda a,b: round((a / b) * 100, 0)