# Fréquence des verbes à particule (15 novembre 2026)

Script : `tools/passe_frequence_vap.py` (méthode en tête du fichier).
Données : `frequency_bigramdictionary_en_243_342.txt`, fourni avec le paquet PyPI symspellpy
(`pip download symspellpy --no-deps`, puis extraire le .whl).

    python3 tools/passe_frequence_vap.py <bigrams.txt>           # simulation, écrit changements.json
    python3 tools/passe_frequence_vap.py <bigrams.txt> --apply   # applique et enregistre vocab.xlsx

`changements.json` garde l'ancien et le nouveau Zipf / Fréq de chaque ligne modifiée.
