"""
pages/structural_discs.py
=========================
Conversão de discos estruturais — conversão individual com esteronet
e conversão em lote via tabela editável ou CSV.
"""

import streamlit as st
import numpy as np
import pandas as pd
import io
import plotly.graph_objects as go
from converters import leapfrog, vulcan, isatis_neo
from converters.cross_converters import vulcan_to_leapfrog_disc

SOFTWARES = ["Leapfrog / Isatis.neo", "Vulcan"]

# Mapeamento simples: Leapfrog e Isatis.neo usam a mesma convenção de disco
_DISC_COLS = {
    "Leapfrog / Isatis.neo": ("Dip (°)", "Dip Direction (°)"),
    "Vulcan": ("Bearing da normal (°)", "Plunge da normal (°)"),
}


def _to_internal(software: str, a: float, b: float) -> tuple[float, float]:
    """Converte para dip/dip_direction interno."""
    if software == "Vulcan":
        return vulcan_to_leapfrog_disc(a, b)
    return float(a), float(b)


def _from_internal(software: str, dip: float, dd: float) -> tuple[float, float]:
    """Converte dip/dip_direction interno para o formato do software."""
    if software == "Vulcan":
        return vulcan.normal_to_disc(leapfrog.disc_to_normal(dip, dd))
    return float(dip), float(dd)


# ---------------------------------------------------------------------------
# Esteronet de Schmidt (Plotly)
# ---------------------------------------------------------------------------

def _pole_xy(dip: float, dd: float) -> tuple[float, float]:
    r = np.sqrt(2) * np.sin(np.radians(dip) / 2)
    return r * np.sin(np.radians(dd)), r * np.cos(np.radians(dd))


def _stereonet(dip_o, dd_o, dip_c, dd_c, src_label, dst_label):
    fig = go.Figure()
    t = np.linspace(0, 2 * np.pi, 361)
    # borda
    fig.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode="lines",
                             line=dict(color="#555", width=1.5), showlegend=False, hoverinfo="skip"))
    # grade
    for d in [30, 60]:
        r = np.sqrt(2) * np.sin(np.radians(d) / 2)
        fig.add_trace(go.Scatter(x=r*np.cos(t), y=r*np.sin(t), mode="lines",
                                 line=dict(color="#ddd", width=0.8, dash="dot"),
                                 showlegend=False, hoverinfo="skip"))
    for az in range(0, 360, 45):
        a = np.radians(az)
        fig.add_trace(go.Scatter(x=[0, np.sin(a)], y=[0, np.cos(a)], mode="lines",
                                 line=dict(color="#ddd", width=0.8, dash="dot"),
                                 showlegend=False, hoverinfo="skip"))
    for lbl, xp, yp in [("N", 0, 1.1), ("E", 1.12, 0), ("S", 0, -1.15), ("W", -1.18, 0)]:
        fig.add_annotation(x=xp, y=yp, text=f"<b>{lbl}</b>", showarrow=False,
                           font=dict(size=11, color="#888"))
    xo, yo = _pole_xy(dip_o, dd_o)
    xc, yc = _pole_xy(dip_c, dd_c)
    fig.add_trace(go.Scatter(x=[xo], y=[yo], mode="markers",
                             marker=dict(symbol="triangle-up", size=16, color="#1f77b4",
                                         line=dict(color="#0a4a8a", width=1.5)),
                             name=f"Original ({src_label})",
                             hovertemplate=f"Dip={dip_o:.1f}°  Dir={dd_o:.1f}°<extra>{src_label}</extra>"))
    fig.add_trace(go.Scatter(x=[xc], y=[yc], mode="markers",
                             marker=dict(symbol="circle", size=14, color="#d62728",
                                         line=dict(color="#8b0000", width=1.5)),
                             name=f"Convertido ({dst_label})",
                             hovertemplate=f"Dip={dip_c:.1f}°  Dir={dd_c:.1f}°<extra>{dst_label}</extra>"))
    fig.update_layout(
        xaxis=dict(visible=False, range=[-1.3, 1.3]),
        yaxis=dict(visible=False, range=[-1.3, 1.3], scaleanchor="x"),
        height=380, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", x=0, y=-0.02, font=dict(size=11)),
        margin=dict(l=5, r=5, t=10, b=5),
    )
    return fig


# ---------------------------------------------------------------------------
# Aba 1 — Conversão Individual
# ---------------------------------------------------------------------------

def _tab_individual(src: str, dst: str):
    c1, c2 = _DISC_COLS[src]
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("#### Entrada")
        a = st.number_input(c1, min_value=0.0, max_value=90.0 if "Dip" in c1 or "Plunge" in c1 else 360.0,
                            step=1.0, value=0.0, key="disc_a")
        b = st.number_input(c2, min_value=0.0, max_value=360.0, step=1.0, value=0.0, key="disc_b")
        if st.button("🔄 Converter", key="disc_btn_single", use_container_width=True, type="primary"):
            dip_i, dd_i = _to_internal(src, a, b)
            v1, v2 = _from_internal(dst, dip_i, dd_i)
            # para esteronet sempre em dip/dd
            dip_plot_o, dd_plot_o = dip_i, dd_i
            dip_plot_c, dd_plot_c = _to_internal(dst, v1, v2)
            st.session_state["disc_single"] = dict(
                v1=v1, v2=v2, dip_o=dip_plot_o, dd_o=dd_plot_o,
                dip_c=dip_plot_c, dd_c=dd_plot_c, src=src, dst=dst,
            )

    if "disc_single" in st.session_state:
        r = st.session_state["disc_single"]
        lc1, lc2 = _DISC_COLS[r["dst"]]
        with col_out:
            st.markdown("#### Resultado")
            m1, m2 = st.columns(2)
            m1.metric(lc1, f"{r['v1']:.3f}°")
            m2.metric(lc2, f"{r['v2']:.3f}°")
            st.plotly_chart(
                _stereonet(r["dip_o"], r["dd_o"], r["dip_c"], r["dd_c"], r["src"], r["dst"]),
                use_container_width=True,
            )

        if r["dst"] in ("Leapfrog / Isatis.neo",) and "Isatis" in r["dst"]:
            st.warning("⚠️ Isatis.neo: sinal do mergulho a confirmar com documentação oficial.")


# ---------------------------------------------------------------------------
# Aba 2 — Conversão em Tabela
# ---------------------------------------------------------------------------

def _tab_tabela(src: str, dst: str):
    c1, c2 = _DISC_COLS[src]
    lc1, lc2 = _DISC_COLS[dst]

    st.markdown("#### Fonte dos dados")
    fonte = st.radio("", ["✏️ Digitar manualmente", "📂 Carregar CSV"], horizontal=True, key="disc_fonte")

    if fonte == "✏️ Digitar manualmente":
        st.caption(f"Edite a tabela abaixo. Colunas: **{c1}** e **{c2}**")
        default = pd.DataFrame({c1: [0.0, 30.0, 45.0, 60.0, 90.0],
                                 c2: [0.0, 45.0, 90.0, 180.0, 270.0]})
        df_in = st.data_editor(default, num_rows="dynamic", use_container_width=True,
                               key="disc_editor",
                               column_config={
                                   c1: st.column_config.NumberColumn(min_value=0, max_value=90, step=0.1),
                                   c2: st.column_config.NumberColumn(min_value=0, max_value=360, step=0.1),
                               })
    else:
        uploaded = st.file_uploader(f"CSV com colunas **{c1}** e **{c2}**", type=["csv"], key="disc_csv")
        if uploaded is None:
            st.info(f"Carregue um CSV com as colunas `{c1}` e `{c2}`.")
            return
        df_in = pd.read_csv(uploaded)
        if c1 not in df_in.columns or c2 not in df_in.columns:
            st.error(f"O CSV precisa ter as colunas: `{c1}` e `{c2}`")
            return
        st.dataframe(df_in[[c1, c2]].head(10), use_container_width=True)

    if st.button("🔄 Converter Tabela", key="disc_btn_table", use_container_width=True, type="primary"):
        rows = []
        for _, row in df_in.iterrows():
            try:
                a_val = float(row[c1])
                b_val = float(row[c2])
                dip_i, dd_i = _to_internal(src, a_val, b_val)
                v1, v2 = _from_internal(dst, dip_i, dd_i)
                rows.append({c1: a_val, c2: b_val, lc1: round(v1, 4), lc2: round(v2, 4)})
            except Exception:
                rows.append({c1: row.get(c1), c2: row.get(c2), lc1: None, lc2: None})
        df_out = pd.DataFrame(rows)
        st.session_state["disc_table_result"] = df_out

    if "disc_table_result" in st.session_state:
        df_out = st.session_state["disc_table_result"]
        st.markdown("#### Resultado da conversão")

        # Tabelas lado a lado
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Entrada — {src}**")
            st.dataframe(df_out[[c1, c2]].style.format("{:.3f}"), use_container_width=True, hide_index=True)
        with col_b:
            st.markdown(f"**Saída — {dst}**")
            st.dataframe(df_out[[lc1, lc2]].style.format("{:.3f}"), use_container_width=True, hide_index=True)

        st.divider()
        buf = io.StringIO()
        df_out.to_csv(buf, index=False)
        st.download_button("⬇️ Baixar tabela convertida (CSV)", buf.getvalue(),
                           file_name="discos_convertidos.csv", mime="text/csv",
                           use_container_width=True)


# ---------------------------------------------------------------------------
# Render principal
# ---------------------------------------------------------------------------

def render():
    st.title("🪨 Discos Estruturais")

    # Seletores no topo — sempre visíveis
    hdr_l, hdr_m, hdr_r = st.columns([2, 1, 2])
    with hdr_l:
        src = st.selectbox("Software de **origem**", SOFTWARES, key="disc_src_top")
    with hdr_m:
        st.markdown("<div style='text-align:center;padding-top:28px;font-size:22px'>→</div>",
                    unsafe_allow_html=True)
    with hdr_r:
        dst = st.selectbox("Software de **destino**", SOFTWARES, key="disc_dst_top")

    st.divider()

    tab1, tab2 = st.tabs(["🔢 Conversão Individual", "📋 Conversão em Tabela"])
    with tab1:
        _tab_individual(src, dst)
    with tab2:
        _tab_tabela(src, dst)

    from help_system import render_help_button
    render_help_button("discos", "📖 Como funciona a conversão de discos estruturais?")
