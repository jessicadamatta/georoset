"""
pages/structural_discs.py
=========================
Página Streamlit para conversão de discos estruturais entre Leapfrog, Isatis.neo e Vulcan.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from converters.cross_converters import (
    leapfrog_to_vulcan_disc,
    vulcan_to_leapfrog_disc,
    leapfrog_to_isatis_disc,
    isatis_to_leapfrog_disc,
    vulcan_to_isatis_disc,
    isatis_to_vulcan_disc,
)
from converters import leapfrog, vulcan, isatis_neo

try:
    import mplstereonet
    HAS_STEREONET = True
except ImportError:
    HAS_STEREONET = False

SOFTWARES = ["Leapfrog", "Isatis.neo", "Vulcan"]


def _get_dip_dd(software: str, key_prefix: str) -> tuple[float, float]:
    """Obtém dip e dip_direction a partir dos inputs da interface."""
    if software == "Vulcan":
        bearing = st.session_state.get(f"{key_prefix}_bearing", 0.0)
        plunge = st.session_state.get(f"{key_prefix}_plunge", 0.0)
        dip, dd = vulcan_to_leapfrog_disc(bearing, plunge)
    else:
        dip = st.session_state.get(f"{key_prefix}_dip", 0.0)
        dd = st.session_state.get(f"{key_prefix}_dd", 0.0)
    return float(dip), float(dd)


def _input_fields(software: str, key_prefix: str):
    """Renderiza os campos de entrada conforme o software selecionado."""
    if software == "Vulcan":
        st.number_input(
            "Bearing da normal (°)",
            min_value=0.0, max_value=360.0, step=1.0,
            key=f"{key_prefix}_bearing",
        )
        st.number_input(
            "Plunge da normal (°)",
            min_value=0.0, max_value=90.0, step=1.0,
            key=f"{key_prefix}_plunge",
        )
    else:
        label_dd = "Dip Direction (°)" if software == "Leapfrog" else "Azimute (°)"
        st.number_input(
            "Dip (°)",
            min_value=0.0, max_value=90.0, step=1.0,
            key=f"{key_prefix}_dip",
        )
        st.number_input(
            label_dd,
            min_value=0.0, max_value=360.0, step=1.0,
            key=f"{key_prefix}_dd",
        )


def _convert(dip_orig: float, dd_orig: float, src: str, dst: str) -> tuple[float, float, str, str]:
    """Realiza a conversão e retorna os valores no formato do software de destino."""
    warning_msg = ""
    # Converter sempre via Leapfrog como intermediário
    # Origem → normal unitário
    if src == "Leapfrog":
        normal = leapfrog.disc_to_normal(dip_orig, dd_orig)
    elif src == "Isatis.neo":
        normal = isatis_neo.disc_to_normal(dip_orig, dd_orig)
    else:
        # Vulcan: dip_orig/dd_orig já são dip/dip_direction internos
        normal = leapfrog.disc_to_normal(dip_orig, dd_orig)

    # Normal → destino
    if dst == "Leapfrog":
        v1, v2 = leapfrog.normal_to_disc(normal)
        label1, label2 = "Dip (°)", "Dip Direction (°)"
    elif dst == "Isatis.neo":
        v1, v2 = isatis_neo.normal_to_disc(normal)
        label1, label2 = "Dip (°)", "Azimute (°)"
        warning_msg = "⚠️ Conversão para Isatis.neo: convenção de disco idêntica ao Leapfrog. Sem incerteza de sinal para discos."
    else:
        v1_b, v2_p = vulcan.normal_to_disc(normal)
        v1, v2 = v1_b, v2_p
        label1, label2 = "Bearing da normal (°)", "Plunge da normal (°)"

    return float(v1), float(v2), label1, label2


def _plot_stereonet(dip_orig: float, dd_orig: float, dip_conv: float, dd_conv: float,
                    src_label: str, dst_label: str):
    """Plota esteronet de Schmidt com os dois polos."""
    fig = plt.figure(figsize=(5, 5))
    if HAS_STEREONET:
        ax = fig.add_subplot(111, projection="stereonet")
        # Polo original (triângulo azul)
        ax.pole(dd_orig, dip_orig, "b^", markersize=10, label=src_label)
        # Polo convertido (círculo vermelho)
        ax.pole(dd_conv, dip_conv, "ro", markersize=8, label=dst_label)
        ax.grid()
        ax.set_title("Validação: os polos devem se sobrepor", fontsize=10)
        ax.legend(loc="lower left", fontsize=8)
    else:
        ax = fig.add_subplot(111)
        ax.set_aspect("equal")
        theta_orig = np.radians(dd_orig)
        r_orig = dip_orig / 90.0
        theta_conv = np.radians(dd_conv)
        r_conv = dip_conv / 90.0
        circle = plt.Circle((0, 0), 1, fill=False, color="gray")
        ax.add_patch(circle)
        ax.plot(r_orig * np.sin(theta_orig), r_orig * np.cos(theta_orig),
                "b^", markersize=10, label=src_label)
        ax.plot(r_conv * np.sin(theta_conv), r_conv * np.cos(theta_conv),
                "ro", markersize=8, label=dst_label)
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_title("Validação (projeção simplificada)\nInstale mplstereonet para esteronet completo")
        ax.legend(fontsize=8)
        ax.axis("off")
    return fig


def render():
    st.title("🪨 Discos Estruturais")
    st.caption("Conversão de dip/dip_direction entre Leapfrog, Isatis.neo e Vulcan.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        src = st.selectbox("Software de origem", SOFTWARES, key="disc_src")
        _input_fields(src, "disc_src")
        dst = st.selectbox("Software de destino", SOFTWARES, key="disc_dst")
        convert_clicked = st.button("🔄 Converter", key="disc_convert")

    if convert_clicked or "disc_result" in st.session_state:
        dip_orig, dd_orig = _get_dip_dd(src, "disc_src")
        v1, v2, label1, label2 = _convert(dip_orig, dd_orig, src, dst)
        st.session_state["disc_result"] = (dip_orig, dd_orig, v1, v2, label1, label2, src, dst)

    if "disc_result" in st.session_state:
        dip_orig, dd_orig, v1, v2, label1, label2, src_s, dst_s = st.session_state["disc_result"]

        with col_right:
            st.subheader("Resultado")
            rc1, rc2 = st.columns(2)
            with rc1:
                st.metric(label1, f"{v1:.2f}°")
            with rc2:
                st.metric(label2, f"{v2:.2f}°")

            # Para o esteronet, garantir dip/dip_direction do destino
            if dst_s == "Vulcan":
                dip_plot, dd_plot = vulcan_to_leapfrog_disc(v1, v2)
            else:
                dip_plot, dd_plot = v1, v2

            fig = _plot_stereonet(dip_orig, dd_orig, dip_plot, dd_plot, src_s, dst_s)
            st.pyplot(fig)
            plt.close(fig)

        if dst_s == "Isatis.neo":
            st.warning("⚠️ Conversão para Isatis.neo: sinal do ângulo de mergulho a confirmar com documentação oficial.")

    from help_system import render_help_button
    render_help_button("discos", "📖 Como funciona a conversão de discos estruturais?")
