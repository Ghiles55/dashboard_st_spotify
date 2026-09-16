# Dashboard Hits Spotify (Streamlit)

## Lancer en local
```bash
pip install -r requirements.txt
streamlit run Synthèse.py
```

## Arborescence
```
Synthèse.py                  # page d'accueil : message + KPIs
pages/1_🔎_Détail.py          # un onglet par visualisation
pages/2_🎯_Tester_un_single.py  # outil d'aide au choix d'un single
utils.py                     # chargement (@st.cache_data), filtres sidebar, formats
data/spotify_songs.csv
cadrage.md
requirements.txt
```

## Déploiement Streamlit Community Cloud
1. Créer un repo GitHub et y pousser ce dossier (`git init && git add . && git commit -m "dashboard" && git push`).
2. Aller sur https://share.streamlit.io → *Create app* → choisir le repo, branche `main`, fichier principal `Synthèse.py`.
3. *Deploy* → copier le lien `https://<nom>.streamlit.app` ici :

**Lien de déploiement :** _à compléter_

Données : Spotify Songs (TidyTuesday) — https://www.kaggle.com/datasets/joebeachcapital/30000-spotify-songs
