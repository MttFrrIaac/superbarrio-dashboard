import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# --- Load Data ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSffz39J7Ct_FPvZ34lEL5neXaAWTWeL4g_egbE-gYlM529sGf-oIKN-N2D3sUkxHcsk1kqxj1da89o/pub?gid=1278185519&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(sheet_url)
    df = df.rename(columns=lambda x: x.strip())
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df.dropna(subset=['N', 'E'])

df = load_data()

# --- Define category colors ---
category_colors = {
    "Accessibility": "#FF6347",
    "Traffic-Management-Solutions": "#3CB371",
    "PMV-Infrastructure": "#1E90FF",
    "Tactical-Urbanism": "#9370DB"
}

# --- Layout Tweaks ---
st.set_page_config(layout="wide")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Filter for Map of Solutions
st.sidebar.subheader("Map Filters")
df_map = df.copy()
date_range_map = st.sidebar.date_input("Date Range (Map)", [df_map['Date'].min(), df_map['Date'].max()])
df_map = df_map[(df_map['Date'] >= pd.to_datetime(date_range_map[0])) & (df_map['Date'] <= pd.to_datetime(date_range_map[1]))]

with st.sidebar.expander("Category Filters (Map)", expanded=True):
    for col in ['Workshop', 'Version', 'Category', 'Solution']:
        if col in df_map.columns:
            options = df_map[col].dropna().unique()
            selected = st.multiselect(f"Select {col}", options, default=list(options))
            df_map = df_map[df_map[col].isin(selected)]

# --- Title ---
st.title("🎯 SuperBarrio Interactive Dashboard")

# --- Layout Columns for Map + Dashboard ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Map of Solutions")
    if not df_map.empty:
        m = folium.Map(location=[41.6488, -0.8891], zoom_start=13)
        for _, row in df_map.iterrows():
            category = row.get('Category', '')
            color = category_colors.get(category, 'gray')
            popup = f"{row.get('Workshop', '')} - {category}: {row.get('Solution', '')}"
            folium.Marker(
                location=(row['N'], row['E']),
                popup=popup,
                icon=folium.Icon(color="blue", icon_color=color)
            ).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning("No data available for selected filters on the map.")

with col2:
    st.subheader("Dashboard Summary")
    if not df_map.empty:
        st.markdown("**Number of Entries per Category**")
        cat_counts = df_map['Category'].value_counts()
        st.bar_chart(cat_counts)

        st.markdown("**Number of Solutions per Workshop**")
        ws_counts = df_map['Workshop'].value_counts()
        st.bar_chart(ws_counts)
    else:
        st.info("Nothing to display in dashboard.")

# --- Heatmap Section ---
st.markdown("### Heatmap of Solutions")
heat_col1, heat_col2 = st.columns([4, 1])

with heat_col2:
    df_heat = df.copy()
    cat_options = df_heat['Category'].dropna().unique()
    selected_cats = st.multiselect("Filter by Category (Heatmap)", cat_options, default=list(cat_options))
    df_heat = df_heat[df_heat['Category'].isin(selected_cats)]

with heat_col1:
    if not df_heat.empty:
        hm = folium.Map(location=[41.6488, -0.8891], zoom_start=13)
        heat_data = df_heat[['N', 'E']].dropna().values.tolist()
        HeatMap(heat_data).add_to(hm)
        st_folium(hm, width=900, height=500)
    else:
        st.warning("No data available for selected filters on the heatmap.")

# --- Download ---
st.markdown("### ⬇️ Download Filtered Data")
csv = df_map.to_csv(index=False)
st.download_button("Download CSV", csv, file_name="filtered_data.csv", mime="text/csv")
