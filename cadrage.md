# Document de cadrage — Dashboard « Hits Spotify »

**Dataset :** Spotify Songs (TidyTuesday, janvier 2020) — 32 833 lignes, soit **28 356 titres uniques** après suppression des doublons (un titre présent dans plusieurs playlists n'est compté qu'une fois). 23 variables : popularité (0-100), genre et sous-genre, date de sortie, durée, indices audio Spotify (dansabilité, énergie, instrumental…).
Sources : https://www.kaggle.com/datasets/joebeachcapital/30000-spotify-songs · https://github.com/rfordatascience/tidytuesday/tree/master/data/2020/2020-01-21

## 1. Message clé (pyramide de Minto)

> **Un hit Spotify se chante et dure moins de 4 minutes : pour maximiser ses chances, le label doit sortir en single des titres chantés au format 2,5–4 min.**

Arguments de soutien :
1. 70 % des hits (popularité ≥ 70) durent entre 2,5 et 4 min ; au-delà de 5 min le taux de hits tombe à 5,3 % (contre 10,6 % pour le format court).
2. Un instrumental a 9 fois moins de chances d'être un hit (1,1 % contre 10,1 %).
3. Tendance de fond : la durée moyenne des sorties est passée de 4 min 14 s (2000) à 3 min 14 s (2020).
4. Le genre compte aussi : 18 % de hits en pop, 1,8 % en EDM.

## 2. Audience cible

**Directeur artistique (A&R) d'un label indépendant.** Il choisit quels titres sortir en single et peut demander un « radio edit ». Il a besoin d'une règle simple et d'un outil pour tester un projet de titre, pas d'une analyse des 12 indices audio.

## 3. KPIs retenus (3 maximum)

Définition : un **hit** est un titre dont la popularité atteint le seuil choisi dans la sidebar (70 par défaut, soit environ le top 10 %).

| KPI | Contexte affiché | Pourquoi actionnable (et pas vanity) |
|---|---|---|
| **Taux de hits** de la sélection | nombre de hits / nombre de titres | Sert de référence pour tout segment filtré (genre, période). Le simple nombre de titres ou d'écoutes serait une vanity metric. |
| **Taux de hits des titres de 2,5 à 4 min** | écart en points vs les autres durées | Levier directement contrôlable par le label (montage, radio edit). |
| **Taux de hits des titres instrumentaux** | écart en points vs titres chantés | Oriente le choix des titres mis en avant (single chanté plutôt qu'instrumental). |

KPIs écartés (vanity) : nombre total de titres, popularité moyenne globale (sans comparaison), nombre d'artistes, tempo moyen (aucun lien avec la popularité, corrélation ≈ 0).

Notes d'honnêteté : la popularité est une **photo prise en janvier 2020** (pas d'historique d'écoutes) ; les écarts observés sont des **associations, pas des causalités** ; le taux de hit dépend du seuil, que l'utilisateur peut modifier.

## 4. Structure (multi-pages)

- **Sidebar commune (filtres conservés entre les pages)** : genre (multiselect), période de sortie (slider), seuil de hit (select_slider).
- **Page 1 – Synthèse** : titre = message ; 3 KPIs `st.metric` avec delta ; 2 graphiques en colonnes : taux de hits par tranche de durée (barres, format court en vert, ligne de moyenne) et par genre (barres horizontales triées, meilleur genre en vert).
- **Page 2 – Détail** (un onglet par visualisation) :
  - Durée dans le temps : courbe de la durée moyenne par année (axe à 0, bande du format 2,5–4 min)
  - Chanté vs instrumental : barres
  - Profil sonore : barres divergentes des écarts hits − autres
  - Popularité par genre : box plots (dispersion + seuil de hit)
- **Page 3 – Tester un single** : l'utilisateur décrit son titre (genre, durée, voix) → taux de hits des titres similaires vs le genre, taille d'échantillon, et les 20 hits les plus proches.

Technique : `@st.cache_data` sur le chargement, `st.columns`, `st.tabs`, dossier `pages/`, Plotly.
