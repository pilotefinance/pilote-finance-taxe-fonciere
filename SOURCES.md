# SOURCES — d'où vient chaque chiffre

Deux familles de sources : les **données** sur lesquelles tourne le calcul, redistribuées ici sans
modification, et les **textes officiels et la presse** cités dans la vidéo, qui ne sont pas
redistribués (avec le lien quand nous l'avons conservé, et la date de lecture).

## Les données du calcul, redistribuées dans `donnees/`

Téléchargées le **25/09/2026 entre 21h19 et 21h20** (heure de Paris, horodatage des fichiers),
**après** que le protocole a été figé, à 21h18. Aucune n'a été modifiée : ce sont les fichiers tels
que téléchargés (le tableur des intercommunalités tel qu'extrait de son archive, l'archive des
populations renommée à l'enregistrement), et leurs empreintes SHA-256 sont vérifiées à chaque passage
de la CI (`EMPREINTES.json`).

| Fichier | Producteur et jeu de données | Version | Octets | SHA-256 |
|---|---|---|---|---|
| `descriptif-tarifs-des-locaux-d-habitation_2024.csv` | DGFiP (Ministères économiques et financiers), « Taxe foncière sur les propriétés bâties - Tarifs des locaux d'habitation 2024 » | mis à jour le 24/04/2025 ; tarifs de 1970 au m², situation au 01/01/2024 | 18 034 931 | `fc4b5ebf612f62fa6a9260cacd02235e39290daed51c79b11a3570bc79047777` |
| `Taux_2026_communes.xlsx` | DGFiP, taux votés en 2026 par les communes | publiés le 27/08/2026 | 1 868 827 | `697c10f3e61aa96a51557c46623466cfb3c7e6ac67efed177af8a558e89f1c54` |
| `Taux_2026_EPCI.xlsx` | DGFiP, taux votés en 2026 par les intercommunalités | publiés le 27/08/2026 | 111 691 | `a0a7aa092d0888d644ca1857bdac2b3b7f7d38bfd0e3f95d034dc6880d3598c2` |
| `EPCI_au_01-01-2026.xlsx` | Insee, « Base des EPCI à fiscalité propre au 1er janvier 2026 » (composition communale) | tableur extrait de l'archive `epci_au_01-01-2026.zip` | 1 270 004 | `7a3156cf6984f0b70b8fba1243b7f16feed7e16eb37b4b5e8426f1f78d51186a` |
| `insee_populations_2023_ensemble.zip` | Insee, « Populations de référence 2023 », fichier d'ensemble (CSV compressé) | paru le 18/12/2025 ; populations en vigueur au 01/01/2026 ; archive `ensemble.zip`, renommée à l'enregistrement | 1 032 385 | `5174fc225398a4c072fb8bb5298b7ccf30c017834c7a4171f44787379d83b3f5` |

### Où les retrouver, et à quelles conditions

Pages vérifiées le 27/09/2026.

- **Tarifs** : [data.gouv.fr](https://www.data.gouv.fr/datasets/taxe-fonciere-sur-les-proprietes-baties-tarifs-des-locaux-dhabitation-2024),
  jeu issu de [data.economie.gouv.fr](https://data.economie.gouv.fr/explore/dataset/descriptif-tarifs-des-locaux-d-habitation_2024/).
  Licence Ouverte / Open Licence version 2.0. Source : DGFiP, Ministères économiques et
  financiers, mise à jour du 24/04/2025.
- **Taux 2026** : [impots.gouv.fr, « Analyses de la DGFiP sur la fiscalité directe locale - année 2026 »](https://www.impots.gouv.fr/analyses-de-la-dgfip-sur-la-fiscalite-directe-locale-annee-2026).
  La page ne mentionne pas de licence, mais les [mentions légales d'impots.gouv.fr](https://www.impots.gouv.fr/mentions-legales)
  placent les informations du site sous licence ouverte Etalab 2.0, sauf propriété intellectuelle
  de tiers : réutilisation libre, avec mention de la source et de la date de dernière mise à jour (à
  défaut de licence, c'est l'[article L322-1 du code des relations entre le public et l'administration](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000032255220)
  qui s'appliquerait). Nous les redistribuons sans aucune modification. Source : DGFiP, 27/08/2026.
- **Intercommunalités** : [insee.fr, « Intercommunalité »](https://www.insee.fr/fr/information/2510634),
  archive `epci_au_01-01-2026.zip` (1 106 611 octets, SHA-256
  `14f8236d99904c7781eee8e293c0f1a6c428c2e35e047d57ac90a356319dfe32`, elle ne contient que ce
  tableur), page mise à jour le 13/03/2026. Seul le tableur est redistribué ici. Source : Insee.
- **Populations** : [insee.fr, « Téléchargement du fichier d'ensemble des populations en 2023 »](https://www.insee.fr/fr/statistiques/8680726),
  paru le 18/12/2025, lien « CSV compressé » (`ensemble.zip`). Source : Insee.
- **Données de l'Insee** : Licence Ouverte / Open Licence version 2.0, avec la mention « Source :
  Insee » et la date de mise à jour ([conditions d'utilisation des données de l'Insee](https://www.insee.fr/fr/information/2381863)).

## Les textes officiels et la presse cités, non redistribués

Consultés le 25/09/2026 ; A15144, A17727, A19047 et la FAQ impots.gouv.fr relues le 27/09/2026.

**Le calcul et le barème**
- DGFiP, brochure pratique [« Impôts locaux 2026 »](https://www.impots.gouv.fr/www2/fichiers/documentation/brochure/idl/idl_2026.pdf),
  PDF de 240 pages. Pages du PDF utilisées : 8, 21 à 26, 43 à 45, 53, 75, 76, 80, 81, 84, 209 (le
  numéro imprimé sur la page est inférieur d'une unité).
- Code général des impôts, annexe III, [art. 324 T](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037128007)
  (équivalences superficielles : le barème) et [art. 324 O](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037128009)
  (pondération de la surface).
- BOFiP [BOI-IF-TFB-20-10-20-50](https://bofip.impots.gouv.fr/bofip/2373-PGP.html/identifiant=BOI-IF-TFB-20-10-20-50-20121210),
  § 500 à 510 : le chauffage central.
- [Documentation administrative de base 6 M 2222, datée du 12/02/1970](https://bofip-archives.impots.gouv.fr/bofip/29796-AIDA.html/identifiant=6M2222-19700212)
  (archives du BOFiP) : la conversion des équipements en mètres carrés pondérés, déjà appliquée lors
  de la révision de 1970 (la page renvoie, pour le barème, au décret du 28/11/1969).
- impots.gouv.fr, FAQ [« Comment est calculée ma taxe foncière ? Pourquoi a-t-elle augmenté en 2026 ? »](https://www.impots.gouv.fr/particulier/questions/comment-est-calculee-ma-taxe-fonciere-pourquoi-t-elle-augmente-en-2026),
  modifiée le 03/09/2026 : revalorisation de + 0,8 % en 2026.
- DGFiP, [étude des taux de fiscalité directe locale votés en 2026](https://www.collectivites-locales.gouv.fr/actualites/publication-dune-etude-sur-les-taux-de-fiscalite-directe-locale-votes-en-2026-par-les-communes-et).

**L'actualité des éléments de confort**
- Sénat, [question d'actualité n° 0567G](https://www.senat.fr/questions/base/2025/qSEQ25110567G.html),
  JO Sénat du 27/11/2025, p. 9732.
- Sénat, [question écrite n° 06871](https://www.senat.fr/questions/base/2025/qSEQ251206871.html),
  JO Sénat du 04/12/2025, p. 5879 ; réponse au JO Sénat du 14/05/2026, p. 2374.
- Assemblée nationale, [question écrite n° 11327](https://www.assemblee-nationale.fr/dyn/17/questions/QANR5L17QE11327),
  réponse au JO du 19/05/2026, p. 4401.
- Sénat, [question orale n° 1237S](https://www.senat.fr/questions/base/2026/qSEQ26071237S.html),
  réponse en séance le 21/07/2026, JO Sénat du 22/07/2026, p. 6142.
- Estimation attribuée à Bercy (7,4 millions de logements, 63 € de hausse en moyenne) : TF1info/AFP
  du 18/11/2025, reprise dans la question écrite n° 06871 ci-dessus (« selon les estimations du
  ministère »).
- « Selon la presse locale, des conseils municipaux s'en sont saisis en septembre » : La République
  des Pyrénées du 20/09/2026 et La Dépêche du 07/09/2026.

**Les règles pratiques de 2026**
- service-public.gouv.fr, [A19047](https://www.service-public.gouv.fr/particuliers/actualites/A19047)
  du 24/08/2026 : exonération et dégrèvement liés à l'âge.
- service-public.gouv.fr, [A15144](https://www.service-public.gouv.fr/particuliers/actualites/A15144),
  mise à jour le 22/09/2026 : dates et moyens de paiement.
- service-public.gouv.fr, [A17727](https://www.service-public.gouv.fr/particuliers/actualites/A17727),
  mise à jour le 08/09/2026 : fiche d'évaluation et réclamation.
- service-public.gouv.fr, [A18426](https://www.service-public.gouv.fr/particuliers/actualites/A18426)
  du 22/07/2026 : l'outil « Fiscalité locale des particuliers ».
- impots.gouv.fr, [date limite de paiement en ligne du 20/10/2026](https://www.impots.gouv.fr/part-20102026-taxes-foncieres-date-limite-de-paiement-par-internet-smartphone-ou-tablette).
