import streamlit as st
from pathlib import Path

# Mapeamento de cada chave para os marcadores de início e fim no reference.md
SECTIONS = {
    "sobre":       ("## 1. Sistema de Coordenadas", "## 2."),
    "discos":      ("## 2. Discos Estruturais",     "## 3."),
    "variograma":  ("## 3. Parâmetros de Variograma", "## 4."),
    "blocos":      ("## 4. Rotação de Modelo de Blocos", "## 5."),
    "coordenadas": ("## 5. Coordenadas de Pontos",  "## 6."),
    "validacao":   ("## 6. Validação Visual",        "## 7."),
    "testes":      ("## 7. Casos de Teste",          "## 8."),
    "referencias": ("## 8. Referências",             None),
}

def load_reference_section(section_key: str) -> str:
    """Carrega uma seção específica do docs/reference.md pelo marcador de título."""
    ref_path = Path(__file__).parent / "docs" / "reference.md"
    content = ref_path.read_text(encoding="utf-8")
    start_marker, end_marker = SECTIONS[section_key]
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return "_Seção não encontrada._"
    if end_marker:
        end_idx = content.find(end_marker, start_idx)
        return content[start_idx:end_idx].strip() if end_idx != -1 else content[start_idx:].strip()
    return content[start_idx:].strip()

def render_help_button(section_key: str, label: str = "📖 Referência técnica"):
    """
    Renderiza um expander colapsado com a seção relevante do reference.md.
    Chamar no final de cada página do app.
    """
    with st.expander(label, expanded=False):
        st.markdown(load_reference_section(section_key))
        st.divider()
        st.caption("📄 Documento completo em `docs/reference.md` no repositório.")

def render_about_panel():
    """
    Renderiza o painel de instruções da página inicial (app.py).
    """
    st.markdown("## 🪨 GeoRoset")
    st.markdown("**Conversor open-source de convenções geológicas entre Leapfrog, Isatis.neo e Vulcan.**")
    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
### Como usar

1. Selecione a **página** na barra lateral
2. Escolha o **software de origem** e o de **destino**
3. **Conversão individual** — insira os ângulos e clique em Converter
4. **Conversão em tabela** — digite ou carregue um CSV com múltiplos valores
5. Verifique o **gráfico de validação** — original (azul) e convertido (vermelho) devem se sobrepor
6. Baixe os resultados em CSV
""")

    with col2:
        st.markdown("""
### Páginas disponíveis

| Página | Converte | Gráfico |
|---|---|---|
| 🪨 Discos Estruturais | Dip/Dip Direction ↔ Bearing/Plunge | Esteronet de Schmidt |
| 📡 Variograma | Ângulos de anisotropia | Elipsoide 3D |
| 📦 Modelo de Blocos | Rotação dos eixos do grid | Caixa 3D com vetores |
| 📍 Coordenadas | Colunas e convenção de Z | — |
""")

    st.divider()

    st.markdown("""
### Convenções resumidas

| | **Leapfrog** | **Isatis.neo** | **Vulcan** |
|---|---|---|---|
| **Disco** | Dip Direction + Dip | Azimute + Dip *(igual LF)* | Bearing da **normal** + Plunge |
| **Variograma** | Z-X-Z: Rz(−α)·Rx(−β)·Rz(γ) | Z-X-X: Rz(−α)·Rx(−β)·Rx(ω) | X-Y-Z: Rx(α)·Ry(β)·Rz(γ) |
| **Blocos** | Z-X-Z: Rz(α)·Rx(β)·Rz(γ) | Z-X-Z *(sinais a confirmar)* | X-Y-Z: Rx(α)·Ry(β)·Rz(γ) |

> ⚠️ Onde houver incerteza sobre o Isatis.neo, o resultado é marcado com aviso amarelo.
""")
    render_help_button("referencias", "📚 Ver referências bibliográficas")
