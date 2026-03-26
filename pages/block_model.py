"""
pages/block_model.py
====================
Página Streamlit para conversão de rotação de modelo de blocos.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from converters import leapfrog, isatis_neo, vulcan
from core.blockmodel import block_axes, unit_block_corners

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan"]


def _block_to_matrix(software: str) -> np.ndarray:
    """Lê os ângulos da session_state e constrói a matriz de rotação."""
    a = st.session_state.get("block_a1", 0.0)
    b = st.session_state.get("block_a2", 0.0)
    c = st.session_state.get("block_a3", 0.0)
    if software == "Leapfrog":
        return leapfrog.block_to_matrix(a, b, c)
    elif software == "Isatis.neo":
        return isatis_neo.block_to_matrix(a, b, c)
    else:
        return vulcan.block_to_matrix(a, b, c)


def _decompose(R: np.ndarray, dst: str) -> tuple:
    if dst == "Leapfrog":
        return leapfrog.matrix_to_block(R)
    elif dst == "Isatis.neo":
        return isatis_neo.matrix_to_block(R)
    else:
        return vulcan.matrix_to_block(R)


def _block_traces(R: np.ndarray, offset=None, alpha: float = 0.5, suffix: str = ""):
    """Gera traces Plotly para o bloco unitário e seus eixos locais."""
    corners = unit_block_corners(R)
    if offset is not None:
        corners = corners + np.array(offset)
    u, v, w = block_axes(R)

    # Faces do cubo (12 triângulos)
    face_idx = [
        [0,1,2], [0,2,3],  # fundo
        [4,5,6], [4,6,7],  # topo
        [0,1,5], [0,5,4],  # frente
        [2,3,7], [2,7,6],  # trás
        [0,3,7], [0,7,4],  # esquerda
        [1,2,6], [1,6,5],  # direita
    ]
    i_idx = [f[0] for f in face_idx]
    j_idx = [f[1] for f in face_idx]
    k_idx = [f[2] for f in face_idx]

    cx = corners[:, 0]
    cy = corners[:, 1]
    cz = corners[:, 2]
    center = corners.mean(axis=0)

    cube = go.Mesh3d(
        x=cx, y=cy, z=cz,
        i=i_idx, j=j_idx, k=k_idx,
        opacity=alpha,
        color="lightblue" if not suffix else "lightsalmon",
        name=f"Bloco{suffix}",
        showlegend=True,
    )

    # Vetores dos eixos locais
    scale = 0.7
    axis_colors = ["red", "green", "blue"]
    axis_labels = ["U", "V", "W"]
    axis_vecs = [u, v, w]
    cone_traces = []
    for color, label, vec in zip(axis_colors, axis_labels, axis_vecs):
        end = center + vec * scale
        cone_traces.append(go.Cone(
            x=[end[0]], y=[end[1]], z=[end[2]],
            u=[vec[0]], v=[vec[1]], w=[vec[2]],
            sizeref=0.2,
            colorscale=[[0, color], [1, color]],
            showscale=False,
            name=f"{label}{suffix}",
        ))

    return [cube] + cone_traces


def render():
    st.title("📦 Modelo de Blocos")
    st.caption("Conversão de ângulos de rotação do grid de blocos entre Leapfrog, Isatis.neo e Vulcan.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        src = st.selectbox("Software de origem", SOFTWARES, key="block_src")
        labels = {
            "Leapfrog": ("Bearing (°)", "Plunge (°)", "Dip (°)"),
            "Isatis.neo": ("Azimute (°)", "Mergulho (°)", "Rake (°)"),
            "Vulcan": ("Bearing (°)", "Plunge (°)", "Dip (°)"),
        }
        lb = labels[src]
        st.number_input(lb[0], 0.0, 360.0, step=1.0, key="block_a1")
        st.number_input(lb[1], 0.0, 90.0, step=1.0, key="block_a2")
        st.number_input(lb[2], 0.0, 360.0, step=1.0, key="block_a3")
        dst = st.selectbox("Software de destino", SOFTWARES, key="block_dst")
        convert_clicked = st.button("🔄 Converter", key="block_convert")

    if convert_clicked:
        R = _block_to_matrix(src)
        angles_dst = _decompose(R, dst)
        st.session_state["block_result"] = (R, angles_dst, src, dst)

    if "block_result" in st.session_state:
        R, angles_dst, src_s, dst_s = st.session_state["block_result"]

        with col_right:
            st.subheader("Resultado")
            lb_dst = labels.get(dst_s, ("A1 (°)", "A2 (°)", "A3 (°)"))
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric(lb_dst[0], f"{angles_dst[0]:.2f}°")
            with rc2:
                st.metric(lb_dst[1], f"{angles_dst[1]:.2f}°")
            with rc3:
                st.metric(lb_dst[2], f"{angles_dst[2]:.2f}°")

            # Reconstruir R do destino para comparação visual
            if dst_s == "Leapfrog":
                R_dst = leapfrog.block_to_matrix(*angles_dst)
            elif dst_s == "Isatis.neo":
                R_dst = isatis_neo.block_to_matrix(*angles_dst)
            else:
                R_dst = vulcan.block_to_matrix(*angles_dst)

            traces_orig = _block_traces(R, offset=[0, 0, 0], alpha=0.5, suffix="")
            traces_conv = _block_traces(R_dst, offset=[0, 0, 0], alpha=0.3, suffix=" (conv)")

            fig = go.Figure(data=traces_orig + traces_conv)
            fig.update_layout(
                title="Validação: vetores dos eixos devem coincidir",
                scene=dict(
                    xaxis_title="Leste (X)",
                    yaxis_title="Norte (Y)",
                    zaxis_title="Cima (Z)",
                    aspectmode="cube",
                ),
                height=500,
            )
            st.plotly_chart(fig, use_container_width=True)

        if dst_s == "Isatis.neo":
            st.warning("⚠️ Conversão para Isatis.neo: sinal do ângulo de mergulho a confirmar com documentação oficial.")

    from help_system import render_help_button
    render_help_button("blocos", "📖 Como funciona a rotação de modelo de blocos?")
