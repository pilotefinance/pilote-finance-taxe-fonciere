# -*- coding: utf-8 -*-
"""
Pilote Finance - Le Test « taxe foncière », option 2 : les euros, commune par commune.
Protocole figé le 25/09/2026 à 21h18, AVANT ouverture des données :
  PF_LeTest_TaxeFonciere_PROTOCOLE_option2.md

Coût annuel 2026 d'un m² d'équipement =
  tarif 1970 au m² (appartement, 6e catégorie) x coefficient d'actualisation du département
  x 3,825 (coefficient amalgamé 2026) / 2 x (taux communal 2026 + taux intercommunal 2026) x 1,03

Sources (dossier sources_taxefonciere/) :
  - descriptif-tarifs-des-locaux-d-habitation_2024.csv (DGFiP, data.gouv.fr / data.economie.gouv.fr, MàJ 24/04/2025)
  - Taux_2026_communes.xlsx, Taux_2026_EPCI.xlsx (DGFiP, 27/08/2026, taux au 31/07/2026)
  - EPCI_au_01-01-2026.xlsx (INSEE, composition communale des EPCI au 01/01/2026)
  - insee_populations_2023_ensemble.zip (INSEE, populations de référence 2023, en vigueur au 01/01/2026)
  - Brochure DGFiP « Impôts locaux 2026 » : p. 43 (actualisation), p. 45 (3,825), p. 53 (formule, frais 3 %)
"""
import json
import re
import sys
import unicodedata
import zipfile
import io

import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "."

AMALGAME_2026 = 3.825
FRAIS = 1.03
EQUIP_M2 = {"baignoire": 5, "douche": 4, "WC": 3, "lavabo": 3, "chauffage central, par pièce": 2,
            "appartement B entier (30 m²)": 30}

# Brochure DGFiP 2026, p. 43 : coefficients d'actualisation, locaux d'habitation
ACTU = {
 "01":1.60,"02":1.75,"03":1.60,"04":1.65,"05":1.67,"06":1.55,"07":1.59,"08":1.72,"09":1.60,"10":1.60,
 "11":1.55,"12":1.73,"13":1.60,"14":1.66,"15":1.60,"16":1.68,"17":1.69,"18":1.57,"19":1.67,"2A":1.58,
 "2B":1.58,"22":1.48,"23":1.63,"24":1.62,"25":1.70,"26":1.70,"27":1.75,"28":1.57,"29":1.70,"30":1.50,
 "31":1.49,"32":1.41,"33":1.65,"34":1.49,"35":1.57,"36":1.60,"37":1.57,"38":1.63,"39":1.65,"40":1.70,
 "41":1.59,"42":1.68,"43":1.65,"44":1.65,"45":1.64,"46":1.73,"47":1.57,"48":1.50,"49":1.63,"50":1.70,
 "51":1.62,"52":1.59,"53":1.59,"55":1.70,"56":1.57,"57":1.76,"58":1.74,"59":1.69,"60":1.78,"61":1.70,
 "62":1.77,"63":1.54,"64":1.70,"65":1.69,"66":1.62,"67":1.67,"68":1.69,"69":1.63,"70":1.66,"71":1.67,
 "72":1.63,"73":1.63,"74":1.60,"75":1.85,"76":1.73,"77":1.67,"78":1.73,"79":1.59,"80":1.75,"81":1.54,
 "82":1.52,"83":1.62,"84":1.60,"85":1.52,"86":1.55,"87":1.67,"88":1.67,"89":1.65,"90":1.74,"91":1.71,
 "92":1.77,"93":1.68,"94":1.70,"95":1.70,
}
# Cas particuliers de la p. 43
COTE_DOR_157 = {"DIJON", "CHENOVE", "CHEVIGNY SAINT SAUVEUR", "FONTAINE LES DIJON", "LONGVIC",
                "QUETIGNY", "SAINT APOLLINAIRE", "TALANT"}
ACTU_21_AUTRES = 1.72
ACTU_54_HAN = 1.70
ACTU_54_AUTRES = 1.63

log = []


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    s = s.replace("ST ", "SAINT ").replace("STE ", "SAINTE ")
    return re.sub(r"[^A-Z0-9]+", " ", s).strip().replace("ST ", "SAINT ")


def dep2(d):
    d = str(d).strip()
    return d.zfill(2) if d.isdigit() and len(d) < 3 else d


# 1. Tarifs : appartements, 6e catégorie, métropole
t = pd.read_csv(f"{SRC}/descriptif-tarifs-des-locaux-d-habitation_2024.csv", sep=";", dtype=str)
n0 = len(t)
t = t.dropna(subset=["Département", "Code Commune"])
t["DEP"] = t["Département"].map(dep2)
t["VL"] = pd.to_numeric(t["VL au m²"], errors="coerce")
a6 = t[(t["Nature locaux"] == "A") & (t["Catégorie"] == "6") & (t["DEP"].isin(ACTU.keys()) | t["DEP"].isin(["21", "54"]))].copy()
log.append(f"Tarifs : {n0} lignes ; appartements 6e catégorie en métropole : {len(a6)} lignes")
nz = (a6["VL"] <= 0) | a6["VL"].isna()
log.append(f"ÉCART au protocole (écrit ici) : {int(nz.sum())} lignes à tarif nul ou vide exclues (un tarif de 0 € n'est pas un tarif)")
a6 = a6[~nz]
a6["COM"] = a6["DEP"] + a6["Code Commune"].str.zfill(3)
# communes à arrondissements -> commune entière (règle 3)
a6["COM_ENT"] = a6["COM"]
a6.loc[a6["COM"].str.match(r"^751(0[1-9]|1\d|20)$"), "COM_ENT"] = "75056"
a6.loc[a6["COM"].str.match(r"^132(0[1-9]|1[0-6])$"), "COM_ENT"] = "13055"
a6.loc[a6["COM"].str.match(r"^6938[1-9]$"), "COM_ENT"] = "69123"
a6 = a6.drop_duplicates(subset=["COM", "Série tarif bâti", "VL"])

# coefficient d'actualisation
def actu(row):
    d = row["DEP"]
    if d == "21":
        return 1.57 if norm(row["Nom de la commune"]) in COTE_DOR_157 else ACTU_21_AUTRES
    if d == "54":
        return ACTU_54_HAN if norm(row["Nom de la commune"]) == "HAN DEVANT PIERREPONT" else ACTU_54_AUTRES
    return ACTU[d]

a6["ACTU"] = a6.apply(actu, axis=1)
cd = a6[a6["DEP"] == "21"]
log.append("Côte-d'Or à 1,57 : " + ", ".join(sorted(set(cd.loc[cd["ACTU"] == 1.57, "Nom de la commune"]))))
log.append("Meurthe-et-Moselle à 1,70 : " + ", ".join(sorted(set(a6.loc[(a6["DEP"] == "54") & (a6["ACTU"] == 1.70), "Nom de la commune"]))))

g = a6.groupby("COM_ENT").agg(
    nom=("Nom de la commune", "first"), dep=("DEP", "first"), n_tarifs=("VL", "size"),
    vl_med=("VL", "median"), vl_min=("VL", "min"), vl_max=("VL", "max"), actu=("ACTU", "median"),
).reset_index().rename(columns={"COM_ENT": "COM"})
g.loc[g["COM"] == "75056", "nom"] = "PARIS"
g.loc[g["COM"] == "13055", "nom"] = "MARSEILLE"
g.loc[g["COM"] == "69123", "nom"] = "LYON"

# 2. Taux 2026 : commune + EPCI
c = pd.read_excel(f"{SRC}/Taux_2026_communes.xlsx", engine="calamine", header=5, dtype=str)
c = c.rename(columns={"Code commune": "COM", "Taxe sur le foncier bâti": "TX_COM"})[["COM", "TX_COM"]]
c["TX_COM"] = pd.to_numeric(c["TX_COM"], errors="coerce")
e = pd.read_excel(f"{SRC}/Taux_2026_EPCI.xlsx", engine="calamine", header=5, dtype=str)
e = e.rename(columns={"SIREN de l'EPCI": "EPCI", "Taux voté Taxe sur le foncier bâti": "TX_EPCI"})[["EPCI", "TX_EPCI"]]
e["TX_EPCI"] = pd.to_numeric(e["TX_EPCI"], errors="coerce")
comp = pd.read_excel(f"{SRC}/EPCI_au_01-01-2026.xlsx", engine="calamine", sheet_name="Composition_communale", header=5, dtype=str)
comp = comp.rename(columns={"CODGEO": "COM"})[["COM", "EPCI"]]

m = g.merge(c, on="COM", how="left")
log.append(f"Communes avec tarif : {len(g)} ; sans taux communal 2026 trouvé (codes changés, fusions) : {int(m['TX_COM'].isna().sum())} -> exclues")
m = m.dropna(subset=["TX_COM"])
m = m.merge(comp, on="COM", how="left").merge(e, on="EPCI", how="left")
sans_epci = m["TX_EPCI"].isna()
log.append(f"Communes sans taux intercommunal de taxe foncière dans le fichier DGFiP 2026 (taux intercommunal compté 0) : {int(sans_epci.sum())}"
           + (" dont Paris (Métropole du Grand Paris absente du fichier)" if bool(m.loc[m['COM'] == '75056', 'TX_EPCI'].isna().any()) else ""))
m["TX_EPCI"] = m["TX_EPCI"].fillna(0.0)
m["TX_GLOBAL"] = m["TX_COM"] + m["TX_EPCI"]

# 3. Coût annuel d'un m² d'équipement, en euros 2026
m["EUR_M2"] = m["vl_med"] * m["actu"] * AMALGAME_2026 / 2 * m["TX_GLOBAL"] / 100 * FRAIS
m["EUR_M2_MIN"] = m["vl_min"] * m["actu"] * AMALGAME_2026 / 2 * m["TX_GLOBAL"] / 100 * FRAIS
m["EUR_M2_MAX"] = m["vl_max"] * m["actu"] * AMALGAME_2026 / 2 * m["TX_GLOBAL"] / 100 * FRAIS
for k, v in EQUIP_M2.items():
    m[f"EUR_{k}"] = m["EUR_M2"] * v

# 4. Résultats
bain = m["EUR_M2"] * 5
nat = {
    "communes": int(len(m)),
    "baignoire_mediane": round(float(bain.median()), 2),
    "baignoire_D1": round(float(bain.quantile(0.1)), 2),
    "baignoire_D9": round(float(bain.quantile(0.9)), 2),
    "baignoire_min": round(float(bain.min()), 2),
    "baignoire_max": round(float(bain.max()), 2),
    "appartB30m2_mediane": round(float((m["EUR_M2"] * 30).median()), 2),
    "tarif_mediane": round(float(m["vl_med"].median()), 2),
    "taux_global_mediane": round(float(m["TX_GLOBAL"].median()), 2),
}
villes = {}
for code in ["75056", "13055", "69123"]:
    r = m[m["COM"] == code].iloc[0]
    villes[r["nom"]] = {
        "tarifs_A6": int(r["n_tarifs"]), "tarif_med": r["vl_med"], "tarif_min": r["vl_min"], "tarif_max": r["vl_max"],
        "actu": r["actu"], "taux_com": r["TX_COM"], "taux_epci": r["TX_EPCI"], "taux_global": round(r["TX_GLOBAL"], 2),
        "eur_m2": round(r["EUR_M2"], 2),
        "baignoire": round(r["EUR_M2"] * 5, 2), "baignoire_min": round(r["EUR_M2_MIN"] * 5, 2), "baignoire_max": round(r["EUR_M2_MAX"] * 5, 2),
        "WC": round(r["EUR_M2"] * 3, 2), "douche": round(r["EUR_M2"] * 4, 2),
        "chauffage_par_piece": round(r["EUR_M2"] * 2, 2), "appartB_30m2": round(r["EUR_M2"] * 30, 2),
    }

cols = ["COM", "nom", "dep", "n_tarifs", "vl_med", "vl_min", "vl_max", "actu", "TX_COM", "EPCI", "TX_EPCI", "TX_GLOBAL",
        "EUR_M2"] + [f"EUR_{k}" for k in EQUIP_M2]
m[cols].sort_values("COM").to_csv(f"{OUT}/PF_LeTest_TaxeFonciere_communes_2026.csv", sep=";", index=False,
                                   encoding="utf-8-sig", float_format="%.4f")
res = {"national": nat, "villes": villes, "journal": log}
with open(f"{OUT}/PF_LeTest_TaxeFonciere_communes_2026_resume.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=float)
print(json.dumps(res, ensure_ascii=False, indent=2, default=float))
