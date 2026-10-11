"""Verifie que les pieces du depot sont bit pour bit celles dont l'empreinte est publiee.

Contrat : le manifeste `EMPREINTES.json` fait foi. Chaque entree = un chemin relatif a la
racine du depot + son SHA-256. Le script recalcule, compare, et refuse de conclure sur ce
qu'il n'a pas lu : un fichier manquant est une ERREUR, jamais un succes silencieux.

C'est la piece qui rend le reste verifiable. Sans elle, << les chiffres publies sont ceux
que le code produit >> reste une phrase.

Usage :
    python verifier_empreintes.py                      # verifie tout le manifeste
    python verifier_empreintes.py --manifeste X.json   # autre manifeste
    python verifier_empreintes.py --ecrire             # RECALCULE et reecrit le manifeste

Sortie console en ASCII. Codes retour : 0 = FEU VERT, 1 = STOP (au moins un ecart),
2 = erreur fichier (manifeste illisible ou mal forme, chemin sorti du depot, fichier
illisible pendant le hachage). La distinction compte : un 1 accuse les donnees d'avoir
bouge, un 2 dit que c'est le controle lui-meme qui est empeche.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
MANIFESTE_PAR_DEFAUT = RACINE / "EMPREINTES.json"
TAILLE_BLOC = 1 << 20  # 1 Mio : on ne charge pas un fichier entier en memoire
FORME_SHA256 = re.compile(r"[0-9a-fA-F]{64}")


def empreinte(chemin: Path) -> str:
    """SHA-256 du fichier, lu par blocs."""
    condensat = hashlib.sha256()
    with chemin.open("rb") as fichier:
        for bloc in iter(lambda: fichier.read(TAILLE_BLOC), b""):
            condensat.update(bloc)
    return condensat.hexdigest()


def resoudre(relatif: str) -> Path:
    """Chemin absolu d'une entree du manifeste, refuse tout ce qui sort du depot."""
    if Path(relatif).is_absolute():
        raise ValueError(f"chemin absolu interdit dans le manifeste : {relatif}")
    chemin = (RACINE / relatif).resolve()
    if not chemin.is_relative_to(RACINE):
        raise ValueError(f"chemin hors du depot : {relatif}")
    return chemin


def charger(manifeste: Path) -> dict[str, str]:
    """Lit le manifeste. Tout ce qui n'est pas un manifeste valide est une ERREUR FICHIER.

    Un manifeste casse ne doit jamais ressortir en << ecart >> : ce serait accuser les
    donnees d'avoir bouge alors que c'est le controle qui est abime.
    """
    donnees = json.loads(manifeste.read_text(encoding="utf-8"))
    if not isinstance(donnees, dict):
        raise ValueError("le manifeste n'est pas un objet JSON")
    pieces = donnees.get("pieces")
    if not isinstance(pieces, dict) or not pieces:
        raise ValueError("le manifeste ne contient aucune piece sous la cle 'pieces'")
    normalisees: dict[str, str] = {}
    for relatif, valeur in pieces.items():
        if not isinstance(valeur, str) or not FORME_SHA256.fullmatch(valeur):
            raise ValueError(f"empreinte illisible pour {relatif} : {valeur!r}")
        normalisees[relatif] = valeur.lower()
    return normalisees


def verifier(pieces: dict[str, str]) -> list[str]:
    """Retourne la liste des ecarts constates (vide = tout concorde)."""
    ecarts: list[str] = []
    for relatif, attendu in sorted(pieces.items()):
        chemin = resoudre(relatif)
        if not chemin.is_file():
            ecarts.append(f"MANQUANT  {relatif}")
            continue
        obtenu = empreinte(chemin)
        if obtenu != attendu.lower():
            ecarts.append(f"ECART     {relatif}\n            attendu {attendu}\n            obtenu  {obtenu}")
        else:
            print(f"OK        {relatif}")
    return ecarts


def ecrire(manifeste: Path, pieces: dict[str, str]) -> list[str]:
    """Recalcule les empreintes des chemins deja listes et reecrit le manifeste.

    Retourne la liste des entrees dont l'empreinte change. Sur un depot de preuve, un
    --ecrire lance par megarde effacerait la trace d'une alteration : il doit DIRE ce
    qu'il change. L'ecriture passe par un .tmp puis un remplacement, pour qu'une
    interruption ne laisse jamais un manifeste mutile.
    """
    recalculees = {}
    for relatif in sorted(pieces):
        chemin = resoudre(relatif)
        if not chemin.is_file():
            raise FileNotFoundError(f"piece absente, rien n'est reecrit : {relatif}")
        recalculees[relatif] = empreinte(chemin)

    changements = [
        f"{relatif} : {pieces[relatif]} -> {nouvelle}"
        for relatif, nouvelle in recalculees.items()
        if pieces[relatif] != nouvelle
    ]

    donnees = json.loads(manifeste.read_text(encoding="utf-8"))
    donnees["pieces"] = recalculees
    texte = json.dumps(donnees, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    provisoire = manifeste.with_name(manifeste.name + ".tmp")
    try:
        # newline="\n" impose : sans lui, Windows ecrit des CRLF et Linux des LF, et le
        # meme --ecrire produirait deux fichiers differents selon la machine. Sur un depot
        # dont tout l'objet est l'exactitude a l'octet, l'outil de controle doit etre le
        # premier a etre deterministe. Attrape par la CI Ubuntu au 1er run du depot
        # pilote-finance-cac40-ia (24/08/2026), d'ou cet outil est repris a l'identique, hors
        # ce commentaire.
        with provisoire.open("w", encoding="utf-8", newline="\n") as flux:
            flux.write(texte)
        provisoire.replace(manifeste)
    except BaseException:
        provisoire.unlink(missing_ok=True)
        raise
    return changements


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Verifie les empreintes SHA-256 publiees dans EMPREINTES.json."
    )
    analyseur.add_argument("--manifeste", default=str(MANIFESTE_PAR_DEFAUT))
    analyseur.add_argument(
        "--ecrire",
        action="store_true",
        help="recalcule et reecrit le manifeste (a n'utiliser que volontairement)",
    )
    arguments = analyseur.parse_args(argv)

    manifeste = Path(arguments.manifeste)
    try:
        pieces = charger(manifeste)
    except (OSError, ValueError, json.JSONDecodeError) as erreur:
        print(f"ERREUR FICHIER : {erreur}", file=sys.stderr)
        return 2

    if arguments.ecrire:
        try:
            changements = ecrire(manifeste, pieces)
        except (OSError, ValueError) as erreur:
            print(f"ERREUR FICHIER : {erreur}", file=sys.stderr)
            return 2
        for changement in changements:
            print(f"CHANGE    {changement}")
        print(
            f"manifeste reecrit : {manifeste} ({len(pieces)} pieces, "
            f"{len(changements)} empreinte(s) modifiee(s))"
        )
        return 0

    try:
        ecarts = verifier(pieces)
    except (OSError, ValueError) as erreur:
        print(f"ERREUR FICHIER : {erreur}", file=sys.stderr)
        return 2

    if ecarts:
        print()
        for ecart in ecarts:
            print(ecart)
        print(f"\nSTOP : {len(ecarts)} ecart(s) sur {len(pieces)} pieces.")
        return 1

    print(f"\nFEU VERT : {len(pieces)} pieces, toutes conformes a leur empreinte publiee.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
