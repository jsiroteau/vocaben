"""Suite de la passe « formes admises » : traitement des synonymes signalés (passes/admis/signalements.md).

    python3 tools/passe_suite.py next        réserve la tranche suivante et affiche ses lots ;
                                             EN COURS si une tranche est réservée depuis moins de 2 h ; TERMINÉ s'il n'en reste pas
    python3 tools/passe_suite.py done <t>    marque la tranche faite
Les tranches se traitent une à la fois (vocab.xlsx est un fichier binaire : pas d'exécutions en parallèle).
"""
import json
import sys
import time

ETAT = 'passes/admis/etat_suite.json'
TRANCHES = {'A': 'lots 1 à 6', 'B': 'lots 7 à 12', 'C': 'lots 13 à 18', 'D': 'lots 19 à 24'}

try:
    etat = json.load(open(ETAT))
except FileNotFoundError:
    etat = {t: {'etat': 'à faire'} for t in TRANCHES}


def save():
    json.dump(etat, open(ETAT, 'w'), ensure_ascii=False, indent=1)


if sys.argv[1] == 'next':
    now = time.time()
    busy = [t for t, v in etat.items() if v['etat'] == 'en cours' and now - v.get('debut', 0) < 7200]
    todo = [t for t, v in etat.items() if v['etat'] != 'fait' and t not in busy]
    if busy:
        print('EN COURS')
    elif not todo:
        print('TERMINÉ')
    else:
        etat[todo[0]] = {'etat': 'en cours', 'debut': now}
        save()
        print(todo[0], ':', TRANCHES[todo[0]])
elif sys.argv[1] == 'done':
    etat[sys.argv[2]] = {'etat': 'fait'}
    save()
    print('reste :', [t for t, v in etat.items() if v['etat'] != 'fait'] or 'rien')
