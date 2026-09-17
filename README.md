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

## Lien de déploiement 

https://dashboardstspotify-qrjlk7k9vchcvxhjr6xdzn.streamlit.app/
