"""
pages/structural_discs.py
=========================
Página Streamlit para conversão de discos estruturais entre Leapfrog, Isatis.neo e Vulcan.
Esteronet de Schmidt implementado com Plotly (sem dependência do mplstereonet).
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from converters import leapfrog, vulcan, isatis_neo
from converters.cross_converters import (
    leapfrog_to_vulcan_disc,
    vulcan_to_leapfrog_disc,
    leapfrog_to_isatis_disc,
    isatis_to_leapfrog_disc,
)

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan"]


# ---------------------------------------------------------------------------
# Esteronet de Schmidt (projeção equiárea, hemisfério inferior)
# ---------------------------------------------------------------------------

def _pole_to_stereonet_xy(dip: float, dip_direction: float) -> tuple[float, float]:
    """
    Converte dip/dip_direction para coordenadas 2D na projeção de Schmidt (hemisfério inferior).

    Na projeção equiárea:
        r = sqrt(2) * sin(dip/2)   (borda = dip=0, centro = dip=90°)
    """
    dip_rad = np.radians(dip)
    dd_rad = np.radians(dip_direction)
    r = np.sqrt(2) * np.sin(dip_rad / 2)
    x = r * np.sin(dd_rad)
    y = r * np.cos(dd_rad)
    return float(x), float(y)


def _stereonet_figure(
    dip_orig: float, dd_orig: float,
    dip_conv: float, dd_conv: float,
    src_label: str, dst_label: str,
) -> go.Figure:
    """Cria figura Plotly com esteronet de Schmidt e dois polos."""
    fig = go.Figure()

    # Círculo externo (dip=0, borda)
    theta = np.linspace(0, 2 * np.pi, 361)
    fig.add_trace(go.Scatter(
        x=np.cos(theta), y=np.sin(theta),
        mode="lines", line=dict(color="black", width=1.5),
        showlegend=False, hoverinfo="skip",
    ))

    # Linhas de grade: círculos de dip constante (10°, 30°, 60°, 90°)
    for dip_g in [10, 30, 60, 90]:
        r_g = np.sqrt(2) * np.sin(np.radians(dip_g) / 2)
        fig.add_trace(go.Scatter(
            x=r_g * np.cos(theta), y=r_g * np.sin(theta),
            mode="lines", line=dict(color="lightgray", width=0.5, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))

    # Linhas de grade: raios de dip_direction (N, NE, E, SE, S, SW, W, NW)
    for az in range(0, 360, 45):
        az_r = np.radians(az)
        fig.add_trace(go.Scatter(
            x=[0, np.sin(az_r)], y=[0, np.cos(az_r)],
            mode="lines", line=dict(color="lightgray", width=0.5, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))

    # Rótulos cardeais
    for label, xp, yp in [("N", 0, 1.08), ("E", 1.08, 0), ("S", 0, -1.12), ("W", -1.12, 0)]:
        fig.add_annotation(x=xp, y=yp, text=f"<b>{label}</b>", showarrow=False,
                           font=dict(size=12, color="gray"))

    # Polo original (triângulo azul)
    x_o, y_o = _pole_to_stereonet_xy(dip_orig, dd_orig)
    fig.add_trace(go.Scatter(
        x=[x_o], y=[y_o],
        mode="markers",
        marker=dict(symbol="triangle-up", size=14, color="blue", line=dict(color="darkblue", width=1)),
        name=f"Original ({src_label})",
        hovertemplate=f"<b>{src_label}</b><br>Dip={dip_orig:.1f}°  Dir={dd_orig:.1f}°<extra></extra>",
    ))

    # Polo convertido (círculo vermelho)
    x_c, y_c = _pole_to_stereonet_xy(dip_conv, dd_conv)
    fig.add_trace(go.Scatter(
        x=[x_c], y=[y_c],
        mode="markers",
        marker=dict(symbol="circle", size=12, color="red", line=dict(color="darkred", width=1)),
        name=f"Convertido ({dst_label})",
        hovertemplate=f"<b>{dst_label}</b><br>Dip={dip_conv:.1f}°  Dir={dd_conv:.1f}°<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Validação: os polos devem se sobrepor", font=dict(size=13)),
        xaxis=dict(visible=False, range=[-1.25, 1.25]),
        yaxis=dict(visible=False, range=[-1.25, 1.25], scaleanchor="x"),
        height=430,
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(x=0.01, y=0.01, bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------------------------
# Helpers de UI
# ---------------------------------------------------------------------------

def _input_fields(software: str, key_prefix: str):
    """Renderiza os campos de entrada conforme o software selecionado."""
    if software == "Vulcan":
        st.number_input("Bearing da normal (°)", min_value=0.0, max_value=360.0,
                        step=1.0, key=f"{key_prefix}_bearing")
        st.number_input("Plunge da normal (°)", min_value=0.0, max_value=90.0,
                        step=1.0, key=f"{key_prefix}_plunge")
    else:
        label_dd = "Dip Direction (°)" if software == "Leapfrog" else "Azimute (°)"
        st.number_input("Dip (°)", min_value=0.0, max_value=90.0,
                        step=1.0, key=f"{key_prefix}_dip")
        st.number_input(label_dd, min_value=0.0, max_value=360.0,
                        step=1.0, key=f"{key_prefix}_dd")


def _read_as_dip_dd(software: str, key_prefix: str) -> tuple[float, float]:
    """Lê os inputs e converte sempre para dip + dip_direction interno."""
    if software == "Vulcan":
        bearing = float(st.session_state.get(f"{key_prefix}_bearing", 0.0))
        plunge = float(st.session_state.get(f"{key_prefix}_plunge", 0.0))
        dip, dd = vulcan_to_leapfrog_disc(bearing, plunge)
    else:
        dip = float(st.session_state.get(f"{key_prefix}_dip", 0.0))
        dd = float(st.session_state.get(f"{key_prefix}_dd", 0.0))
    return dip, dd


def _convert_and_format(
    dip: float, dd: float, src: str, dst: str
) -> tuple[float, float, float, float, str, str]:
    """
    Converte e retorna:
        dip_plot, dd_plot  — para o esteronet (sempre em dip/dip_direction)
        v1, v2             — valores no formato nativo do destino
        label1, label2     — rótulos dos campos
    """
    normal = leapfrog.disc_to_normal(dip, dd) if src != "Vulcan" else \
             leapfrog.disc_to_normal(dip, dd)  # interno já é Leapfrog

    if dst == "Leapfrog":
        v1, v2 = leapfrog.normal_to_disc(normal)
        label1, label2 = "Dip (°)", "Dip Direction (°)"
        dip_plot, dd_plot = v1, v2
    elif dst == "Isatis.neo":
        v1, v2 = isatis_neo.normal_to_disc(normal)
        label1, label2 = "Dip (°)", "Azimute (°)"
        dip_plot, dd_plot = v1, v2
    else:
        v1, v2 = vulcan.normal_to_disc(normal)
        label1, label2 = "Bearing da normal (°)", "Plunge da normal (°)"
        dip_plot, dd_plot = vulcan_to_leapfrog_disc(v1, v2)

    return dip_plot, dd_plot, float(v1), float(v2), label1, label2


# ---------------------------------------------------------------------------
# Render principal
# ---------------------------------------------------------------------------

def render():
    st.title("🪨 Discos Estruturais")
    st.caption("Converta dip/dip_direction entre Leapfrog, Isatis.neo e Vulcan.")

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        src = st.selectbox("Software de origem", SOFTWARES, key="disc_src")
        _input_fields(src, "disc_src")
        st.divider()
        dst = st.selectbox("Software de destino", SOFTWARES, key="disc_dst")
        convert_clicked = st.button("🔄 Converter", key="disc_convert",
                                    use_container_width=True, type="primary")

    if convert_clicked:
        dip_orig, dd_orig = _read_as_dip_dd(src, "disc_src")
        dip_plot, dd_plot, v1, v2, label1, label2 = _convert_and_format(
            dip_orig, dd_orig, src, dst
        )
        st.session_state["disc_result"] = {
            "dip_orig": dip_orig, "dd_orig": dd_orig,
            "dip_plot": dip_plot, "dd_plot": dd_plot,
            "v1": v1, "v2": v2,
            "label1": label1, "label2": label2,
            "src": src, "dst": dst,
        }

    if "disc_result" in st.session_state:
        r = st.session_state["disc_result"]
        with col_right:
            st.subheader("Resultado")
            c1, c2 = st.columns(2)
            c1.metric(r["label1"], f"{r['v1']:.2f}°")
            c2.metric(r["label2"], f"{r['v2']:.2f}°")

            fig = _stereonet_figure(
                r["dip_orig"], r["dd_orig"],
                r["dip_plot"], r["dd_plot"],
                r["src"], r["dst"],
            )
            st.plotly_chart(fig, use_container_width=True)

        if r["dst"] == "Isatis.neo":
            st.warning("⚠️ Conversão para Isatis.neo: sinal do ângulo de mergulho a confirmar com documentação oficial.")

    from help_system import render_help_button
    render_help_button("discos", "📖 Como funciona a conversão de discos estruturais?")
