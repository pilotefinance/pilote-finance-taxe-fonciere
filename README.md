# Le Test « taxe foncière » — Pilote Finance

*La CI de ce dépôt (GitHub Actions) est verte quand le lint des deux outils passe, quand le calcul,
rejoué à partir des données publiées ici, redonne **les fichiers de résultats publiés ici**, et quand
chaque pièce listée dans `EMPREINTES.json` (données, scripts, résultats, protocole, outils) a
l'empreinte SHA-256 publiée. Elle tourne à chaque modification, et le 1er de chaque mois tant que
GitHub ne suspend pas la tâche planifiée (il le fait sur un dépôt public après 60 jours sans
activité). Pas besoin de nous croire sur parole.*

On a testé une idée reçue : **« la taxe foncière, c'est la surface du logement multipliée par le
taux de la commune »**. Verdict : non. Les équipements (baignoire, toilettes, chauffage central…)
sont convertis en mètres carrés et payés au même tarif au m² que la surface.

Tout est ici : le protocole figé **avant** le téléchargement des données, les données officielles,
les trois scripts, leurs sorties. C'est publié pour que n'importe qui puisse **refaire le calcul et
nous contredire**.

Scripts, textes et vérifications de ce dépôt sont produits avec des outils d'IA, sous la
responsabilité éditoriale de Pilote Finance.

---

## Premier résultat : ce que pèsent les équipements, en pourcentage

Deux logements **types** (aucun n'est réel), de même catégorie (6e, confort ordinaire), construits
pour le test ; les scripts les appellent « fictifs ». **Hypothèses annoncées** : correctif d'ensemble
(entretien, situation) égal à 1, aucune dépendance.

| Cas type | Équipements | Surface pondérée | dont équipements | Part des équipements dans la valeur locative |
|---|---|---|---|---|
| **Studio type**, 15 m² | eau courante, électricité, égout, douche, lavabo, WC, chauffage central (la pièce et la salle d'eau) | 18 + 23 = 41 m² | 23 m² | **56,1 %** |
| **Appartement type**, 70 m² : séjour, 2 chambres, cuisine, salle de bains, WC séparé | eau courante, électricité, égout, baignoire, lavabo, WC, chauffage central (4 pièces et la salle de bains) | 70 + 30 = 100 m² | 30 m² | **30,0 %** |

À catégorie et correctif égaux, plus le logement est petit, plus ses équipements pèsent : c'est ce
que montrent nos deux cas types. Dans l'appartement type, la baignoire seule représente 5 % de la
valeur locative : sur 1 000 € de taxe, 50 €.

**À part, parce que ce n'est pas le même cas :** la maison de l'exemple de calcul officiel de la
DGFiP (un exemple de calcul, pas une maison réelle : 160 m², 3e catégorie, 3 WC, un garage, une
piscine). Pour la **maison entière, garage et piscine compris**, les équipements pèsent **15,2 %**
de la valeur locative (ligne « Maison entière » de la sortie console,
`resultats/PF_LeTest_TaxeFonciere_calcul_sortie.txt`). Le tableur donne aussi 15,6 % pour la partie
principale seule : ce n'est pas le même périmètre. Catégorie, correctif et dépendances diffèrent de
nos deux cas types : ce n'est pas une comparaison « toutes choses égales par ailleurs ».

## Deuxième résultat : ce que coûte une baignoire, en euros par an

**Conditions de tous les montants ci-dessous :** appartement ordinaire (6e catégorie), au tarif
médian de la commune, taxe foncière 2026, hors taxe d'ordures ménagères, taxes spéciales
d'équipement, GEMAPI et part des syndicats de communes.

- **Dans la commune médiane : 16,64 € par an**, sur 28 338 communes de métropole (celles qui ont un
  tarif d'appartement de 6e catégorie et un taux 2026 publié, règle 1 du protocole ; chaque commune
  compte pour une). Huit communes sur dix sont entre 10,91 € et 26,91 €.
- **Pour l'habitant médian de ces communes : 28,69 € par an.** Ce chiffre a été calculé **après
  coup, hors protocole**, en pondérant chaque commune par sa population (Insee, populations de
  référence 2023) : beaucoup de communes du champ sont peu peuplées, et 86,8 % des habitants vivent
  dans une commune au-dessus de 16,64 €. Huit habitants sur dix sont entre 15,53 € et 43,93 €.
- **Paris 38,74 € · Marseille 37,36 € (40,78 € si chaque tarif distinct de la ville compte une
  fois) · Lyon 30,15 €.** Les trois communes les plus peuplées, choisies avant de voir leur
  résultat. **Paris et Marseille sont trop proches pour être départagées** : l'écart change de sens
  selon la façon de compter les tarifs marseillais. Aucun classement n'est tiré de ce dépôt.
- **Pourquoi deux valeurs pour Marseille.** Marseille n'a que trois tarifs distincts d'appartement
  de 6e catégorie (5,03 €, 5,49 €, 5,95 €), et le plus bas se retrouve dans ses 16 arrondissements :
  selon la façon de compter, sa médiane vaut 5,03 € ou 5,49 €, et la baignoire passe de 37,36 € à
  40,78 € (protocole, corrections du 25/09/2026). À Paris, la médiane bouge à peine : 10,37 € ou
  10,35 €.

**Le paradoxe Paris-Marseille.** Taux 2026, commune et intercommunalité : Paris 20,5 %, Marseille
47,13 %, soit 2,30 fois plus. Mais les tarifs médians au m², une fois actualisés, sont plus de deux
fois plus élevés à Paris (10,37 × 1,85 = 19,18 € contre 5,03 × 1,60 = 8,05 € ; rapport 2,38, ou 2,18
dans l'autre convention de comptage, médiane des tarifs distincts : Paris 10,35 €, Marseille
5,49 €). Les deux effets se compensent.

## La formule

Coût annuel, en 2026, d'un m² d'équipement dans une commune (brochure DGFiP « Impôts locaux 2026 »,
p. 43, 45 et 53 du PDF ; art. 1388 et 1641 du CGI) :

```
tarif 1970 au m² (appartement, 6e catégorie, médiane des tarifs de la commune)
  × coefficient d'actualisation du département (brochure, p. 43)
  × 3,825 (coefficient cumulé des revalorisations pour 2026, p. 45)
  ÷ 2
  × (taux communal 2026 + taux intercommunal 2026)
  × 1,03 (frais de gestion de 3 %, p. 53)
```

Le barème des équivalences (CGI, annexe III, art. 324 T ; brochure DGFiP 2026, p. 25 du PDF) :

- par logement : eau courante 4 m², gaz (installation fixe) 2 m², électricité 2 m², raccordement à
  l'égout 3 m², vide-ordures 3 m² ;
- par équipement : baignoire 5 m², douche 4 m², lavabo et autres appareils sanitaires 3 m², WC 3 m² ;
- chauffage central : 2 m² par pièce et par salle d'eau desservies (sauf les WC et les pièces
  annexes : entrée, couloir, dégagement, dressing…).

Remplacer une baignoire par une douche retire donc 1 m², soit environ 7,75 € par an à Paris, dans
les conditions ci-dessus.

## L'ordre des opérations

Les pourcentages sont calculés le 25/09/2026, puis recalculés séparément, sans notre script, par un
second agent d'IA lancé à contexte vierge : identiques. Pour les euros :

1. **25/09/2026, 21h18** : protocole écrit et figé **avant** le téléchargement des données
   ([`protocole/PF_LeTest_TaxeFonciere_PROTOCOLE_option2.md`](protocole/PF_LeTest_TaxeFonciere_PROTOCOLE_option2.md)).
2. **21h19 à 21h20** : téléchargement des taux 2026, des intercommunalités, des populations et des
   tarifs (horodatage des fichiers, heure de Paris).
3. **21h23** : calcul exécuté ; les écarts d'application sont écrits et datés dans le protocole,
   aucune règle n'est changée.
4. **21h39** : corrections après une contre-vérification par un agent d'IA à contexte vierge (celle
   que le protocole appelle « indépendante »), écrites dans le protocole ; le complément pondéré par
   la population est ajouté et annoncé comme ajouté après coup.

Ces heures sont celles de nos outils et de nos fichiers : elles ne sont pas attestées par un tiers.

## Ce que ce dépôt ne dit pas

- **Ce n'est pas un avis sur la situation de chacun.** Les logements sont des cas types. Un logement
  réel a sa catégorie et sa série de tarifs, toutes deux sur sa fiche d'évaluation. Pour un cas
  précis : le centre des finances publiques.
- **Tarif médian.** Une commune peut avoir plusieurs tarifs ; on a pris la médiane. Un tarif de
  6e catégorie existe aussi dans des villages où ce type d'appartement est rare.
- **Non compté** (règle 6 du protocole) : taxe d'ordures ménagères, taxes spéciales d'équipement,
  GEMAPI et part des syndicats de communes, calculées sur la même base : là où elles s'appliquent,
  le coût réel sur l'avis est plus élevé. Les arrondis annuels de l'administration ne sont pas
  comptés non plus.
- **Exonérations et dégrèvements non appliqués** : une exonération totale annule la taxe foncière
  (la taxe d'ordures ménagères reste due), et le dégrèvement de 100 € entre 65 et 75 ans, sous
  condition de revenus, change le total.
- **Dates** : tarifs au 01/01/2024, appliqués aux taux votés en 2026.
- **Taux intercommunal inconnu pour 42 communes**, dont l'intercommunalité est absente du fichier
  DGFiP des taux 2026 : compté 0, sans effet sur les médianes (écrit dans le protocole).
- **Ni minimum ni maximum national.** Le résumé les contient, mais ils portent des valeurs
  probablement anormales : le protocole prévoit la médiane et les déciles, rien d'autre.
- **Aucune autre commune que Paris, Marseille et Lyon** n'est commentée : une commune repérée après
  coup serait du tri a posteriori.

## Rejouer le calcul

Python 3.12 et les versions figées de `requirements.txt` :

```bash
pip install -r requirements.txt
python rejouer.py               # relance les trois scripts et compare à resultats/
python verifier_empreintes.py   # chaque pièce listée a bien son empreinte
```

Ou script par script (le dossier de sortie doit exister) :

```bash
python calcul/PF_LeTest_TaxeFonciere_calcul.py sortie/PF_LeTest_TaxeFonciere_calcul.csv
python calcul/PF_LeTest_TaxeFonciere_communes_2026.py donnees sortie
python calcul/PF_LeTest_TaxeFonciere_communes_2026_pondere.py donnees sortie
```

Un même script écrit ses fichiers avec des fins de ligne CRLF sous Windows et LF sous Linux :
`rejouer.py` compare le contenu en neutralisant les fins de ligne, pour qu'on puisse rejouer sur
l'un comme sur l'autre. Seule autre exception, dite à l'écran quand elle joue : un JSON aux octets
différents mais au contenu identique (mêmes clés, mêmes valeurs écrites), parce que l'ordre des ex
æquo d'un dictionnaire, trié par pandas, peut changer d'un processeur à l'autre. Tout autre écart est
un STOP. Les trois scripts sont publiés tels qu'exécutés le 25/09/2026 : on ne les retouche pas,
même pour le style, leurs empreintes sont consignées.

## Les fichiers

| Fichier | Quoi |
|---|---|
| `protocole/PF_LeTest_TaxeFonciere_PROTOCOLE_option2.md` | Le protocole figé à 21h18, puis ses écarts et corrections, datés. |
| `calcul/PF_LeTest_TaxeFonciere_calcul.py` | Les pourcentages : studio type, appartement type, maison de l'exemple officiel. |
| `calcul/PF_LeTest_TaxeFonciere_communes_2026.py` | Les euros, commune par commune (règles du protocole). |
| `calcul/PF_LeTest_TaxeFonciere_communes_2026_pondere.py` | Le complément pondéré par la population, ajouté après coup. |
| `resultats/PF_LeTest_TaxeFonciere_calcul.csv` | Le tableur des pourcentages. |
| `resultats/PF_LeTest_TaxeFonciere_calcul_sortie.txt` | La sortie console du calcul des pourcentages, dont la maison de l'exemple DGFiP, entière, garage et piscine compris (15,19 %). |
| `resultats/PF_LeTest_TaxeFonciere_communes_2026.csv` | Commune par commune : le coût d'un m² d'équipement, de cinq équipements et des 30 m² de l'appartement type. |
| `resultats/PF_LeTest_TaxeFonciere_communes_2026_resume.json` | Médiane et déciles nationaux, Paris, Marseille, Lyon, journal des exclusions. |
| `resultats/PF_LeTest_TaxeFonciere_communes_2026_pondere.json` | Médiane et déciles pondérés par la population, et les contrôles demandés par le vérificateur (agent d'IA). Le détail `communes_taux_intercommunal_0_par_EPCI` compte toutes les communes dont le taux intercommunal retenu est nul (1 915) : ce n'est pas le décompte des 175 communes sans taux dans le fichier DGFiP, écrit dans le protocole. |
| `donnees/` | Les données officielles, telles que téléchargées (le tableur des intercommunalités tel qu'extrait de l'archive Insee, l'archive des populations renommée à l'enregistrement) : liste, producteurs, licences dans [`SOURCES.md`](SOURCES.md). |
| `rejouer.py` | Relance les trois scripts et compare à `resultats/`. |
| `verifier_empreintes.py` + `EMPREINTES.json` | Vérifie que chaque pièce listée est celle dont l'empreinte est publiée. |

## Une erreur trouvée ? Dites-le

[Ouvrez une issue](../../issues/new?template=signaler-une-erreur.md). Si vous avez raison, on
corrige et on le dit publiquement. Merci de rester sur les chiffres : ce dépôt sert à vérifier un
calcul, pas à conseiller qui que ce soit sur sa situation fiscale.

## Licence

[MIT](LICENSE) pour nos scripts et nos résultats.

Les données de `donnees/` ne sont pas couvertes par cette licence : elles restent celles de leurs
producteurs (DGFiP, Insee), redistribuées sans modification, avec leur source et leur date. Détail,
licence par licence : [`SOURCES.md`](SOURCES.md).

---

**Ce dépôt mesure la place des équipements dans le calcul de la taxe foncière, sur des cas types.
Il ne dit rien de la taxe d'un logement précis.**
