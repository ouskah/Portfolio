# Module permettant de parser des arguments via terminal
import argparse
# Module permettant d'estimer le genre d'un individu à partir de son prénom (cf https://pypi.org/project/gender-guesser/)
import gender_guesser.detector as gender
# Module permettant de mesurer le temps d'exécution du script
import time

# Initialisation d'un premier point d'ancrage temporel
start = time.time()
# Création et ajout d'un argument à parser via le terminal
parser = argparse.ArgumentParser()
parser.add_argument('prenom', type=str)
args = parser.parse_args()
# Appel de la class Detector du module gender_guesser (on spécifie ici que les prénoms ne sont pas sensibles à la case)
d = gender.Detector(case_sensitive=False)

def fix_gender(name):
    """ Fonction permettant d'estimer le genre d'un individu à partir de son prénom """
    genre = d.get_gender(u"{}".format(name))
    
    if genre in ['male', 'mostly_male']:
        gender_value = 1
    elif genre in ['female', 'mostly_female']:
        gender_value = 0
    else:
        gender_value = 'NULL'
    
    return gender_value

x = fix_gender(args.prenom)
# On affiche le retour de la fonction dans le terminal
print(x)
# On affiche le temps d'exécution du script : il est ici nettement inférieur à 500 ms (~aux alentours de 300ms)
print('Temps d\'exécution : {0:0.3f} seconds'.format(time.time() - start))
