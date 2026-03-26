"""
pages/coordinates.py
====================
Reformatação e conversão de coordenadas de pontos e sondagens.
"""

import streamlit as st
import pandas as pd
import io
from core.coordinates import flip_z_sign, standardize_columns

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan — pontos", "Vulcan — sondagens (Z profundidade → cota)"]


def _sample_csv(software: str) -> str:
    """Gera um CSV de exemplo para o software selecionado."""
    if "sondagens" in software.lower():
        df = pd.DataFrame({"X": [350000.0, 350010.0], "Y": [7500000.0, 7500020.0],
                           "Z_profundidade": [0.0, 50.0], "amostra": ["A1", "A2"]})
    else:
        df = pd.DataFrame({"X": [350000.0, 350010.0], "Y": [7500000.0, 7500020.0],
                           "Z": [800.0, 780.0], "amostra": ["A1", "A2"]})
    return df.to_csv(index=False)


def render():
    st.title("📍 Coordenadas de Pontos e Sondagens")
    st.caption("Reformatação de colunas e conversão da convenção de Z entre softwares.")

    # ── Seletores no topo ──────────────────────────────────────────────────
    hdr_l, hdr_r = st.columns([2, 2])
    with hdr_l:
        src = st.selectbox("Software / convenção de **origem**", SOFTWARES, key="coord_src")
    with hdr_r:
        st.download_button(
            "📄 Baixar CSV de exemplo",
            data=_sample_csv(src),
            file_name="exemplo_coordenadas.csv",
            mime="text/csv",
        )

    st.divider()

    tab1, tab2 = st.tabs(["📂 Carregar CSV", "✏️ Digitar manualmente"])

    # ── Tab 1 — Upload de CSV ───────────────────────────────────────────────
    with tab1:
        uploaded = st.file_uploader("Selecione o arquivo CSV", type=["csv"], key="coord_upload")

        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded)
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {e}")
                return

            st.markdown("#### Prévia — dados originais")
            st.dataframe(df_raw.head(10), use_container_width=True, hide_index=True)

            st.markdown("#### Mapeamento de colunas")
            cols = list(df_raw.columns)
            c1, c2, c3 = st.columns(3)
            x_col = c1.selectbox("Coluna X (Leste)", cols, key="coord_x")
            y_col = c2.selectbox("Coluna Y (Norte)", cols,
                                 index=min(1, len(cols)-1), key="coord_y")
            z_col = c3.selectbox("Coluna Z", cols,
                                 index=min(2, len(cols)-1), key="coord_z")

            if st.button("🔄 Reformatar", key="coord_btn_csv", use_container_width=True, type="primary"):
                df_out = standardize_columns(df_raw, x_col=x_col, y_col=y_col, z_col=z_col)
                if "sondagens" in src.lower():
                    df_out = flip_z_sign(df_out, z_col="Z")
                st.session_state["coord_result_csv"] = df_out

        if "coord_result_csv" in st.session_state:
            df_out = st.session_state["coord_result_csv"]
            _show_result(df_out, src, "coordenadas_convertidas.csv")

    # ── Tab 2 — Entrada manual ─────────────────────────────────────────────
    with tab2:
        z_label = "Z_profundidade" if "sondagens" in src.lower() else "Z"
        default = pd.DataFrame({
            "X":     [350000.0, 350010.0, 350020.0],
            "Y":     [7500000.0, 7500015.0, 7500030.0],
            z_label: [800.0, 50.0, 120.0] if "sondagens" not in src.lower() else [0.0, 25.0, 50.0],
        })
        st.caption(f"Edite os valores diretamente na tabela. Coluna Z: **{z_label}**")
        df_manual = st.data_editor(
            default, num_rows="dynamic", use_container_width=True, key="coord_editor",
            column_config={
                "X": st.column_config.NumberColumn(format="%.2f"),
                "Y": st.column_config.NumberColumn(format="%.2f"),
                z_label: st.column_config.NumberColumn(format="%.2f"),
            },
        )

        if st.button("🔄 Converter", key="coord_btn_manual", use_container_width=True, type="primary"):
            df_out = df_manual.rename(columns={z_label: "Z"}).copy()
            if "sondagens" in src.lower():
                df_out = flip_z_sign(df_out, z_col="Z")
            st.session_state["coord_result_manual"] = df_out

        if "coord_result_manual" in st.session_state:
            df_out = st.session_state["coord_result_manual"]
            _show_result(df_out, src, "coordenadas_manuais.csv")

    # ── Nota sobre reprojeção ──────────────────────────────────────────────
    with st.expander("🌐 Reprojeção geodésica (em desenvolvimento)"):
        st.info(
            "Conversão entre fusos UTM, SAD69 → SIRGAS 2000 e coordenadas locais de mina → UTM "
            "estará disponível em breve via `pyproj`. Por ora, utilize o QGIS ou o `pyproj` diretamente."
        )

    from help_system import render_help_button
    render_help_button("coordenadas", "📖 Convenções de coordenadas por software")


def _show_result(df_out: pd.DataFrame, src: str, filename: str):
    """Exibe o resultado da conversão e o botão de download."""
    st.divider()
    st.markdown("#### Resultado")

    if "sondagens" in src.lower():
        st.success("Z invertido: profundidade (positivo ↓) → cota geográfica (positivo ↑)")

    # Tabelas lado a lado: antes × depois
    z_label_orig = "Z_profundidade" if "sondagens" in src.lower() else "Z"
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Entrada — {src.split('—')[0].strip()}**")
        df_show_in = df_out.copy()
        if "sondagens" in src.lower():
            df_show_in["Z"] = -df_show_in["Z"]  # mostra original
            df_show_in = df_show_in.rename(columns={"Z": z_label_orig})
        st.dataframe(df_show_in.style.format("{:.3f}", subset=["X", "Y",
                     z_label_orig if "sondagens" in src.lower() else "Z"]),
                     use_container_width=True, hide_index=True)
    with col_b:
        st.markdown("**Saída — X, Y, Z (cota geográfica)**")
        numeric_cols = [c for c in ["X", "Y", "Z"] if c in df_out.columns]
        st.dataframe(df_out.style.format("{:.3f}", subset=numeric_cols),
                     use_container_width=True, hide_index=True)

    st.divider()
    buf = io.StringIO()
    df_out.to_csv(buf, index=False)
    st.download_button(
        "⬇️ Baixar CSV convertido",
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )
