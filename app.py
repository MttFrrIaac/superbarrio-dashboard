import streamlit as st
import pandas as pd

st.title("🧪 Streamlit App Test")

st.write("✅ App is running")

sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSffz39J7Ct_FPvZ34lEL5neXaAWTWeL4g_egbE-gYlM529sGf-oIKN-N2D3sUkxHcsk1kqxj1da89o/pub?gid=1278185519&single=true&output=csv"

@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

try:
    df = load_data()
    st.write("### Preview of Data")
    st.dataframe(df)
except Exception as e:
    st.error(f"Failed to load data: {e}")
