import streamlit as st

st.set_page_config(
    page_title="GeoRoset",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🪨 GeoRoset")
st.sidebar.caption("Conversor de convenções geológicas")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navegação",
    ["🏠 Início", "🪨 Discos Estruturais", "📡 Variograma", "📦 Modelo de Blocos", "📍 Coordenadas"],
)

st.sidebar.divider()
st.sidebar.markdown("[![GitHub](https://img.shields.io/badge/GitHub-open--source-black)](https://github.com/jessicadamatta/georoset)")
st.sidebar.caption("MIT License · Contribuições bem-vindas")

if page == "🏠 Início":
    from help_system import render_about_panel
    render_about_panel()
elif page == "🪨 Discos Estruturais":
    from pages.structural_discs import render
    render()
elif page == "📡 Variograma":
    from pages.variogram_params import render
    render()
elif page == "📦 Modelo de Blocos":
    from pages.block_model import render
    render()
elif page == "📍 Coordenadas":
    from pages.coordinates import render
    render()
