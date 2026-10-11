# -*- coding: utf-8 -*-
"""
Complément AJOUTÉ APRÈS COUP (25/09/2026, après la contre-vérification de 21h3x) — pas dans le protocole figé à 21h18.
Même résultat commune par commune (PF_LeTest_TaxeFonciere_communes_2026.csv), pondéré par la population municipale
INSEE 2023 (populations de référence en vigueur au 01/01/2026), pour dire ce que paie « un habitant typique »
plutôt que « une commune typique ». Plus : contrôles demandés par le vérificateur (6M, communes sans taux intercommunal).
"""
import sys, zipfile, io, json
import numpy as np
import pandas as pd
SRC, OUT = sys.argv[1], sys.argv[2]
m = pd.read_csv(f"{OUT}/PF_LeTest_TaxeFonciere_communes_2026.csv", sep=";", dtype={"COM": str, "EPCI": str})
z = zipfile.ZipFile(f"{SRC}/insee_populations_2023_ensemble.zip")
p = pd.read_csv(io.BytesIO(z.read("donnees_communes.csv")), sep=";", dtype=str)
p["PMUN"] = pd.to_numeric(p["PMUN"])
p.loc[p["COM"].str.match(r"^751(0[1-9]|1\d|20)$"), "COM"] = "75056"
p.loc[p["COM"].str.match(r"^132(0[1-9]|1[0-6])$"), "COM"] = "13055"
p.loc[p["COM"].str.match(r"^6938[1-9]$"), "COM"] = "69123"
p = p.groupby("COM", as_index=False)["PMUN"].sum()
d = m.merge(p, on="COM", how="left")
sans_pop = int(d["PMUN"].isna().sum())
d = d.dropna(subset=["PMUN"]).sort_values("EUR_baignoire")
cw = d["PMUN"].cumsum() / d["PMUN"].sum()
def wq(q): return float(d.loc[cw >= q, "EUR_baignoire"].iloc[0])
res = {"communes_avec_population": int(len(d)), "communes_sans_population": sans_pop,
       "habitants_couverts": int(d["PMUN"].sum()),
       "baignoire_mediane_ponderee": round(wq(0.5), 2), "baignoire_D1_ponderee": round(wq(0.1), 2),
       "baignoire_D9_ponderee": round(wq(0.9), 2),
       "part_habitants_au_dessus_de_16_64": round(float(d.loc[d["EUR_baignoire"] > 16.64, "PMUN"].sum() / d["PMUN"].sum()), 4)}
# Contrôle 6M / 6 (appartements, même commune d'origine, même série)
t = pd.read_csv(f"{SRC}/descriptif-tarifs-des-locaux-d-habitation_2024.csv", sep=";", dtype=str).dropna(subset=["Département"])
t["VL"] = pd.to_numeric(t["VL au m²"], errors="coerce")
k = ["Département", "Code Commune", "Code commune origine du tarif", "Série tarif bâti"]
a = t[t["Nature locaux"] == "A"]
x = a[a["Catégorie"] == "6"][k + ["VL"]].merge(a[a["Catégorie"] == "6M"][k + ["VL"]], on=k, suffixes=("_6", "_6M"))
x = x[(x["VL_6"] > 0) & (x["VL_6M"] > 0)]
r = 1 - x["VL_6M"] / x["VL_6"]
res["ecart_6M_sous_6_mediane"] = round(float(r.median()), 4)
res["ecart_6M_sous_6_Q1_Q3"] = [round(float(r.quantile(.25)), 4), round(float(r.quantile(.75)), 4)]
# Communes sans taux intercommunal : répartition par EPCI
s = m[m["TX_EPCI"] == 0].groupby("EPCI", dropna=False).size().sort_values(ascending=False)
res["communes_taux_intercommunal_0_par_EPCI"] = {str(kk): int(v) for kk, v in s.items()}
print(json.dumps(res, ensure_ascii=False, indent=2))
with open(f"{OUT}/PF_LeTest_TaxeFonciere_communes_2026_pondere.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
