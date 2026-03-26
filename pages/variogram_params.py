"""
pages/variogram_params.py
=========================
Conversão de parâmetros de variograma — individual com elipsoide 3D e em tabela.
"""

import streamlit as st
import numpy as np
import pandas as pd
import io
import plotly.graph_objects as go
from converters import leapfrog, isatis_neo, vulcan
from core.variogram import ellipsoid_surface

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan"]

_VARIO_COLS = {
    "Leapfrog":   ("Bearing (°)", "Plunge (°)", "Rake (°)"),
    "Isatis.neo": ("Azimute (°)", "Mergulho (°)", "Rake (°)"),
    "Vulcan":     ("Bearing (°)", "Plunge (°)", "Dip (°)"),
}


def _to_matrix(software: str, a: float, b: float, c: float) -> np.ndarray:
    if software == "Leapfrog":
        return leapfrog.vario_to_matrix(a, b, c)
    elif software == "Isatis.neo":
        return isatis_neo.vario_to_matrix(a, b, c)
    return vulcan.vario_to_matrix(a, b, c)


def _from_matrix(software: str, R: np.ndarray) -> tuple[float, float, float]:
    if software == "Leapfrog":
        return leapfrog.matrix_to_vario(R)
    elif software == "Isatis.neo":
        return isatis_neo.matrix_to_vario(R)
    return vulcan.matrix_to_vario(R)


def _ellipsoid_trace(R, a1, a2, a3, color, name, opacity=0.4):
    X, Y, Z = ellipsoid_surface(R, a1, a2, a3, n=25)
    return go.Surface(x=X, y=Y, z=Z,
                      colorscale=[[0, color], [1, color]],
                      opacity=opacity, showscale=False, name=name, hoverinfo="skip")


def _axis_traces(scale):
    traces = []
    for label, vec, color in [("E", [1,0,0], "#d62728"), ("N", [0,1,0], "#2ca02c"), ("Z", [0,0,1], "#1f77b4")]:
        traces.append(go.Scatter3d(
            x=[0, vec[0]*scale], y=[0, vec[1]*scale], z=[0, vec[2]*scale],
            mode="lines+text", line=dict(color=color, width=3),
            text=["", f"<b>{label}</b>"], textposition="top center",
            showlegend=False, hoverinfo="skip",
        ))
    return traces


# ---------------------------------------------------------------------------
# Aba 1 — Individual
# ---------------------------------------------------------------------------

def _tab_individual(src: str, dst: str):
    lbs_src = _VARIO_COLS[src]
    lbs_dst = _VARIO_COLS[dst]
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("#### Ângulos de entrada")
        a = st.number_input(lbs_src[0], value=0.0, step=1.0, key="vario_a")
        b = st.number_input(lbs_src[1], min_value=0.0, max_value=90.0, value=0.0, step=1.0, key="vario_b")
        c = st.number_input(lbs_src[2], value=0.0, step=1.0, key="vario_c")
        st.markdown("#### Alcances (semieixos)")
        a1 = st.number_input("a₁ — maior alcance", min_value=0.1, value=100.0, step=5.0, key="vario_a1")
        a2 = st.number_input("a₂ — intermediário", min_value=0.1, value=60.0, step=5.0, key="vario_a2")
        a3 = st.number_input("a₃ — menor alcance", min_value=0.1, value=20.0, step=5.0, key="vario_a3")
        if st.button("🔄 Converter", key="vario_btn", use_container_width=True, type="primary"):
            R = _to_matrix(src, a, b, c)
            v1, v2, v3 = _from_matrix(dst, R)
            st.session_state["vario_single"] = dict(R=R, v1=v1, v2=v2, v3=v3,
                                                     a1=a1, a2=a2, a3=a3, src=src, dst=dst)

    if "vario_single" in st.session_state:
        r = st.session_state["vario_single"]
        with col_out:
            st.markdown("#### Resultado")
            m1, m2, m3 = st.columns(3)
            m1.metric(lbs_dst[0], f"{r['v1']:.3f}°")
            m2.metric(lbs_dst[1], f"{r['v2']:.3f}°")
            m3.metric(lbs_dst[2], f"{r['v3']:.3f}°")

            R_dst = _to_matrix(r["dst"], r["v1"], r["v2"], r["v3"])
            mx = max(r["a1"], r["a2"], r["a3"]) * 1.3
            fig = go.Figure(data=[
                _ellipsoid_trace(r["R"],  r["a1"], r["a2"], r["a3"], "#1f77b4", f"Original ({r['src']})", 0.45),
                _ellipsoid_trace(R_dst, r["a1"], r["a2"], r["a3"], "#d62728", f"Convertido ({r['dst']})", 0.30),
            ] + _axis_traces(mx))
            fig.update_layout(
                scene=dict(xaxis_title="Leste (X)", yaxis_title="Norte (Y)", zaxis_title="Cima (Z)"),
                height=430, showlegend=True,
                legend=dict(orientation="h", x=0, y=-0.05, font=dict(size=11)),
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        if r["dst"] == "Isatis.neo":
            st.warning("⚠️ Isatis.neo: sinal do ângulo de mergulho a confirmar com documentação oficial.")


# ---------------------------------------------------------------------------
# Aba 2 — Tabela
# ---------------------------------------------------------------------------

def _tab_tabela(src: str, dst: str):
    lbs_src = _VARIO_COLS[src]
    lbs_dst = _VARIO_COLS[dst]
    c1, c2, c3 = lbs_src
    lc1, lc2, lc3 = lbs_dst

    fonte = st.radio("Fonte dos dados", ["✏️ Digitar manualmente", "📂 Carregar CSV"],
                     horizontal=True, key="vario_fonte")

    if fonte == "✏️ Digitar manualmente":
        default = pd.DataFrame({c1: [0.0, 30.0, 45.0], c2: [0.0, 20.0, 45.0], c3: [0.0, 10.0, 30.0]})
        df_in = st.data_editor(default, num_rows="dynamic", use_container_width=True,
                               key="vario_editor")
    else:
        uploaded = st.file_uploader(f"CSV com colunas {c1}, {c2}, {c3}", type=["csv"], key="vario_csv")
        if uploaded is None:
            st.info(f"Carregue um CSV com as colunas `{c1}`, `{c2}`, `{c3}`.")
            return
        df_in = pd.read_csv(uploaded)

    if st.button("🔄 Converter Tabela", key="vario_btn_table", use_container_width=True, type="primary"):
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
        st.session_state["vario_table_result"] = pd.DataFrame(rows)

    if "vario_table_result" in st.session_state:
        df_out = st.session_state["vario_table_result"]
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
                           file_name="variograma_convertido.csv", mime="text/csv",
                           use_container_width=True)


# ---------------------------------------------------------------------------
# Render principal
# ---------------------------------------------------------------------------

def render():
    st.title("📡 Parâmetros de Variograma")

    hdr_l, hdr_m, hdr_r = st.columns([2, 1, 2])
    with hdr_l:
        src = st.selectbox("Software de **origem**", SOFTWARES, key="vario_src_top")
    with hdr_m:
        st.markdown("<div style='text-align:center;padding-top:28px;font-size:22px'>→</div>",
                    unsafe_allow_html=True)
    with hdr_r:
        dst = st.selectbox("Software de **destino**", SOFTWARES, key="vario_dst_top")

    st.divider()

    tab1, tab2 = st.tabs(["🔢 Conversão Individual", "📋 Conversão em Tabela"])
    with tab1:
        _tab_individual(src, dst)
    with tab2:
        _tab_tabela(src, dst)

    from help_system import render_help_button
    render_help_button("variograma", "📖 Como funciona a conversão de variogramas?")
