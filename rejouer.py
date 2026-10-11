"""Rejoue les trois scripts de calcul sur les donnees publiees ici, et compare a resultats/.

Contrat : les chiffres publies sont ceux que le code produit. Le script relance, dans un
dossier temporaire, et dans l'ordre :
  1. calcul/PF_LeTest_TaxeFonciere_calcul.py          -> les pourcentages (tableur + console)
  2. calcul/PF_LeTest_TaxeFonciere_communes_2026.py   -> les euros, commune par commune
  3. calcul/PF_LeTest_TaxeFonciere_communes_2026_pondere.py
                                                      -> le complement pondere par la population,
                                                         calcule sur le CSV REJOUE a l'etape 2
puis compare chaque sortie au fichier publie dans resultats/.

La comparaison ignore les fins de ligne, et seulement elles : un meme script ecrit CRLF sous
Windows et LF sous Linux (pandas, json), et on doit pouvoir rejouer sur l'un comme sur l'autre.
Une seule exception, DITE a l'ecran : un JSON dont les octets different mais dont le CONTENU est
identique (memes cles, memes valeurs ECRITES, listes dans le meme ordre) est accepte. Le tri de pandas
n'est pas stable : l'ordre des ex aequo d'un dictionnaire peut changer selon le processeur (jeu
d'instructions de numpy), sans qu'une seule valeur bouge. Tout autre ecart, d'un seul octet, est
un STOP. Les trois scripts sont publies tels qu'executes le 25/09/2026 : on ne les retouche pas,
leurs empreintes sont consignees (EMPREINTES.json).

Usage :
    python rejouer.py

Codes retour : 0 = FEU VERT, 1 = STOP (une sortie differe du fichier publie), 2 = erreur (un
script echoue, une piece manque, un fichier est illisible) : le controle lui-meme est empeche,
ce n'est pas aux donnees qu'on le reproche.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent
CALCUL = RACINE / "calcul"
DONNEES = RACINE / "donnees"
RESULTATS = RACINE / "resultats"
DELAI_S = 900  # le fichier des tarifs fait 506 284 lignes : quelques secondes, jamais un quart d'heure

# (sortie produite dans le dossier temporaire, fichier publie dans resultats/)
SORTIES = (
    ("PF_LeTest_TaxeFonciere_calcul.csv", "PF_LeTest_TaxeFonciere_calcul.csv"),
    ("calcul_console.txt", "PF_LeTest_TaxeFonciere_calcul_sortie.txt"),
    ("PF_LeTest_TaxeFonciere_communes_2026.csv", "PF_LeTest_TaxeFonciere_communes_2026.csv"),
    ("PF_LeTest_TaxeFonciere_communes_2026_resume.json", "PF_LeTest_TaxeFonciere_communes_2026_resume.json"),
    ("PF_LeTest_TaxeFonciere_communes_2026_pondere.json", "PF_LeTest_TaxeFonciere_communes_2026_pondere.json"),
)


class Empeche(Exception):
    """Le rejeu n'a pas pu aller au bout : ce n'est pas un ecart, c'est un controle empeche."""


def lancer(script: str, *arguments: str, dossier: Path) -> bytes:
    """Lance un script de calcul publie, rend sa sortie console (octets)."""
    chemin = CALCUL / script
    if not chemin.is_file():
        raise Empeche(f"script absent : calcul/{script}")
    try:
        resultat = subprocess.run(
            [sys.executable, str(chemin), *arguments],
            capture_output=True,
            timeout=DELAI_S,
            cwd=dossier,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except (OSError, subprocess.SubprocessError) as erreur:
        raise Empeche(f"calcul/{script} n'a pas pu etre lance : {erreur}") from None
    if resultat.returncode != 0:
        fin = resultat.stderr.decode("utf-8", "replace")[-600:]
        raise Empeche(f"calcul/{script} a echoue (code {resultat.returncode}) :\n{fin}")
    return resultat.stdout


def sans_fins_de_ligne(octets: bytes) -> bytes:
    """CRLF et LF se valent ; rien d'autre n'est neutralise."""
    return octets.replace(b"\r\n", b"\n")


def meme_contenu_json(produit: bytes, publie: bytes) -> bool:
    """Vrai si les deux JSON portent exactement les memes cles et les memes valeurs ECRITES.

    Les nombres sont compares avec leur type et tels qu'ecrits : « 1 », « 1.0 », « true » et le
    texte « "28.69" » ne valent ni l'un l'autre ni 28.69. L'egalite de dictionnaires ignore l'ordre
    des cles, pas celui des listes : seuls l'ordre des ex aequo d'un dictionnaire et la mise en page
    sont donc pardonnes, jamais une valeur ni un ordre de liste.
    """

    def lire(octets: bytes) -> object:
        # chaque nombre lu avec son TYPE et son ecriture : ni 1 = 1.0, ni 28.69 = "28.69" ; un JSON
        # ne produit jamais de tuple, donc aucune collision avec une vraie valeur
        return json.loads(octets.decode("utf-8"), parse_int=lambda s: ("int", s),
                          parse_float=lambda s: ("float", s), parse_constant=lambda s: ("const", s))

    try:
        return lire(produit) == lire(publie)
    except (UnicodeDecodeError, ValueError):
        return False


def rejouer(dossier: Path) -> list[str]:
    """Rejoue les trois scripts dans `dossier`, rend la liste des ecarts (vide = conforme)."""
    console = lancer("PF_LeTest_TaxeFonciere_calcul.py",
                     str(dossier / "PF_LeTest_TaxeFonciere_calcul.csv"), dossier=dossier)
    (dossier / "calcul_console.txt").write_bytes(console)
    lancer("PF_LeTest_TaxeFonciere_communes_2026.py", str(DONNEES), str(dossier), dossier=dossier)
    lancer("PF_LeTest_TaxeFonciere_communes_2026_pondere.py", str(DONNEES), str(dossier), dossier=dossier)

    ecarts = []
    for produit, publie in SORTIES:
        chemin_produit, chemin_publie = dossier / produit, RESULTATS / publie
        if not chemin_publie.is_file():
            raise Empeche(f"fichier publie absent : resultats/{publie}")
        if not chemin_produit.is_file():
            raise Empeche(f"le rejeu n'a pas produit {produit}")
        octets_produit = sans_fins_de_ligne(chemin_produit.read_bytes())
        octets_publie = sans_fins_de_ligne(chemin_publie.read_bytes())
        if octets_produit == octets_publie:
            print(f"OK        resultats/{publie}")
        elif publie.endswith(".json") and meme_contenu_json(octets_produit, octets_publie):
            print(f"OK        resultats/{publie}  (ordre des ex aequo different, valeurs identiques)")
        else:
            ecarts.append(f"ECART     resultats/{publie}")
    return ecarts


def main() -> int:
    # La ligne ERREUR relaie le stderr d'un script enfant tel quel : jamais de plantage d'affichage
    # sur une console qui ne sait pas l'ecrire.
    for flux in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            flux.reconfigure(errors="backslashreplace")
    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as provisoire:
            ecarts = rejouer(Path(provisoire))
    except Empeche as erreur:
        print(f"ERREUR : {erreur}", file=sys.stderr)
        return 2
    except OSError as erreur:
        print(f"ERREUR : lecture ou ecriture impossible pendant le rejeu : {erreur}", file=sys.stderr)
        return 2
    except Exception as erreur:  # tout imprevu empeche le controle : code 2, jamais le 1 du STOP
        print(f"ERREUR imprevue pendant le rejeu ({type(erreur).__name__}) : {erreur}", file=sys.stderr)
        return 2
    if ecarts:
        print()
        for ecart in ecarts:
            print(ecart)
        print(f"\nSTOP : {len(ecarts)} sortie(s) sur {len(SORTIES)} ne redonnent pas le fichier publie.")
        return 1
    print(f"\nFEU VERT : les {len(SORTIES)} sorties rejouees redonnent les fichiers publies (fins de "
          "ligne mises a part ; pour un JSON, ordre des ex aequo mis a part, dit ci-dessus s'il a joue).")
    return 0


if __name__ == "__main__":
    try:
        code_retour = main()
    except Exception as erreur:  # tout imprevu, affichage compris : controle empeche, code 2
        with contextlib.suppress(Exception):
            print(f"ERREUR imprevue ({type(erreur).__name__}) : {erreur}", file=sys.stderr)
        code_retour = 2
    sys.exit(code_retour)
