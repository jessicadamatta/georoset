import streamlit as st

st.set_page_config(
    page_title="GeoRoset",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/GeoRoset-v0.1-D4A843?style=for-the-badge")
    st.caption("Conversor de convenções geológicas")
    st.divider()

    page = st.radio(
        "**Navegação**",
        options=[
            "🏠 Início",
            "🪨 Discos Estruturais",
            "📡 Variograma",
            "📦 Modelo de Blocos",
            "📍 Coordenadas",
        ],
        label_visibility="visible",
    )

    st.divider()
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-jessicadamatta-black?logo=github)]"
        "(https://github.com/jessicadamatta/georoset)"
    )
    st.caption("MIT License · Contribuições bem-vindas")

# ── Roteamento ─────────────────────────────────────────────────────────────
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
