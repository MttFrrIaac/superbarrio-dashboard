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

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Date Filter
date_range = st.sidebar.date_input("Date Range", [df['Date'].min(), df['Date'].max()])
df = df[(df['Date'] >= pd.to_datetime(date_range[0])) & (df['Date'] <= pd.to_datetime(date_range[1]))]

# Categorical Filters
for col in ['Workshop', 'Version', 'Category', 'Solution']:
    if col in df.columns:
        options = df[col].dropna().unique()
        selected = st.sidebar.multiselect(f"Select {col}", options, default=options)
        df = df[df[col].isin(selected)]

# --- Main Title ---
st.title("🎯 SuperBarrio Interactive Dashboard")

# --- Map with Markers and Heatmap ---
st.subheader("🗺️ Map of Solutions")

zaragoza_coords = [41.6488, -0.8891]  # Center on Zaragoza
m = folium.Map(location=zaragoza_coords, zoom_start=13)

if not df.empty:
    # Marker colors per category
    category_colors = {
        'Environment': 'green',
        'Mobility': 'blue',
        'Health': 'red',
        'Education': 'purple',
        'Other': 'gray'
    }

    for _, row in df.iterrows():
        popup = f"{row.get('Workshop', '')} - {row.get('Category', '')}: {row.get('Solution', '')}"
        color = category_colors.get(row.get('Category', ''), 'gray')
        folium.Marker(
            location=(row['N'], row['E']),
            popup=popup,
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Heatmap layer
    heat_data = [[row['N'], row['E']] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=10).add_to(m)

st_folium(m, width=700, height=500)

# --- Dashboard View ---
st.subheader("📊 Dashboard Summary")

if not df.empty:
    st.markdown("**Number of Entries per Category**")
    st.bar_chart(df['Category'].value_counts())

    st.markdown("**Number of Solutions per Workshop**")
    st.bar_chart(df['Workshop'].value_counts())
else:
    st.info("Nothing to display in dashboard.")

# --- Download Data ---
st.subheader("⬇️ Download Filtered Data")
csv = df.to_csv(index=False)
st.download_button("Download CSV", csv, file_name="filtered_data.csv", mime="text/csv")
