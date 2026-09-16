"""Page 2 - Détail : un onglet par visualisation pour comprendre ce qui distingue un hit."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import GRIS, ROUGE, VERT, fmt_pct, hit_rate, load_data, sidebar_filters

st.set_page_config(page_title="Hits Spotify - Détail", page_icon="🔎", layout="wide")

df = load_data()
dff = sidebar_filters(df)

st.title("Les titres raccourcissent, et les hits suivent la tendance")
st.caption("Chaque onglet isole un facteur. Tous les graphiques réagissent aux filtres de la sidebar.")

if dff.empty:
    st.warning("Aucun titre ne correspond aux filtres. Élargissez la sélection.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(
    ["⏱️ Durée dans le temps", "🎤 Chanté vs instrumental", "🎛️ Profil sonore", "📊 Popularité par genre"]
)

with tab1:
    st.subheader("La durée moyenne des titres a perdu près d'une minute depuis 2000")
    # On part de 1990 : avant, trop peu de titres par année pour une moyenne fiable
    t = (dff[dff["annee"] >= 1990].groupby("annee")["duree_min"].agg(duree="mean", titres="size").reset_index())
    t = t[t["titres"] >= 30]
    if t.empty:
        st.info("Pas assez de titres par année dans la sélection (minimum 30).")
    else:
        fig = px.line(t, x="annee", y="duree", markers=True, custom_data=["titres"])
        fig.add_hrect(y0=2.5, y1=4, fillcolor=VERT, opacity=0.1, line_width=0,
                      annotation_text="Format 2,5-4 min", annotation_position="top left")
        fig.update_traces(line_color=VERT,
                          hovertemplate="%{x} : %{y:.2f} min en moyenne<br>%{customdata[0]} titres<extra></extra>")
        fig.update_layout(xaxis_title="Année de sortie", yaxis_title="Durée moyenne (min)",
                          yaxis_range=[0, max(5, t["duree"].max() * 1.1)])
        st.plotly_chart(fig, width="stretch")
        st.info("**Pourquoi une courbe ?** Le temps est continu : la pente montre la tendance. "
                "L'axe part de 0 pour ne pas exagérer la baisse. Années avec moins de 30 titres masquées.")

with tab2:
    st.subheader("Presque aucun instrumental ne devient un hit")
    t = dff.groupby("type_voix")["hit"].agg(taux="mean", titres="size").reset_index()
    fig = px.bar(t, x="type_voix", y="taux", color="type_voix", text=t["taux"].map(fmt_pct),
                 color_discrete_map={"Chanté": VERT, "Instrumental": ROUGE}, custom_data=["titres"])
    fig.update_traces(hovertemplate="%{x} : %{y:.1%} de hits<br>%{customdata[0]} titres<extra></extra>")
    fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Taux de hits",
                      yaxis_tickformat=".0%", yaxis_rangemode="tozero")
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Les instrumentaux représentent {fmt_pct((dff['type_voix'] == 'Instrumental').mean())} des titres de la sélection.")

with tab3:
    st.subheader("Écart de profil sonore entre hits et autres titres")
    variables = {"danceability": "Dansabilité", "energy": "Énergie", "valence": "Positivité",
                 "acousticness": "Acoustique", "speechiness": "Parlé", "instrumentalness": "Instrumental",
                 "liveness": "Live"}
    if dff["hit"].nunique() < 2:
        st.info("Il faut à la fois des hits et des non-hits dans la sélection.")
    else:
        moyennes = dff.groupby("hit")[list(variables)].mean().T.rename(index=variables)
        ecart = (moyennes[True] - moyennes[False]).rename("ecart").rename_axis("variable").reset_index().sort_values("ecart")
        ecart["sens"] = ecart["ecart"].gt(0).map({True: "Plus présent chez les hits", False: "Moins présent chez les hits"})
        fig = px.bar(ecart, x="ecart", y="variable", orientation="h", color="sens",
                     color_discrete_map={"Plus présent chez les hits": VERT, "Moins présent chez les hits": ROUGE},
                     text=ecart["ecart"].map(lambda v: f"{v:+.3f}".replace(".", ",")))
        fig.add_vline(x=0, line_color="black")
        fig.update_traces(hovertemplate="%{y} : écart %{x:+.3f}<extra></extra>")
        fig.update_layout(xaxis_title="Écart de moyenne (hits − autres), indices de 0 à 1",
                          yaxis_title=None, legend_title=None, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, width="stretch")
        st.info("**Pourquoi des barres divergentes ?** On compare un écart à zéro : le sens (couleur) "
                "et l'ampleur (longueur) se lisent immédiatement. Les écarts restent faibles hors 'Instrumental' : "
                "le son compte moins que le format.")

with tab4:
    st.subheader("Distribution de la popularité par genre")
    ordre = dff.groupby("genre")["track_popularity"].median().sort_values(ascending=False).index.tolist()
    fig = px.box(dff, x="genre", y="track_popularity", category_orders={"genre": ordre},
                 color_discrete_sequence=[GRIS], points=False)
    fig.add_hline(y=st.session_state["f_seuil"], line_dash="dot", line_color=VERT,
                  annotation_text="Seuil de hit", annotation_position="top right")
    fig.update_layout(xaxis_title=None, yaxis_title="Popularité Spotify (0-100)", yaxis_range=[0, 100])
    st.plotly_chart(fig, width="stretch")
    st.info("**Pourquoi un box plot ?** La moyenne cache la dispersion : on voit médiane, quartiles "
            "et la part de chaque genre au-dessus du seuil de hit. Genres triés par médiane.")
