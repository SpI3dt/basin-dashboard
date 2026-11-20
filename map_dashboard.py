"""
Basin morphometrics map dashboard (Streamlit).

Displays the maps from your morphometrics script: HI, RR, DD, RI, BC
(and BSI if that column exists). It reads the GeoJSON your script saves,
so run the analysis script first.

Run:

 TO RUN THIS FILE
       "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m streamlit run map_dashboard.py in terminal, do not run plainly as streamlit does not recognize the path of the file.
  python -m streamlit run map_dashboard.py
Install once:
  pip install streamlit geopandas matplotlib pandas numpy
"""

import os
import math
import geopandas as gpd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Basin Morphometrics", layout="wide")

# Files the analysis scripts save (first one that exists is used as default)
CANDIDATES = [
    r"C:\Users\siddh\Documents\College\SEMESTER III\GEOproject\morphometrics.rar\morphometrics\basins_morphometrics.geojson",
    r"C:\Users\siddh\Documents\College\SEMESTER III\GEOproject\HI_CALC\basins_morphometrics.geojson",
    r"C:\Users\siddh\Documents\College\SEMESTER III\GEOproject\HI_CALC\basins_parameters.geojson",
    "basins_morphometrics.geojson",
]

# column: (title, what a high value means)
PARAMS = {
    "HI":  ("Hypsometric integral", "most of the basin is high up: young, uplifted landscape"),
    "RR":  ("Relief ratio", "steeper basin over its length"),
    "DD":  ("Drainage density (km/km²)", "more stream length per area: more dissected terrain"),
    "RI":  ("Ruggedness index", "rougher, more dissected relief"),
    "BC":  ("Basin compactness (4πA/P²)", "closer to circular (low = elongated)"),
    "BSI": ("Basin shape index (L/W)", "longer and thinner basin"),
}


@st.cache_data
def load(path):
    return gpd.read_file(path)


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
st.sidebar.title("Controls")
default = next((c for c in CANDIDATES if os.path.exists(c)), CANDIDATES[0])
path = st.sidebar.text_input("Path to the basins GeoJSON", default)

if not os.path.exists(path):
    st.error(f"File not found:\n{path}\n\nRun your analysis script first, then "
             "paste the full path to its .geojson output in the sidebar.")
    st.stop()

basins = load(path)
available = [c for c in PARAMS if c in basins.columns]
if not available:
    st.error("No known parameter columns (HI, RR, DD, RI, BC) found in this file.")
    st.stop()

cmap = st.sidebar.selectbox(
    "Color scale", ["viridis", "plasma", "magma", "cividis", "YlOrRd", "RdYlBu_r", "terrain"])
show_ids = st.sidebar.checkbox("Show basin IDs on maps", value=True)

has_id = "basin_id" in basins.columns
if not has_id:
    basins["basin_id"] = range(1, len(basins) + 1)


def draw(ax, col, highlight=None, big=False):
    basins.plot(column=col, cmap=cmap, legend=True, edgecolor="black",
                linewidth=0.4, ax=ax, missing_kwds={"color": "lightgrey"},
                legend_kwds={"shrink": 0.7})
    if highlight is not None:
        basins[basins["basin_id"] == highlight].boundary.plot(
            ax=ax, color="red", linewidth=2.5)
    if show_ids:
        for _, row in basins.iterrows():
            x, y = row.geometry.representative_point().coords[0]
            ax.text(x, y, str(row["basin_id"]), fontsize=8 if big else 6,
                    ha="center", va="center", color="white",
                    bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.35, lw=0))
    ax.set_title(PARAMS[col][0], fontsize=12 if big else 10)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")


# ------------------------------------------------------------------
# Main page
# ------------------------------------------------------------------
st.title("Basin Morphometrics Maps")
st.caption(f"{len(basins)} basins loaded from {os.path.basename(path)}")

tab_all, tab_one, tab_table = st.tabs(["All maps", "Single map + inspector", "Table"])

# ---- All maps in a grid
with tab_all:
    n = len(available)
    ncols = 3 if n > 2 else n
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 6 * nrows))
    axes = [axes] if n == 1 else list(axes.flatten())
    for ax, col in zip(axes, available):
        draw(ax, col)
    for ax in axes[n:]:
        ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

# ---- One big map, summary stats, basin inspector
with tab_one:
    col = st.selectbox("Parameter", available,
                       format_func=lambda c: f"{c} - {PARAMS[c][0]}")
    st.caption(f"High value = {PARAMS[col][1]}.")

    ids = basins["basin_id"].tolist()
    sel = st.selectbox("Highlight a basin (red outline)", ["None"] + ids)
    highlight = None if sel == "None" else sel

    left, right = st.columns([3, 2])
    with left:
        fig, ax = plt.subplots(figsize=(8, 8))
        draw(ax, col, highlight, big=True)
        st.pyplot(fig)

    with right:
        s = basins[col].dropna()
        m1, m2, m3 = st.columns(3)
        m1.metric("Min", f"{s.min():.3f}")
        m2.metric("Mean", f"{s.mean():.3f}")
        m3.metric("Max", f"{s.max():.3f}")

        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.hist(s, bins=15, color="steelblue", edgecolor="black")
        ax2.set_xlabel(col)
        ax2.set_ylabel("Number of basins")
        if highlight is not None:
            v = basins.loc[basins["basin_id"] == highlight, col].iloc[0]
            if v == v:   # not NaN
                ax2.axvline(v, color="red", linewidth=2)
        st.pyplot(fig2)

        if highlight is not None:
            st.write(f"**Basin {highlight}**")
            row = basins[basins["basin_id"] == highlight].iloc[0]
            show = {c: round(float(row[c]), 4) for c in available if row[c] == row[c]}
            for extra in ("area_km2", "E_min", "E_max", "E_mean"):
                if extra in basins.columns and row[extra] == row[extra]:
                    show[extra] = round(float(row[extra]), 2)
            st.table(show)

# ---- Table
with tab_table:
    keep = ["basin_id"] + [c for c in ("area_km2", "E_min", "E_max", "E_mean")
                           if c in basins.columns] + available
    table = basins[keep].drop(columns="geometry", errors="ignore").round(4)
    st.dataframe(table, width="stretch")
    st.download_button("Download CSV", table.to_csv(index=False), "basin_morphometrics.csv")
