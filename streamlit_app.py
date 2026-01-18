import streamlit as st
import pandas as pd

#HIlfsfunktion
def zeige_spalten(df, spalten_liste):
    vorhandene = [c for c in spalten_liste if c in df.columns]
    return df[vorhandene]



st.title("Baumarten-Analyse & Empfehlungstool für die Stadt Zug")

st.write(
    "Interaktive Oberfläche für die Python-basierte "
    "Analyse und Empfehlung von Baumarten."
)

@st.cache_data
def lade_daten():
    df = pd.read_csv(
        "art_merged.csv",
        sep=";",
        encoding="latin1"
    )
    return df

art_merged = lade_daten()

def Baumart(art_name):
    """
    Eingabe: wissenschaftlicher Artenname
    Ausgabe: DataFrame mit Art-Steckbrief
    """

    # 1) Exakte Übereinstimmung
    mask_exact = art_merged["scientific_name"].str.lower() == art_name.lower()
    treffer = art_merged[mask_exact]

    # 2) Fallback: Teiltreffer
    if treffer.empty:
        treffer = art_merged[
            art_merged["scientific_name"].str.contains(
                art_name, case=False, na=False
            )
        ]

    # 3) Wenn leer → None zurückgeben
    if treffer.empty:
        return None

    # 4) Spaltenauswahl
    spalten = [
        "scientific_name", "genus", "family",
        "count_species_total", "pct_species_total",
        "count_species_park", "pct_species_park",
        "count_species_street", "pct_species_street",
        "biodiv_index", "growth_type",
        "s_MEAN_dbh_cm", "s_MEAN_height_m", "s_MEAN_crown_m", "s_MEAN_age",
        "s_MEDIAN_dbh_cm", "s_MEDIAN_height_m", "s_MEDIAN_crown_m",
        "s_MAX_dbh_cm", "s_MAX_height_m", "s_MAX_crown_m",
        "p_MEAN_dbh_cm", "p_MEAN_height_m", "p_MEAN_crown_m", "p_MEAN_age",
        "p_MEDIAN_dbh_cm", "p_MEDIAN_height_m", "p_MEDIAN_crown_m",
        "p_MAX_dbh_cm", "p_MAX_height_m", "p_MAX_crown_m",
        "pct_genus_all", "pct_family_all"
    ]

    # 5) Anzeigenamen
    anzeige_namen = {
        "scientific_name": "Art",
        "genus": "Gattung",
        "family": "Familie",
        "count_species_total": "Anzahl gesamt",
        "pct_species_total": "Artanteil gesamt (%)",
        "count_species_park": "Anzahl Park",
        "pct_species_park": "Artanteil Park (%)",
        "count_species_street": "Anzahl Strasse",
        "pct_species_street": "Artanteil Strasse (%)",
        "biodiv_index": "Biodiversitätsindex",
        "growth_type": "Wachstumstyp",
        "pct_genus_all": "Gattungsanteil gesamt (%)",
        "pct_family_all": "Familienanteil gesamt (%)"
    }

    anzeige_df = treffer[spalten].rename(columns=anzeige_namen).round(2)

    return anzeige_df

#Eingabefenster
st.divider()
st.subheader("Art-Steckbrief")

art_input = st.text_input(
    "Wissenschaftlichen Artnamen eingeben (z. B. Acer campestre):"
)

if art_input:
    ergebnis = Baumart(art_input)

    if ergebnis is None:
        st.warning("Keine passende Baumart gefunden.")
    else:
        st.dataframe(ergebnis)


def Baumgattung(genus_name):
    """
    Eingabe: Gattungsname, z.B. "Acer"
    Ausgabe:
    - Gattungsüberblick (DataFrame)
    - Artenliste der Gattung (DataFrame)
    """

    # 1) Alle Arten dieser Gattung auswählen
    mask = art_merged["genus"].str.lower() == genus_name.lower()
    treffer = art_merged[mask]

    # 2) Falls keine Treffer
    if treffer.empty:
        return None, None

    # -------------------------
    # TEIL A: GATTUNGS-ÜBERBLICK
    # -------------------------
    gattung_ueberblick = (
        treffer[["genus", "pct_genus_all", "pct_genus_park", "pct_genus_street"]]
        .head(1)
        .rename(columns={
            "genus": "Gattung",
            "pct_genus_all": "Gattungsanteil gesamt (%)",
            "pct_genus_park": "Gattungsanteil Park (%)",
            "pct_genus_street": "Gattungsanteil Strasse (%)"
        })
        .round(2)
    )

    # -------------------------
    # TEIL B: ARTEN DER GATTUNG
    # -------------------------
    arten_tabelle = (
        treffer[[
            "scientific_name",
            "count_species_total",
            "pct_species_total",
            "biodiv_index",
            "growth_type"
        ]]
        .rename(columns={
            "scientific_name": "Art (wissenschaftlich)",
            "count_species_total": "Anzahl gesamt",
            "pct_species_total": "Artanteil gesamt (%)",
            "biodiv_index": "Biodiversitätsindex",
            "growth_type": "Wachstumstyp"
        })
        .round(2)
    )

    return gattung_ueberblick, arten_tabelle

#Eingabefenster
st.divider()
st.subheader("Gattungs-Steckbrief")

gattung_input = st.text_input(
    "Wissenschaftlichen Gattungsnamen eingeben (z. B. Acer):",
    key="gattung"
)

if gattung_input:
    ueberblick, arten = Baumgattung(gattung_input)

    if ueberblick is None:
        st.warning("Keine passende Gattung gefunden.")
    else:
        st.markdown("### Gattungs-Überblick")
        st.dataframe(ueberblick)

        st.markdown("### Vorkommende Arten der Gattung")
        st.dataframe(arten)

########################
# FAMILIENEBENE
########################
def Baumfamilie(family_name):
    """
    Eingabe: Familienname, z.B. "Sapindaceae"
    Ausgabe:
    - Familien-Überblick (DataFrame)
    - Artenliste der Familie (DataFrame)
    """

    # 1) Alle Arten dieser Familie auswählen
    mask = art_merged["family"].str.lower() == family_name.lower()
    treffer = art_merged[mask]

    # 2) Falls keine Treffer
    if treffer.empty:
        return None, None

    # -------------------------------
    # TEIL A: FAMILIEN-ÜBERBLICK
    # -------------------------------
    familien_ueberblick = (
        treffer[[
            "family",
            "pct_family_all",
            "pct_family_park",
            "pct_family_street"
        ]]
        .head(1)
        .rename(columns={
            "family": "Familie",
            "pct_family_all": "Familienanteil gesamt (%)",
            "pct_family_park": "Familienanteil Park (%)",
            "pct_family_street": "Familienanteil Strasse (%)"
        })
        .round(2)
    )

    # -------------------------------
    # TEIL B: ARTEN DER FAMILIE
    # -------------------------------
    arten_tabelle = (
        treffer[[
            "scientific_name",
            "genus",
            "count_species_total",
            "pct_species_total",
            "biodiv_index",
            "growth_type"
        ]]
        .rename(columns={
            "scientific_name": "Art (wissenschaftlich)",
            "genus": "Gattung",
            "count_species_total": "Anzahl gesamt",
            "pct_species_total": "Artanteil gesamt (%)",
            "biodiv_index": "Biodiversitätsindex",
            "growth_type": "Wachstumstyp"
        })
        .round(2)
    )

    return familien_ueberblick, arten_tabelle

#Eingabefenster
st.divider()
st.subheader("Familien-Steckbrief")

familie_input = st.text_input(
    "Wissenschaftlichen Familiennamen eingeben (z. B. Sapindaceae):",
    key="familie"
)

if familie_input:
    ueberblick, arten = Baumfamilie(familie_input)

    if ueberblick is None:
        st.warning("Keine passende Familie gefunden.")
    else:
        st.markdown("### Familien-Überblick")
        st.dataframe(ueberblick)

        st.markdown("### Arten der Familie")
        st.dataframe(arten)

#################

### KOMPLEXERE ABFRAGEN
#################

# 5.1 Top-n Arten mit höchstem Biodiversitätsindex
def Top_10_Baumarten(n=10):
    """
    Gibt die Top-n Arten mit dem höchsten Biodiversitätsindex aus.
    """

    df = art_merged.copy()

    # Nur Arten mit gültigem Biodiversitätsindex
    df = df[df["biodiv_index"].notna()]

    # Sortieren (absteigend)
    df = df.sort_values(by="biodiv_index", ascending=False)

    # Top n auswählen
    top = df.head(n)

    spalten = [
        "scientific_name",
        "genus",
        "family",
        "biodiv_index",
        "pct_species_total",
        "pct_genus_all",
        "pct_family_all"
    ]

    anzeige_namen = {
        "scientific_name": "Art",
        "genus": "Gattung",
        "family": "Familie",
        "biodiv_index": "Biodiversitätsindex",
        "pct_species_total": "Artanteil gesamt (%)",
        "pct_genus_all": "Gattungsanteil gesamt (%)",
        "pct_family_all": "Familienanteil gesamt (%)"
    }

    out = zeige_spalten(top, spalten).rename(columns=anzeige_namen).round(2)

    return out

st.divider()
st.subheader("Top 10 Baumarten mit höchstem Biodiversitätsindex")

top10 = Top_10_Baumarten()

st.dataframe(top10)

# 5.2 Top-n Arten mit tiefstem Biodiversitätsindex
def Bottom_10_Baumarten(n=10):
    """
    Gibt die Top-n Arten mit dem tiefsten Biodiversitätsindex aus.
    """

    df = art_merged.copy()
    df = df[df["biodiv_index"].notna()]

    df = df.sort_values(by="biodiv_index", ascending=True)
    bottom = df.head(n)

    spalten = [
        "scientific_name",
        "genus",
        "family",
        "biodiv_index",
        "pct_species_total",
        "pct_genus_all",
        "pct_family_all"
    ]

    anzeige_namen = {
        "scientific_name": "Art",
        "genus": "Gattung",
        "family": "Familie",
        "biodiv_index": "Biodiversitätsindex",
        "pct_species_total": "Artanteil gesamt (%)",
        "pct_genus_all": "Gattungsanteil gesamt (%)",
        "pct_family_all": "Familienanteil gesamt (%)"
    }

    out = zeige_spalten(bottom, spalten).rename(columns=anzeige_namen).round(2)

    return out

#Visualisation
st.divider()
st.subheader("Top 10 Baumarten mit tiefstem Biodiversitätsindex")

bottom10 = Bottom_10_Baumarten()
st.dataframe(bottom10)

def Baumarten_über_10_Prozent():
    """
    Arten mit >10 % Anteil 
    """

    df = art_merged.copy()

    df = df[
        (df["pct_species_park"] > 10) |
        (df["pct_species_street"] > 10) |
        (df["pct_species_total"] > 10)
    ]

    out = (
        df[[
            "scientific_name",
            "pct_species_park",
            "pct_species_street",
            "pct_species_total"
        ]]
        .rename(columns={
            "scientific_name": "Art (wissenschaftlich)",
            "pct_species_park": "Artanteil Park (%)",
            "pct_species_street": "Artanteil Strasse (%)",
            "pct_species_total": "Artanteil Stadtweit (%)"
        })
        .round(2)
    )

    return out

#visualisation
st.divider()
st.subheader("Baumarten >10 % Anteil (10/20/30-Regel)")

st.dataframe(Baumarten_über_10_Prozent())

def Baumgattungen_über_20_prozent():
    """
    Gattungen mit >20 % Anteil
    """

    df = art_merged.copy()

    df = df[
        (df["pct_genus_park"] > 20) |
        (df["pct_genus_street"] > 20) |
        (df["pct_genus_all"] > 20)
    ]

    out = (
        df[[
            "genus",
            "pct_genus_park",
            "pct_genus_street",
            "pct_genus_all"
        ]]
        .drop_duplicates(subset=["genus"])
        .rename(columns={
            "genus": "Gattung",
            "pct_genus_park": "Gattungsanteil Park (%)",
            "pct_genus_street": "Gattungsanteil Strasse (%)",
            "pct_genus_all": "Gattungsanteil Stadtweit (%)"
        })
        .round(2)
    )

    return out

#visualisation
st.divider()
st.subheader("Baumgattungen >20 % Anteil")

st.dataframe(Baumgattungen_über_20_prozent())

def Baumfamilien_nah_an_30_Prozent():
    """
    Häufigste Baumfamilie:
    - stadtweit
    - im Park
    - an der Strasse
    """

    df = art_merged.copy()

    top_all = (
        df.sort_values("pct_family_all", ascending=False)
          [["family", "pct_family_all"]]
          .drop_duplicates()
          .head(1)
          .rename(columns={
              "family": "Familie",
              "pct_family_all": "Anteil Stadtweit (%)"
          })
          .round(2)
    )

    top_park = (
        df.sort_values("pct_family_park", ascending=False)
          [["family", "pct_family_park"]]
          .drop_duplicates()
          .head(1)
          .rename(columns={
              "family": "Familie",
              "pct_family_park": "Anteil Park (%)"
          })
          .round(2)
    )

    top_street = (
        df.sort_values("pct_family_street", ascending=False)
          [["family", "pct_family_street"]]
          .drop_duplicates()
          .head(1)
          .rename(columns={
              "family": "Familie",
              "pct_family_street": "Anteil Strasse (%)"
          })
          .round(2)
    )

    return top_all, top_park, top_street

#Visualisation
st.divider()
st.subheader("Baumfamilien nahe an der 30-%-Grenze")

st.write("10/20/30-Regel wird eingehalten – häufigste Familie:")

stadt, park, strasse = Baumfamilien_nah_an_30_Prozent()

st.markdown("**Stadtweit**")
st.dataframe(stadt)

st.markdown("**Park**")
st.dataframe(park)

st.markdown("**Strasse**")
st.dataframe(strasse)

# 5.4 Hochwertig UND selten
def Hochwertige_und_seltene_Baumarten(index_schwelle=4, selten_schwelle=5):
    """
    Arten mit hohem Biodiversitätsindex UND geringem Artanteil
    (gesamt, Park, Strasse).
    """

    df = art_merged.copy()

    # --- Gesamt ---
    gesamt = (
        df[
            (df["biodiv_index"].notna()) &
            (df["biodiv_index"] >= index_schwelle) &
            (df["pct_species_total"] < selten_schwelle)
        ][[
            "scientific_name",
            "biodiv_index",
            "pct_species_total"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_total": "Artanteil gesamt (%)"
        })
        .round(2)
    )

    # --- Park ---
    park = (
        df[
            (df["biodiv_index"].notna()) &
            (df["biodiv_index"] >= index_schwelle) &
            (df["pct_species_park"] < selten_schwelle)
        ][[
            "scientific_name",
            "biodiv_index",
            "pct_species_park"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_park": "Artanteil Park (%)"
        })
        .round(2)
    )

    # --- Strasse ---
    strasse = (
        df[
            (df["biodiv_index"].notna()) &
            (df["biodiv_index"] >= index_schwelle) &
            (df["pct_species_street"] < selten_schwelle)
        ][[
            "scientific_name",
            "biodiv_index",
            "pct_species_street"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_street": "Artanteil Strasse (%)"
        })
        .round(2)
    )

    return gesamt, park, strasse

st.divider()
st.subheader("Hochwertige UND seltene Baumarten")

gesamt, park, strasse = Hochwertige_und_seltene_Baumarten()

st.markdown("**Stadtweit**")
st.dataframe(gesamt)

st.markdown("**Park**")
st.dataframe(park)

st.markdown("**Strasse**")
st.dataframe(strasse)

# 5.5 Hochwertig UND häufig
def Hochwertige_und_häufige_Baumarten(index_schwelle=4, haeufig_schwelle=5):
    """
    Arten mit hohem Biodiversitätsindex UND hohem Artanteil
    (gesamt, Park, Strasse).
    """

    df = art_merged.copy()

    # --- Gesamt ---
    gesamt = (
        df[
            (df["biodiv_index"].notna()) &
            (df["biodiv_index"] >= index_schwelle) &
            (df["pct_species_total"] >= haeufig_schwelle)
        ][[
            "scientific_name",
            "biodiv_index",
            "pct_species_total"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_total": "Artanteil gesamt (%)"
        })
        .round(2)
    )

    # --- Park ---
    park = (
        df[
            (df["biodiv_index"].notna()) &
            (df["biodiv_index"] >= index_schwelle) &
            (df["pct_species_park"] >= haeufig_schwelle)
        ][[
            "scientific_name",
            "biodiv_index",
            "pct_species_park"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_park": "Artanteil Park (%)"
        })
        .round(2)
    )

    # --- Strasse ---
    strasse = (
        df[
            (df["biodiv_index"].notna()) &
            (df["biodiv_index"] >= index_schwelle) &
            (df["pct_species_street"] >= haeufig_schwelle)
        ][[
            "scientific_name",
            "biodiv_index",
            "pct_species_street"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_street": "Artanteil Strasse (%)"
        })
        .round(2)
    )

    return gesamt, park, strasse

st.divider()
st.subheader("Hochwertige UND häufige Baumarten")

gesamt, park, strasse = Hochwertige_und_häufige_Baumarten()

st.markdown("**Stadtweit**")
st.dataframe(gesamt)

st.markdown("**Park**")
st.dataframe(park)

st.markdown("**Strasse**")
st.dataframe(strasse)

def Empfohlene_Baumarten_Stadtweit():
    df = art_merged.copy()

    df = df[
        (df["biodiv_index"].notna()) &
        (df["biodiv_index"] >= 4) &
        (df["pct_species_total"] < 5) &
        (df["pct_genus_all"] <= 20) &
        (df["pct_family_all"] <= 30)
    ]

    out = (
        df[[
            "scientific_name",
            "genus",
            "family",
            "biodiv_index",
            "pct_species_total"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "genus": "Gattung",
            "family": "Familie",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_total": "Artanteil gesamt (%)"
        })
        .round(2)
    )

    return out

def Empfohlene_Baumarten_Park():
    df = art_merged.copy()

    df = df[
        (df["biodiv_index"].notna()) &
        (df["biodiv_index"] >= 4) &
        (df["pct_species_park"] < 5) &
        (df["pct_genus_park"] <= 20) &
        (df["pct_family_park"] <= 30)
    ]

    out = (
        df[[
            "scientific_name",
            "genus",
            "family",
            "biodiv_index",
            "pct_species_park"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "genus": "Gattung",
            "family": "Familie",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_park": "Artanteil Park (%)"
        })
        .round(2)
    )

    return out

def Empfohlene_Baumarten_Strasse():
    df = art_merged.copy()

    df = df[
        (df["biodiv_index"].notna()) &
        (df["biodiv_index"] >= 4) &
        (df["pct_species_street"] < 5) &
        (df["pct_genus_street"] <= 20) &
        (df["pct_family_street"] <= 30)
    ]

    out = (
        df[[
            "scientific_name",
            "genus",
            "family",
            "biodiv_index",
            "pct_species_street"
        ]]
        .rename(columns={
            "scientific_name": "Art",
            "genus": "Gattung",
            "family": "Familie",
            "biodiv_index": "Biodiversitätsindex",
            "pct_species_street": "Artanteil Strasse (%)"
        })
        .round(2)
    )

    return out

#visualisation
st.divider()
st.subheader("Empfohlene Baumarten – Stadtweit")
st.dataframe(Empfohlene_Baumarten_Stadtweit())

st.subheader("Empfohlene Baumarten – Park")
st.dataframe(Empfohlene_Baumarten_Park())

st.subheader("Empfohlene Baumarten – Strasse")
st.dataframe(Empfohlene_Baumarten_Strasse())

def Empfohlene_Baumarten_interaktiv(art_name):
    df = art_merged.copy()

    treffer = df[df["scientific_name"].str.lower() == art_name.lower()]

    if treffer.empty:
        treffer = df[
            df["scientific_name"].str.contains(art_name, case=False, na=False)
        ]

    if treffer.empty:
        return None

    row = treffer.iloc[0]

    hoher_index = pd.notna(row["biodiv_index"]) and row["biodiv_index"] >= 4

    empfohlen_gesamt = (
        hoher_index and
        row["pct_species_total"] < 5 and
        row["pct_genus_all"] <= 20 and
        row["pct_family_all"] <= 30
    )

    empfohlen_park = (
        hoher_index and
        row["pct_species_park"] < 5 and
        row["pct_genus_park"] <= 20 and
        row["pct_family_park"] <= 30
    )

    empfohlen_strasse = (
        hoher_index and
        row["pct_species_street"] < 5 and
        row["pct_genus_street"] <= 20 and
        row["pct_family_street"] <= 30
    )

    return {
        "Art": row["scientific_name"],
        "Biodiversitätsindex": row["biodiv_index"],
        "Empfehlung Stadtweit": empfohlen_gesamt,
        "Empfehlung Park": empfohlen_park,
        "Empfehlung Strasse": empfohlen_strasse
    }
st.divider()
st.subheader("Interaktive Empfehlung für eine Baumart")

art_input = st.text_input(
    "Wissenschaftlichen Artnamen eingeben (z. B. Acer campestre):",
    key="empfehlung"
)

if art_input:
    ergebnis = Empfohlene_Baumarten_interaktiv(art_input)

    if ergebnis is None:
        st.warning("Keine passende Art gefunden.")
    else:
        st.write("**Art:**", ergebnis["Art"])
        st.write("**Biodiversitätsindex:**", ergebnis["Biodiversitätsindex"])
        st.write("**Empfehlung Stadtweit:**", "empfohlen" if ergebnis["Empfehlung Stadtweit"] else "nicht priorisieren")
        st.write("**Empfehlung Park:**", "empfohlen" if ergebnis["Empfehlung Park"] else "nicht priorisieren")
        st.write("**Empfehlung Strasse:**", "empfohlen" if ergebnis["Empfehlung Strasse"] else "nicht priorisieren")

st.divider()
st.subheader("Biodiversitätsindex – Erklärung")

biodiv_info = pd.DataFrame({
    "Indexwert": [1, 2, 3, 4, 5, 6],
    "Bedeutung": [
        "nicht wertvoll",
        "geringe Bedeutung",
        "mittlere Bedeutung",
        "hohe Bedeutung",
        "sehr hohe Bedeutung",
        "sehr hohe Bedeutung (Parkbäume)"
    ]
})

st.table(biodiv_info)

st.divider()

st.markdown(
    """
    ---
    **Autor:** Adrian Hürlimann, Student BA Umweltingenieurwesen  
    **Smesterprojekt Angewandte Geoinformatik:** Analyse und Empfehlung von Stadtbaumarten (Stadt Zug)

    **Datenquellen & Referenzen:**
    - Baumkataster: WSL / kantonale Fachstellen  
    - Biodiversitätsindex Stadtbäume (2021)  
    - OpenStreetMap (Park- und Strassenflächen)  
    - Santamour, F. S. (1990): *Trees for Urban Planting: Diversity, Uniformity, and Common Sense*  
      (US National Arboretum) – Ursprung der 10/20/30-Regel

    **Hinweis:**  
    Die 10/20/30-Regel stellt eine empfohlene Richtgrösse zur Förderung der Baumartenvielfalt dar
    und ist nicht als starre Vorgabe zu verstehen.
    """
)



