# -*- coding: utf-8 -*-
"""
Pilote Finance - Le Test « taxe foncière » - calcul refait par nous.
Poids de chaque élément de confort dans la valeur locative (donc dans la taxe foncière
et la TEOM du même local, qui sont proportionnelles à cette valeur).

Sources des règles (lues le 25/09/2026) :
- CGI, annexe III, art. 324 T (équivalences superficielles) : brochure DGFiP « Impôts locaux 2026 », p. 25
- CGI, annexe III, art. 324 O (coefficient d'importance) : Légifrance LEGIARTI000037128009
- BOFiP BOI-IF-TFB-20-10-20-50 : appartement de 70 m² en 6e catégorie -> surface pondérée comparative 70 m²
- Exemple officiel de la maison : brochure DGFiP « Impôts locaux 2026 », p. 25-26
Hypothèse de protocole (annoncée) pour les deux logements fictifs : correctif d'ensemble = 1.
"""
import csv
import math
import sys

EQ = {  # m² par élément, art. 324 T
    "eau courante": 4, "gaz": 2, "électricité": 2, "égout": 3, "vide-ordures": 3,
    "baignoire": 5, "douche": 4, "lavabo": 3, "WC": 3, "chauffage central (par pièce ou salle d'eau)": 2,
}

# Art. 324 O, immeubles collectifs : (coef 20 premiers m², borne 2e tranche, coef 2e tranche, coef au-delà)
IMPORTANCE_COLLECTIF = {6: (1.25, 70, 0.90, 0.75), 5: (1.35, 90, 0.90, 0.75)}


def surface_comparative_collectif(surface_reelle, categorie):
    c1, borne, c2, c3 = IMPORTANCE_COLLECTIF[categorie]
    t1 = min(surface_reelle, 20) * c1
    t2 = max(0, min(surface_reelle, borne) - 20) * c2
    t3 = max(0, surface_reelle - borne) * c3
    return math.floor(t1 + t2 + t3)  # arrondie au m² inférieur (art. 324 O)


def logement(nom, surface_ponderee_nette, equipements):
    """equipements : liste de (libellé, nombre)."""
    lignes = [(lib, n, EQ[lib] * n) for lib, n in equipements]
    total_eq = sum(m for _, _, m in lignes)
    total = surface_ponderee_nette + total_eq
    return {"nom": nom, "nette": surface_ponderee_nette, "lignes": lignes, "eq": total_eq, "totale": total}


# --- A. Studio fictif : 15 m² réels, 6e catégorie, immeuble collectif, correctif d'ensemble 1
spc_a = surface_comparative_collectif(15, 6)
A = logement("A - Studio fictif 15 m² (6e cat., collectif)", spc_a * 1, [
    ("eau courante", 1), ("électricité", 1), ("égout", 1),
    ("douche", 1), ("lavabo", 1), ("WC", 1),
    ("chauffage central (par pièce ou salle d'eau)", 2),  # 1 pièce + 1 salle d'eau
])

# --- B. Appartement fictif : 70 m² réels, 6e catégorie (le « local courant » du BOFiP), correctif 1
spc_b = surface_comparative_collectif(70, 6)
B = logement("B - Appartement fictif 70 m² (6e cat., collectif)", spc_b * 1, [
    ("eau courante", 1), ("électricité", 1), ("égout", 1),
    ("baignoire", 1), ("lavabo", 1), ("WC", 1),
    ("chauffage central (par pièce ou salle d'eau)", 5),  # séjour, 2 chambres, cuisine + salle de bains
])

# --- C. Maison : exemple officiel DGFiP (brochure IDL 2026, p. 25-26), partie principale seule
C = logement("C - Maison, exemple officiel DGFiP (partie principale)", 275, [
    ("eau courante", 1), ("gaz", 1), ("électricité", 1), ("égout", 1),
    ("baignoire", 1), ("douche", 1), ("lavabo", 2), ("WC", 3),
    ("chauffage central (par pièce ou salle d'eau)", 8),
])
# Contrôles contre la brochure : 51 m² d'équivalences, 326 m² de surface pondérée totale
assert C["eq"] == 51 and C["totale"] == 326, C
assert spc_b == 70, spc_b  # exemple BOFiP
# Maison entière selon la brochure : VL 1970 = 3 260 (maison) + 240 (garage) + 148 (piscine) = 3 648
VL_MAISON_TOTALE = 3260 + 240 + 148
TARIF_MAISON = 10  # €/m², tarif illustratif de la brochure

rows = []
for L in (A, B, C):
    for lib, n, m2 in L["lignes"]:
        part = m2 / L["totale"]
        rows.append({
            "logement": L["nom"], "élément": lib, "nombre": n, "m² ajoutés": m2,
            "surface pondérée totale": L["totale"],
            "part de la valeur locative (%)": round(100 * part, 2),
            "pour 1 000 € de taxe (€)": round(1000 * part, 2),
        })
    rows.append({
        "logement": L["nom"], "élément": "TOTAL éléments de confort", "nombre": "",
        "m² ajoutés": L["eq"], "surface pondérée totale": L["totale"],
        "part de la valeur locative (%)": round(100 * L["eq"] / L["totale"], 2),
        "pour 1 000 € de taxe (€)": round(1000 * L["eq"] / L["totale"], 2),
    })

# Maison entière (dépendances comprises), baignoire et confort total rapportés à la VL totale
bain_maison_totale = 5 * TARIF_MAISON / VL_MAISON_TOTALE
confort_maison_totale = (51 * 10 + 2 * 10 + 6 * 4) / VL_MAISON_TOTALE

# Scénario « fiche incomplète » (illustration, logement B' = B avec une douche au lieu d'une baignoire) :
# la fiche ne mentionne que l'eau, l'électricité et l'égout ; la mise à jour décrite par le ministère
# (réponses du 14/05 et du 19/05/2026 : eau, électricité, un WC, un lavabo, une douche par salle d'eau,
# chauffage ou climatisation) ajouterait : WC 3 + lavabo 3 + douche 4 + chauffage 5 x 2 = 20 m².
manquants_B = 3 + 3 + 4 + 10
avant = spc_b + 4 + 2 + 3
apres = avant + manquants_B
hausse_B = manquants_B / avant

out = sys.argv[1] if len(sys.argv) > 1 else "PF_LeTest_TaxeFonciere_calcul.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
    w.writeheader()
    w.writerows(rows)

print(f"Surface comparative studio 15 m² (6e cat.) : {spc_a} m² ; appartement 70 m² : {spc_b} m²")
for L in (A, B, C):
    print(f"\n{L['nom']} : nette {L['nette']} + confort {L['eq']} = {L['totale']} m² pondérés"
          f" -> confort = {100*L['eq']/L['totale']:.1f} % de la valeur locative")
    for lib, n, m2 in L["lignes"]:
        print(f"   {lib:40s} x{n}  {m2:3d} m²  {100*m2/L['totale']:5.2f} %  ({1000*m2/L['totale']:6.2f} € pour 1 000 €)")
print(f"\nMaison entière (garage et piscine compris, VL 1970 = {VL_MAISON_TOTALE} €) :"
      f" baignoire {100*bain_maison_totale:.2f} %, tout le confort {100*confort_maison_totale:.2f} %")
print(f"Appartement B' (douche), fiche avec seulement eau, électricité, égout : {avant} -> {apres} m²"
      f" = +{100*hausse_B:.1f} % de valeur locative")
