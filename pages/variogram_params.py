"""
pages/variogram_params.py
=========================
Página Streamlit para conversão de parâmetros de variograma (anisotropia).
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from converters import leapfrog, isatis_neo, vulcan
from core.variogram import ellipsoid_surface

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan"]


def _vario_to_matrix(software: str, a1: float, a2: float, a3: float):
    """Lê os ângulos da session_state e constrói a matriz de rotação."""
    if software == "Leapfrog":
        bearing = st.session_state.get("vario_src_bearing", 0.0)
        plunge = st.session_state.get("vario_src_plunge", 0.0)
        rake = st.session_state.get("vario_src_rake", 0.0)
        return leapfrog.vario_to_matrix(bearing, plunge, rake)
    elif software == "Isatis.neo":
        az = st.session_state.get("vario_src_az", 0.0)
        dip = st.session_state.get("vario_src_dip", 0.0)
        rake = st.session_state.get("vario_src_rake", 0.0)
        return isatis_neo.vario_to_matrix(az, dip, rake)
    else:
        bearing = st.session_state.get("vario_src_bearing", 0.0)
        plunge = st.session_state.get("vario_src_plunge", 0.0)
        dip = st.session_state.get("vario_src_dip", 0.0)
        return vulcan.vario_to_matrix(bearing, plunge, dip)


def _input_fields_vario(software: str):
    """Campos de entrada conforme o software."""
    if software == "Leapfrog":
        st.number_input("Bearing (°)", 0.0, 360.0, step=1.0, key="vario_src_bearing")
        st.number_input("Plunge (°)", 0.0, 90.0, step=1.0, key="vario_src_plunge")
        st.number_input("Rake (°)", 0.0, 360.0, step=1.0, key="vario_src_rake")
    elif software == "Isatis.neo":
        st.number_input("Azimute (°)", 0.0, 360.0, step=1.0, key="vario_src_az")
        st.number_input("Mergulho (°)", 0.0, 90.0, step=1.0, key="vario_src_dip")
        st.number_input("Rake (°)", 0.0, 360.0, step=1.0, key="vario_src_rake")
    else:
        st.number_input("Bearing (°)", 0.0, 360.0, step=1.0, key="vario_src_bearing")
        st.number_input("Plunge (°)", 0.0, 90.0, step=1.0, key="vario_src_plunge")
        st.number_input("Dip (°)", 0.0, 360.0, step=1.0, key="vario_src_dip")


def _decompose_to_dst(R: np.ndarray, dst: str) -> tuple:
    """Decompõe a matriz R nos ângulos do software de destino."""
    if dst == "Leapfrog":
        return leapfrog.matrix_to_vario(R)
    elif dst == "Isatis.neo":
        return isatis_neo.matrix_to_vario(R)
    else:
        return vulcan.matrix_to_vario(R)


def _make_ellipsoid_trace(R: np.ndarray, a1: float, a2: float, a3: float,
                          color: str, name: str, opacity: float = 0.4):
    """Cria um trace Plotly surface para a elipsoide."""
    X, Y, Z = ellipsoid_surface(R, a1, a2, a3, n=30)
    return go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[[0, color], [1, color]],
        opacity=opacity,
        showscale=False,
        name=name,
        hoverinfo="skip",
    )


def render():
    st.title("📡 Parâmetros de Variograma")
    st.caption("Conversão de ângulos de anisotropia entre Leapfrog, Isatis.neo e Vulcan.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        src = st.selectbox("Software de origem", SOFTWARES, key="vario_src")
        _input_fields_vario(src)
        st.subheader("Alcances (semieixos)")
        a1 = st.number_input("a1 — maior alcance", min_value=0.1, value=100.0, step=1.0, key="vario_a1")
        a2 = st.number_input("a2 — alcance intermediário", min_value=0.1, value=60.0, step=1.0, key="vario_a2")
        a3 = st.number_input("a3 — menor alcance", min_value=0.1, value=20.0, step=1.0, key="vario_a3")
        dst = st.selectbox("Software de destino", SOFTWARES, key="vario_dst")
        convert_clicked = st.button("🔄 Converter", key="vario_convert")

    if convert_clicked:
        R = _vario_to_matrix(src, a1, a2, a3)
        angles_dst = _decompose_to_dst(R, dst)
        st.session_state["vario_result"] = (R, angles_dst, a1, a2, a3, src, dst)

    if "vario_result" in st.session_state:
        R, angles_dst, a1_s, a2_s, a3_s, src_s, dst_s = st.session_state["vario_result"]

        with col_right:
            st.subheader("Resultado")
            labels = {
                "Leapfrog": ("Bearing (°)", "Plunge (°)", "Rake (°)"),
                "Isatis.neo": ("Azimute (°)", "Mergulho (°)", "Rake (°)"),
                "Vulcan": ("Bearing (°)", "Plunge (°)", "Dip (°)"),
            }
            lbs = labels[dst_s]
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric(lbs[0], f"{angles_dst[0]:.2f}°")
            with rc2:
                st.metric(lbs[1], f"{angles_dst[1]:.2f}°")
            with rc3:
                st.metric(lbs[2], f"{angles_dst[2]:.2f}°")

            # Elipsoide 3D — original (azul) e convertido (vermelho)
            R_dst = _vario_to_matrix(dst_s, a1_s, a2_s, a3_s) if False else R  # mesma R
            trace_orig = _make_ellipsoid_trace(R, a1_s, a2_s, a3_s, "blue", f"Original ({src_s})", 0.4)

            # Reconstruir R do destino para validação
            if dst_s == "Leapfrog":
                R_dst = leapfrog.vario_to_matrix(*angles_dst)
            elif dst_s == "Isatis.neo":
                R_dst = isatis_neo.vario_to_matrix(*angles_dst)
            else:
                R_dst = vulcan.vario_to_matrix(*angles_dst)

            trace_conv = _make_ellipsoid_trace(R_dst, a1_s, a2_s, a3_s, "red", f"Convertido ({dst_s})", 0.3)

            # Eixos de referência
            mx = max(a1_s, a2_s, a3_s) * 1.2
            axis_traces = [
                go.Scatter3d(x=[0, mx], y=[0, 0], z=[0, 0], mode="lines+text",
                             line=dict(color="red", width=3),
                             text=["", "E"], textposition="top center", name="Leste"),
                go.Scatter3d(x=[0, 0], y=[0, mx], z=[0, 0], mode="lines+text",
                             line=dict(color="green", width=3),
                             text=["", "N"], textposition="top center", name="Norte"),
                go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, mx], mode="lines+text",
                             line=dict(color="blue", width=3),
                             text=["", "Z"], textposition="top center", name="Cima"),
            ]

            fig = go.Figure(data=[trace_orig, trace_conv] + axis_traces)
            fig.update_layout(
                title="Validação: elipsoides devem coincidir",
                scene=dict(
                    xaxis_title="Leste (X)",
                    yaxis_title="Norte (Y)",
                    zaxis_title="Cima (Z)",
                ),
                height=500,
                showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        if dst_s == "Isatis.neo":
            st.warning("⚠️ Conversão para Isatis.neo: sinal do ângulo de mergulho a confirmar com documentação oficial.")

    from help_system import render_help_button
    render_help_button("variograma", "📖 Como funciona a conversão de variogramas?")
