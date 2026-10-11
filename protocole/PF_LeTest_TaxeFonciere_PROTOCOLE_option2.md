# Protocole figé AVANT d'ouvrir les données — Le Test taxe foncière, option 2 (les euros)
Écrit par Cowork le vendredi 25/09/2026 à 21h18 (heure relevée par outil), avant tout téléchargement du fichier des tarifs et du tableur des taux 2026. Décision d'Aleksandar à 21h17 : « Fais ce qu'il y a de mieux pour le projet » → pourcentages ET euros (§3 du Fact-Lock v1.1).

## Formule (brochure DGFiP « Impôts locaux 2026 », p. 45 et 53 du PDF ; art. 1388 et 1641 du CGI)
Coût annuel d'un m² d'équipement, en 2026 =
tarif 1970 au m² (appartement, 6e catégorie, commune) × coefficient d'actualisation du département (brochure p. 43) × 3,825 (coefficient amalgamé 2026, p. 45) ÷ 2 × (taux communal 2026 + taux intercommunal 2026) × 1,03 (frais de gestion de 3 % sur la taxe foncière, p. 53).
Baignoire = 5 m², douche = 4 m², WC = 3 m², lavabo = 3 m², chauffage central = 2 m² par pièce ou salle d'eau.

## Règles de sélection (écrites avant de voir un seul chiffre)
1. Univers : communes de métropole présentes dans le fichier DGFiP des tarifs des locaux d'habitation (data.gouv.fr, édition 2024) avec au moins un tarif « appartement » de 6e catégorie, et présentes dans les taux 2026 publiés par la DGFiP. DOM exclus (autre date de référence, pas d'actualisation de 1980).
2. Si une commune a plusieurs séries de tarifs pour l'appartement de 6e catégorie : on retient la médiane de ses tarifs, et on garde le minimum et le maximum pour l'écran.
3. Communes à arrondissements (Paris, Marseille, Lyon) : tous les tarifs de leurs arrondissements, traités comme une seule commune.
4. Résultat national : médiane, 1er décile et 9e décile du coût annuel de la baignoire, chaque commune comptant pour une (non pondéré).
5. Les trois communes montrées : Paris, Marseille et Lyon, les trois communes les plus peuplées (populations légales de l'INSEE), choisies pour être parlantes, pas pour leur résultat. Si l'une n'a pas de tarif d'appartement de 6e catégorie, on la remplace par la suivante dans l'ordre de population.
6. Non compté, et dit à l'écran : syndicats, taxes spéciales d'équipement, GEMAPI, taxe d'ordures ménagères, arrondis annuels de l'administration.
7. Aucun de ces choix ne sera changé après avoir vu les résultats. Tout écart sera écrit ici, daté, avec sa raison.

## Écarts et précisions, écrits après ouverture des données (25/09/2026, 21h23, heure relevée par outil)
Aucune règle 1 à 7 n'a été changée. Précisions d'application, toutes visibles dans le journal du script `PF_LeTest_TaxeFonciere_communes_2026.py` :
- « 6e catégorie » = le code « 6 » du fichier. Le code « 6M » existe aussi (souvent environ 9 % sous le « 6 » de la même série) ; son sens n'est pas documenté dans le fichier et la notice n'a pas été ouverte : non retenu.
- 35 lignes à tarif nul ou vide exclues (un tarif de 0 € n'est pas un tarif). Lignes strictement identiques (même commune, même série, même tarif) comptées une fois.
- 81 communes du fichier des tarifs sans taux communal 2026 trouvé (codes changés, fusions) : exclues. 175 communes sans taux intercommunal de taxe foncière dans le fichier DGFiP : taux intercommunal compté 0, dont Paris (la Métropole du Grand Paris ne figure pas dans le fichier des taux des EPCI).
- Extrêmes nationaux (minimum et maximum) non affichés : ils contiennent des valeurs probablement anormales (par exemple un tarif de 17 €/m² pour un appartement de 6e catégorie dans un village). Seuls la médiane et les déciles sont montrés, comme prévu par la règle 4.
- Population (règle 5), INSEE, populations de référence 2023 en vigueur au 01/01/2026 : Paris 2 103 778, Marseille 886 040, Lyon 519 127, Toulouse 514 819 (somme des arrondissements municipaux pour Paris, Marseille et Lyon).

## Corrections après la contre-vérification indépendante (25/09/2026, 21h39, heure relevée par outil)
- La catégorie « 6M » est une catégorie intermédiaire entre la 6e et la 7e (CGI, ann. III, art. 324 H-III ; BOFiP BOI-IF-TFB-20-10-20-30). Son tarif est en médiane **11,5 %** sous celui de la 6e dans la même série (entre 8,0 % et 15,1 % pour la moitié des cas), et non « environ 9 % ». L'exclure reste justifié. En métropole, 663 communes n'ont qu'un tarif « 6M » d'appartement, selon notre décompte (666 selon le vérificateur, écart de périmètre) : elles sont hors champ.
- Règle exacte de dédoublonnage : une ligne compte une fois par **code commune du fichier** (donc par arrondissement à Paris, Marseille et Lyon), série et tarif. Des lignes ne différant que par le « code commune origine du tarif » sont comptées une fois.
  - Effet : à Marseille, 3 tarifs distincts (5,03 ; 5,49 ; 5,95 €), le premier présent dans les 16 arrondissements, donnent une médiane de 5,03 € (baignoire 37,36 €).
  - Avec une convention différente (chaque tarif distinct compté une fois pour toute la ville), la médiane serait de 5,49 € (baignoire 40,78 €).
  - La règle appliquée n'est pas changée. Le Fact-Lock ne compare plus Paris et Marseille à l'euro près.
- Les 175 communes sans taux intercommunal se répartissent ainsi :
  - 130 communes de la Métropole du Grand Paris (pas de taux de taxe foncière) ;
  - 3 communes insulaires hors intercommunalité ;
  - 42 communes de deux intercommunalités absentes du fichier DGFiP des taux 2026 : CC du Sud Avesnois (200043404) et CC du Pays Noyonnais (246000756). Leur taux réel est inconnu ; sans effet sur les médianes et les déciles (testé par le vérificateur).
- **Complément AJOUTÉ APRÈS COUP**, hors protocole, à annoncer comme tel : les mêmes résultats, pondérés par la population municipale INSEE 2023.
  - Médiane : 28,69 € pour la baignoire ; 1er décile 15,53 €, 9e décile 43,93 € ;
  - 86,8 % des habitants vivent dans une commune au-dessus de la médiane par commune (16,64 €) ;
  - script : `PF_LeTest_TaxeFonciere_communes_2026_pondere.py`.
