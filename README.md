# 🪨 GeoRoset

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

**Conversor open-source de convenções geológicas entre Leapfrog, Isatis.neo e Vulcan.**

Geólogos e engenheiros de minas frequentemente precisam migrar dados estruturais, parâmetros de variograma e rotações de modelos de blocos entre softwares, cada um com sua própria convenção de ângulos. O GeoRoset automatiza essas conversões com validação visual integrada.

---

## Convenções comparadas

### Discos Estruturais

| Software | Parâmetro 1 | Parâmetro 2 | Observação |
|---|---|---|---|
| **Leapfrog** | Dip Direction (0–360°, CW from N) | Dip (0–90°) | Convenção geológica padrão |
| **Isatis.neo** | Azimute (0–360°, CW from N) | Dip (0–90°) | Idêntico ao Leapfrog |
| **Vulcan** | Bearing (azimute da **normal**) | Plunge (inclinação da normal) | ⚠️ Usa a normal ao plano, não o vetor de mergulho |

### Parâmetros de Variograma

| Software | Sequência | Fórmula |
|---|---|---|
| **Leapfrog** | Bearing → Plunge → Rake | R = Rz(−α) · Rx(−β) · Rz(γ) |
| **Isatis.neo** | Azimute → Mergulho → Rake | R = Rz(−α) · Rx(−β) · Rx(ω) ⚠️ sinal a confirmar |
| **Vulcan** | Bearing → Plunge → Dip | R = Rx(α) · Ry(β) · Rz(γ) |

### Modelo de Blocos

| Software | Sequência | Fórmula |
|---|---|---|
| **Leapfrog** | Bearing, Plunge, Dip | Z-X-Z: R = Rz(α) · Rx(β) · Rz(γ) |
| **Isatis.neo** | Azimute, Mergulho, Rake | Z-X-Z (sinais a confirmar) |
| **Vulcan** | Bearing, Plunge, Dip | X-Y-Z: R = Rx(α) · Ry(β) · Rz(γ) |

---

## Instalação local

```bash
git clone https://github.com/jessicadamatta/georoset.git
cd georoset
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy no Streamlit Community Cloud

1. Faça fork deste repositório (ou conecte o seu)
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Clique em **New app**
4. Selecione o repositório e o arquivo `app.py`
5. Clique em **Deploy**

---

## Estrutura do projeto

```
georoset/
├── app.py                  # Entrada principal do Streamlit
├── help_system.py          # Sistema de ajuda integrado
├── docs/
│   └── reference.md        # Referência técnica completa de convenções
├── core/
│   ├── rotations.py        # Matrizes de rotação e conversões fundamentais
│   ├── structural.py       # Conversões dip/strike/polo
│   ├── variogram.py        # Elipsoide de anisotropia
│   ├── blockmodel.py       # Rotação de modelo de blocos
│   └── coordinates.py      # Coordenadas de pontos e sondagens
├── converters/
│   ├── leapfrog.py         # Convenções do Leapfrog Geo
│   ├── isatis_neo.py       # Convenções do Isatis.neo
│   ├── vulcan.py           # Convenções do Vulcan (Maptek)
│   └── cross_converters.py # Conversões diretas entre pares de softwares
├── pages/
│   ├── structural_discs.py # Página: discos estruturais
│   ├── variogram_params.py # Página: parâmetros de variograma
│   ├── block_model.py      # Página: modelo de blocos
│   └── coordinates.py      # Página: coordenadas
├── tests/
│   ├── test_rotations.py
│   ├── test_structural.py
│   └── test_converters.py
└── requirements.txt
```

---

## Como contribuir

1. **Novo software:** crie `converters/novo_software.py` seguindo o padrão dos módulos existentes
2. **Nova página:** crie `pages/novo_software.py` com uma função `render()`
3. **Documentação:** adicione uma seção em `docs/reference.md`
4. **Testes:** adicione casos em `tests/test_converters.py`
5. Abra um Pull Request no GitHub

> ⚠️ Onde houver incerteza sobre convenções (especialmente Isatis.neo), marque com
> `# TODO: validar com documentação oficial` e use a flag `ISATIS_NEO_SIGN_CONVENTION`.

---

## Licença

MIT — veja [LICENSE](LICENSE) para detalhes.
