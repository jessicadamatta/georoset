"""
pages/coordinates.py
====================
Página Streamlit para reformatação e conversão de coordenadas de pontos e sondagens.
"""

import streamlit as st
import pandas as pd
import io
from core.coordinates import flip_z_sign, standardize_columns

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan (pontos)", "Vulcan (sondagens — Z profundidade)"]


def render():
    st.title("📍 Coordenadas de Pontos e Sondagens")
    st.caption("Reformatação de colunas e conversão de convenção de Z entre softwares.")

    src = st.selectbox("Software de origem (convenção de Z)", SOFTWARES, key="coord_src")

    uploaded = st.file_uploader("Carregar CSV", type=["csv"], key="coord_upload")

    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return

        st.subheader("Prévia dos dados originais")
        st.dataframe(df.head(20), use_container_width=True)

        # Detectar ou selecionar colunas
        cols = list(df.columns)
        col1, col2, col3 = st.columns(3)
        with col1:
            x_col = st.selectbox("Coluna X (Leste)", cols, key="coord_xcol")
        with col2:
            y_col = st.selectbox("Coluna Y (Norte)", cols, key="coord_ycol")
        with col3:
            z_col = st.selectbox("Coluna Z", cols, key="coord_zcol")

        if st.button("🔄 Reformatar", key="coord_convert"):
            df_out = standardize_columns(df, x_col=x_col, y_col=y_col, z_col=z_col)

            # Se for Vulcan com sondagens (Z profundidade), inverter sinal
            if "sondagens" in src.lower():
                df_out = flip_z_sign(df_out, z_col="Z")
                st.info(
                    "Z invertido: Vulcan armazena profundidade como Z positivo para baixo. "
                    "Convertido para cota geográfica (Z positivo para cima)."
                )

            st.subheader("Resultado reformatado")
            st.dataframe(df_out.head(20), use_container_width=True)

            # Download
            csv_buffer = io.StringIO()
            df_out.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Baixar CSV reformatado",
                data=csv_buffer.getvalue(),
                file_name="coordenadas_georoset.csv",
                mime="text/csv",
                key="coord_download",
            )

    else:
        st.info("Carregue um arquivo CSV com colunas de coordenadas X, Y, Z.")

    st.info(
        "Reprojeção de datum (SAD69/SIRGAS 2000/UTM) e conversão de fuso em desenvolvimento. "
        "Para reprojeção, utilize `pyproj` diretamente."
    )

    from help_system import render_help_button
    render_help_button("coordenadas", "📖 Convenções de coordenadas por software")
