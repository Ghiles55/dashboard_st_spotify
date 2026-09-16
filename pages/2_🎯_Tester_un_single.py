"""Page 3 - Action : évaluer un projet de single en le comparant aux titres similaires."""
import streamlit as st

from utils import GENRES, fmt_min, fmt_pct, hit_rate, load_data, sidebar_filters

st.set_page_config(page_title="Hits Spotify - Tester un single", page_icon="🎯", layout="wide")

df = load_data()
dff = sidebar_filters(df)  # on garde le seuil et la période de la sidebar

st.title("Ce projet de single a-t-il le profil d'un hit ?")
st.markdown("Décrivez le titre : on calcule le taux de hits des **titres similaires** déjà sortis "
            "(même genre, durée proche à ± 30 s, même type de voix).")

c1, c2, c3 = st.columns(3)
genre = c1.selectbox("Genre du titre", list(GENRES.values()))
duree = c2.slider("Durée prévue (min)", 1.5, 7.0, 3.5, step=0.25)
voix = c3.radio("Voix", ["Chanté", "Instrumental"], horizontal=True)

# Filtre "titres similaires" : les données de la sidebar (période + seuil) sont conservées
base = df[df["annee"].between(*st.session_state["f_annees"])].copy()
base["hit"] = base["track_popularity"] >= st.session_state["f_seuil"]
meme_genre = base[base["genre"] == genre]
similaires = meme_genre[meme_genre["duree_min"].between(duree - 0.5, duree + 0.5) & (meme_genre["type_voix"] == voix)]

k1, k2 = st.columns(2)
k1.metric("Taux de hits des titres similaires", fmt_pct(hit_rate(similaires)),
          delta=f"{(hit_rate(similaires) - hit_rate(meme_genre)) * 100:+.1f} pts vs le genre {genre} ({fmt_pct(hit_rate(meme_genre))})".replace(".", ","))
k2.metric("Titres similaires trouvés", f"{len(similaires)}",
          delta="échantillon faible, prudence" if len(similaires) < 50 else "échantillon suffisant",
          delta_color="inverse" if len(similaires) < 50 else "normal")

st.subheader("Les hits les plus proches de ce profil")
tableau = (similaires[similaires["hit"]].sort_values("track_popularity", ascending=False)
           .head(20)
           .assign(duree=lambda d: d["duree_min"].map(fmt_min))
           [["track_name", "track_artist", "annee", "duree", "track_popularity"]]
           .rename(columns={"track_name": "Titre", "track_artist": "Artiste", "annee": "Année",
                            "duree": "Durée", "track_popularity": "Popularité"}))
if tableau.empty:
    st.info("Aucun hit avec ce profil sur la période : c'est en soi un signal d'alerte.")
else:
    st.dataframe(tableau, width="stretch", hide_index=True)
st.caption("Outil d'aide à la décision fondé sur l'historique, pas une prédiction : un titre reste unique.")
