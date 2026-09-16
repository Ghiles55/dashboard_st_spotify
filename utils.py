"""Fonctions partagées par toutes les pages : chargement des données, filtres, formats."""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "spotify_songs.csv"

# Palette : gris pour le contexte, vert pour ce qui doit attirer l'oeil (canal pré-attentif)
GRIS = "#B0B7C3"
VERT = "#1A9E4B"
ROUGE = "#D62728"

ORDRE_DUREE = ["< 2,5 min", "2,5-3 min", "3-3,5 min", "3,5-4 min", "4-5 min", "> 5 min"]
GENRES = {"pop": "Pop", "rap": "Rap", "rock": "Rock", "latin": "Latin", "r&b": "R&B", "edm": "EDM"}


@st.cache_data
def load_data() -> pd.DataFrame:
    """Lit le CSV une seule fois (mis en cache) et prépare les colonnes utiles."""
    df = pd.read_csv(DATA_PATH)

    # Un même titre peut apparaître dans plusieurs playlists : on garde 1 ligne par titre
    # (sinon les titres présents dans 5 playlists compteraient 5 fois)
    df = df.drop_duplicates(subset="track_id").copy()

    # Dates de sortie hétérogènes ("2019-06-14", "2012", "2012-01") -> on garde l'année
    df["annee"] = pd.to_datetime(df["track_album_release_date"], errors="coerce", format="mixed").dt.year
    df = df.dropna(subset=["annee"])
    df["annee"] = df["annee"].astype(int)

    df["genre"] = df["playlist_genre"].map(GENRES)
    df["duree_min"] = df["duration_ms"] / 60000
    df["tranche_duree"] = pd.cut(
        df["duree_min"], bins=[0, 2.5, 3, 3.5, 4, 5, 100], labels=ORDRE_DUREE, right=False
    )
    df["format_court"] = df["duree_min"].between(2.5, 4, inclusive="left")
    # Convention Spotify : instrumentalness > 0.5 = probablement sans voix
    df["type_voix"] = (df["instrumentalness"] > 0.5).map({True: "Instrumental", False: "Chanté"})
    return df


FILTER_KEYS = ["f_genre", "f_annees", "f_seuil"]


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Affiche les filtres dans la sidebar, ajoute la colonne 'hit' et renvoie le DataFrame filtré.

    Les valeurs sont conservées d'une page à l'autre grâce à st.session_state.
    """
    defauts = {
        "f_genre": list(GENRES.values()),
        "f_annees": (int(df["annee"].min()), int(df["annee"].max())),
        "f_seuil": 70,
    }
    for key in FILTER_KEYS:
        # Réassigner la valeur empêche Streamlit de l'effacer au changement de page
        st.session_state[key] = st.session_state.get(key, defauts[key])

    st.sidebar.header("Filtres")
    genres = st.sidebar.multiselect("Genre", list(GENRES.values()), key="f_genre")
    annee_min, annee_max = st.sidebar.slider(
        "Année de sortie", int(df["annee"].min()), int(df["annee"].max()), key="f_annees"
    )
    seuil = st.sidebar.select_slider(
        "Seuil de popularité d'un « hit »", options=[50, 60, 70, 80, 90], key="f_seuil",
        help="Popularité Spotify de 0 à 100. À 70, environ 1 titre sur 10 est un hit.",
    )

    dff = df[df["genre"].isin(genres) & df["annee"].between(annee_min, annee_max)].copy()
    dff["hit"] = dff["track_popularity"] >= seuil

    st.sidebar.caption(f"{len(dff):,} titres sélectionnés sur {len(df):,}".replace(",", " "))
    st.sidebar.caption("Source : Spotify via TidyTuesday (janv. 2020), 1 ligne par titre.")
    return dff


def hit_rate(data: pd.DataFrame) -> float:
    """Taux de hits ; NaN si aucun titre (évite une division par zéro)."""
    return data["hit"].mean() if len(data) else float("nan")


def fmt_pct(x: float) -> str:
    return "—" if pd.isna(x) else f"{x:.1%}".replace(".", ",")


def fmt_min(x: float) -> str:
    """3.29 -> '3 min 17 s'."""
    if pd.isna(x):
        return "—"
    m, s = divmod(round(x * 60), 60)
    return f"{m} min {s:02d} s"
