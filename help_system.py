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
    st.markdown("""
    ## 🪨 GeoRoset
    **Conversor de convenções geológicas entre Leapfrog, Isatis.neo e Vulcan.**

    ### Como usar
    1. Selecione a página na barra lateral correspondente ao tipo de objeto a converter
    2. Escolha o **software de origem** e insira os ângulos
    3. Escolha o **software de destino**
    4. Clique em **Converter**
    5. Verifique o resultado numérico e o **gráfico de validação** — os dois objetos devem se sobrepor

    ### Páginas disponíveis

    | Página | O que converte |
    |---|---|
    | 🪨 Discos Estruturais | Dip/Dip Direction ↔ Bearing/Plunge |
    | 📡 Parâmetros de Variograma | Ângulos de anisotropia entre softwares |
    | 📦 Modelo de Blocos | Rotação dos eixos do grid de blocos |
    | 📍 Coordenadas | Reformatação e reprojeção de pontos/sondagens |

    ### Validação visual
    Cada página exibe um gráfico onde o objeto **original** (azul) e o objeto **convertido** (vermelho)
    são plotados no mesmo espaço. Se a conversão estiver correta, eles se sobrepõem perfeitamente.

    > ⚠️ Onde houver incerteza sobre a convenção exata do Isatis.neo, o resultado é marcado com
    > um aviso amarelo e uma flag editável no código (`ISATIS_NEO_SIGN_CONVENTION`).
    """)
    render_help_button("referencias", "📚 Ver referências bibliográficas")
