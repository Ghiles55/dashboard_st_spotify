"""Page 1 - Synthèse : le message clé et les 3 KPIs, lisibles en moins de 5 secondes."""
import plotly.express as px
import streamlit as st

from utils import GRIS, ORDRE_DUREE, VERT, fmt_pct, hit_rate, load_data, sidebar_filters

st.set_page_config(page_title="Hits Spotify - Synthèse", page_icon="🎧", layout="wide")

df = load_data()
dff = sidebar_filters(df)
seuil = st.session_state["f_seuil"]

# ---- Titre = le message ----
st.title("Un hit Spotify se chante et dure moins de 4 minutes")
st.markdown(
    "**Pour la direction artistique du label :** 7 hits sur 10 durent entre 2,5 et 4 min, "
    "et un titre instrumental a 9 fois moins de chances de percer. "
    "**Privilégier des singles chantés, au format court.**"
)

if dff.empty:
    st.warning("Aucun titre ne correspond aux filtres. Élargissez la sélection.")
    st.stop()

# ---- Zone KPIs : 3 indicateurs, chacun comparé à une référence ----
court = dff[dff["format_court"]]
long_ = dff[~dff["format_court"]]
chante = dff[dff["type_voix"] == "Chanté"]
instru = dff[dff["type_voix"] == "Instrumental"]

k1, k2, k3 = st.columns(3)
k1.metric(
    f"Taux de hits (popularité ≥ {seuil})",
    fmt_pct(hit_rate(dff)),
    delta=f"{len(dff[dff['hit']]):,} hits sur {len(dff):,} titres".replace(",", " "),
    delta_color="off",
    help="Part des titres de la sélection dont la popularité atteint le seuil choisi.",
)
k2.metric(
    "Taux de hits des titres de 2,5 à 4 min",
    fmt_pct(hit_rate(court)),
    delta=f"{(hit_rate(court) - hit_rate(long_)) * 100:+.1f} pts vs autres durées ({fmt_pct(hit_rate(long_))})".replace(".", ","),
    help="Compare le format radio (2,5-4 min) à tous les autres formats.",
)
k3.metric(
    "Taux de hits des titres instrumentaux",
    fmt_pct(hit_rate(instru)),
    delta=f"{(hit_rate(instru) - hit_rate(chante)) * 100:+.1f} pts vs titres chantés ({fmt_pct(hit_rate(chante))})".replace(".", ","),
    help="Instrumental = indice 'instrumentalness' de Spotify > 0,5.",
)

st.divider()

# ---- Zone détail : 2 graphiques réactifs aux filtres ----
col_g, col_d = st.columns(2)
taux_ref = hit_rate(dff)

with col_g:
    st.subheader("Taux de hits selon la durée du titre")
    t = (dff.groupby("tranche_duree", observed=True)["hit"].agg(taux="mean", titres="size")
         .reindex(ORDRE_DUREE).dropna().reset_index())
    # Vert = tranches du format court (2,5-4 min), gris = le reste
    t["format"] = t["tranche_duree"].isin(ORDRE_DUREE[1:4]).map({True: "2,5 à 4 min", False: "Autres durées"})
    fig = px.bar(t, x="tranche_duree", y="taux", color="format", text=t["taux"].map(fmt_pct),
                 color_discrete_map={"2,5 à 4 min": VERT, "Autres durées": GRIS}, custom_data=["titres"],
                 category_orders={"tranche_duree": ORDRE_DUREE})
    fig.add_hline(y=taux_ref, line_dash="dot", line_color="black",
                  annotation_text=f"Moyenne {fmt_pct(taux_ref)}", annotation_position="top left")
    fig.update_traces(textposition="outside", cliponaxis=False, hovertemplate="%{x} : %{y:.1%} de hits<br>%{customdata[0]} titres<extra></extra>")
    fig.update_layout(xaxis_title="Durée du titre", yaxis_title="Taux de hits", yaxis_tickformat=".0%",
                      yaxis_rangemode="tozero", legend_title=None, legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, width="stretch")

with col_d:
    st.subheader("Taux de hits par genre")
    t = dff.groupby("genre")["hit"].agg(taux="mean", titres="size").sort_values("taux").reset_index()
    t["couleur"] = t["genre"].eq(t.loc[t["taux"].idxmax(), "genre"]).map({True: "Meilleur genre", False: "Autres"})
    fig2 = px.bar(t, x="taux", y="genre", orientation="h", color="couleur", text=t["taux"].map(fmt_pct),
                  color_discrete_map={"Meilleur genre": VERT, "Autres": GRIS}, custom_data=["titres"])
    fig2.add_vline(x=taux_ref, line_dash="dot", line_color="black",
                   annotation_text=f"Moyenne {fmt_pct(taux_ref)}", annotation_position="bottom right")
    fig2.update_traces(textposition="outside", cliponaxis=False,
                       hovertemplate="%{y} : %{x:.1%} de hits<br>%{customdata[0]} titres<extra></extra>")
    fig2.update_layout(xaxis_title="Taux de hits", yaxis_title=None, xaxis_tickformat=".0%",
                       xaxis_range=[0, t["taux"].max() * 1.25 if t["taux"].max() > 0 else 0.1],
                       showlegend=False)
    st.plotly_chart(fig2, width="stretch")

st.caption(
    "Axes démarrant à zéro. Popularité mesurée en janvier 2020 (photo à date, pas un cumul d'écoutes), "
    "et une association n'est pas une causalité. 👉 Page **Détail** pour comprendre, "
    "page **Tester un single** pour évaluer un projet de titre."
)
