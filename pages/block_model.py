"""
pages/block_model.py
====================
Conversão de rotação de modelo de blocos — individual com visualização 3D e em tabela.
"""

import streamlit as st
import numpy as np
import pandas as pd
import io
import plotly.graph_objects as go
from converters import leapfrog, isatis_neo, vulcan
from core.blockmodel import block_axes, unit_block_corners

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan"]

_BLOCK_COLS = {
    "Leapfrog":   ("Bearing (°)", "Plunge (°)", "Dip (°)"),
    "Isatis.neo": ("Azimute (°)", "Mergulho (°)", "Rake (°)"),
    "Vulcan":     ("Bearing (°)", "Plunge (°)", "Dip (°)"),
}


def _to_matrix(software: str, a: float, b: float, c: float) -> np.ndarray:
    if software == "Leapfrog":
        return leapfrog.block_to_matrix(a, b, c)
    elif software == "Isatis.neo":
        return isatis_neo.block_to_matrix(a, b, c)
    return vulcan.block_to_matrix(a, b, c)


def _from_matrix(software: str, R: np.ndarray) -> tuple[float, float, float]:
    if software == "Leapfrog":
        return leapfrog.matrix_to_block(R)
    elif software == "Isatis.neo":
        return isatis_neo.matrix_to_block(R)
    return vulcan.matrix_to_block(R)


def _block_figure(R_orig, R_conv, src_label, dst_label):
    """Bloco 3D com eixos locais U/V/W para os dois softwares."""
    fig = go.Figure()
    configs = [
        (R_orig, src_label, ["#1f77b4", "#2ca02c", "#ff7f0e"], 0.35, [0, 0, 0]),
        (R_conv, dst_label, ["#d62728", "#9467bd", "#8c564b"], 0.20, [0, 0, 0]),
    ]
    for R, label, colors, alpha, offset in configs:
        corners = unit_block_corners(R) + np.array(offset)
        # Faces (índices dos 8 cantos)
        face_i = [0,0,4,4,0,0,3,3,1,1,2,2]
        face_j = [1,3,5,7,4,1,7,4,5,2,6,3]
        face_k = [2,2,6,6,5,5,6,6,6,6,7,7]
        fig.add_trace(go.Mesh3d(
            x=corners[:,0], y=corners[:,1], z=corners[:,2],
            i=face_i, j=face_j, k=face_k,
            opacity=alpha, color="#aec7e8" if "orig" in label.lower() or R is R_orig else "#ffbb78",
            name=label, showlegend=True, hoverinfo="skip",
        ))
        u, v, w = block_axes(R)
        center = corners.mean(axis=0)
        scale = 0.65
        for vec, color, ax_name in zip([u, v, w], colors, ["U", "V", "W"]):
            end = center + vec * scale
            fig.add_trace(go.Cone(
                x=[end[0]], y=[end[1]], z=[end[2]],
                u=[vec[0]*0.3], v=[vec[1]*0.3], w=[vec[2]*0.3],
                colorscale=[[0, color], [1, color]],
                sizeref=0.25, showscale=False,
                name=f"{ax_name} ({label})", showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter3d(
                x=[center[0], end[0]], y=[center[1], end[1]], z=[center[2], end[2]],
                mode="lines", line=dict(color=color, width=4),
                name=f"{ax_name} ({label})", showlegend=False, hoverinfo="skip",
            ))

    fig.update_layout(
        scene=dict(xaxis_title="Leste (X)", yaxis_title="Norte (Y)", zaxis_title="Cima (Z)",
                   aspectmode="cube"),
        height=430, showlegend=True,
        legend=dict(orientation="h", x=0, y=-0.05, font=dict(size=11)),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    return fig


# ---------------------------------------------------------------------------
# Aba 1 — Individual
# ---------------------------------------------------------------------------

def _tab_individual(src: str, dst: str):
    lbs_src = _BLOCK_COLS[src]
    lbs_dst = _BLOCK_COLS[dst]
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("#### Ângulos de entrada")
        a = st.number_input(lbs_src[0], value=0.0, step=1.0, key="blk_a")
        b = st.number_input(lbs_src[1], value=0.0, min_value=0.0, max_value=90.0, step=1.0, key="blk_b")
        c = st.number_input(lbs_src[2], value=0.0, step=1.0, key="blk_c")
        if st.button("🔄 Converter", key="blk_btn", use_container_width=True, type="primary"):
            R = _to_matrix(src, a, b, c)
            v1, v2, v3 = _from_matrix(dst, R)
            st.session_state["blk_single"] = dict(R=R, v1=v1, v2=v2, v3=v3,
                                                    src=src, dst=dst)

    if "blk_single" in st.session_state:
        r = st.session_state["blk_single"]
        with col_out:
            st.markdown("#### Resultado")
            m1, m2, m3 = st.columns(3)
            m1.metric(lbs_dst[0], f"{r['v1']:.3f}°")
            m2.metric(lbs_dst[1], f"{r['v2']:.3f}°")
            m3.metric(lbs_dst[2], f"{r['v3']:.3f}°")
            R_dst = _to_matrix(r["dst"], r["v1"], r["v2"], r["v3"])
            st.plotly_chart(_block_figure(r["R"], R_dst, r["src"], r["dst"]),
                            use_container_width=True)
        if r["dst"] == "Isatis.neo":
            st.warning("⚠️ Isatis.neo: sinal do ângulo de mergulho a confirmar com documentação oficial.")


# ---------------------------------------------------------------------------
# Aba 2 — Tabela
# ---------------------------------------------------------------------------

def _tab_tabela(src: str, dst: str):
    lbs_src = _BLOCK_COLS[src]
    lbs_dst = _BLOCK_COLS[dst]
    c1, c2, c3 = lbs_src
    lc1, lc2, lc3 = lbs_dst

    fonte = st.radio("Fonte dos dados", ["✏️ Digitar manualmente", "📂 Carregar CSV"],
                     horizontal=True, key="blk_fonte")

    if fonte == "✏️ Digitar manualmente":
        default = pd.DataFrame({c1: [0.0, 45.0, 90.0], c2: [0.0, 30.0, 45.0], c3: [0.0, 15.0, 30.0]})
        df_in = st.data_editor(default, num_rows="dynamic", use_container_width=True, key="blk_editor")
    else:
        uploaded = st.file_uploader(f"CSV com colunas {c1}, {c2}, {c3}", type=["csv"], key="blk_csv")
        if uploaded is None:
            st.info(f"Carregue um CSV com as colunas `{c1}`, `{c2}`, `{c3}`.")
            return
        df_in = pd.read_csv(uploaded)

    if st.button("🔄 Converter Tabela", key="blk_btn_table", use_container_width=True, type="primary"):
        rows = []
        for _, row in df_in.iterrows():
            try:
                R = _to_matrix(src, float(row[c1]), float(row[c2]), float(row[c3]))
                v1, v2, v3 = _from_matrix(dst, R)
                rows.append({c1: row[c1], c2: row[c2], c3: row[c3],
                              lc1: round(v1, 4), lc2: round(v2, 4), lc3: round(v3, 4)})
            except Exception:
                rows.append({c1: row.get(c1), c2: row.get(c2), c3: row.get(c3),
                              lc1: None, lc2: None, lc3: None})
        st.session_state["blk_table_result"] = pd.DataFrame(rows)

    if "blk_table_result" in st.session_state:
        df_out = st.session_state["blk_table_result"]
        st.markdown("#### Resultado")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Entrada — {src}**")
            st.dataframe(df_out[[c1, c2, c3]].style.format("{:.3f}"), use_container_width=True, hide_index=True)
        with col_b:
            st.markdown(f"**Saída — {dst}**")
            st.dataframe(df_out[[lc1, lc2, lc3]].style.format("{:.3f}"), use_container_width=True, hide_index=True)
        st.divider()
        buf = io.StringIO()
        df_out.to_csv(buf, index=False)
        st.download_button("⬇️ Baixar tabela convertida (CSV)", buf.getvalue(),
                           file_name="blocos_convertidos.csv", mime="text/csv",
                           use_container_width=True)


# ---------------------------------------------------------------------------
# Render principal
# ---------------------------------------------------------------------------

def render():
    st.title("📦 Modelo de Blocos")

    hdr_l, hdr_m, hdr_r = st.columns([2, 1, 2])
    with hdr_l:
        src = st.selectbox("Software de **origem**", SOFTWARES, key="blk_src_top")
    with hdr_m:
        st.markdown("<div style='text-align:center;padding-top:28px;font-size:22px'>→</div>",
                    unsafe_allow_html=True)
    with hdr_r:
        dst = st.selectbox("Software de **destino**", SOFTWARES, key="blk_dst_top")

    st.divider()

    tab1, tab2 = st.tabs(["🔢 Conversão Individual", "📋 Conversão em Tabela"])
    with tab1:
        _tab_individual(src, dst)
    with tab2:
        _tab_tabela(src, dst)

    from help_system import render_help_button
    render_help_button("blocos", "📖 Como funciona a rotação de modelo de blocos?")
