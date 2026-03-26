# GeoRoset — Referência Técnica de Convenções
## Conversão de Rotações e Coordenadas entre Leapfrog, Isatis.neo e Vulcan

> **Como usar este documento:**
> Cada seção descreve como um software define seus ângulos, seguida das equações de conversão.
> O sistema de coordenadas interno do GeoRoset é: **X = Leste, Y = Norte, Z = Cima** (dextrogiro).

---

## 1. Sistema de Coordenadas de Referência

Todos os três softwares usam um sistema de coordenadas geográfico dextrogiro com Z apontando para cima. As diferenças estão na **ordem das rotações** e na **definição dos ângulos**, não no sistema de eixos em si.

```
Z (Cima)
│
│    Y (Norte)
│   /
│  /
│ /
└──────── X (Leste)
```

**Ângulo de azimute:** sempre medido no plano horizontal, sentido horário a partir do Norte (0° = Norte, 90° = Leste, 180° = Sul, 270° = Oeste).

---

## 2. Discos Estruturais

### 2.1 Definição dos ângulos

| Parâmetro | Definição |
|---|---|
| **Dip (mergulho)** | Ângulo entre o plano e a horizontal, medido na direção de máximo mergulho (0° = horizontal, 90° = vertical) |
| **Dip Direction** | Azimute da direção de mergulho máximo |
| **Strike** | Azimute da linha de intersecção do plano com a horizontal. Strike = Dip Direction − 90° |

### 2.2 Convenções por software

| Software | Parâmetro 1 | Parâmetro 2 | Observação |
|---|---|---|---|
| **Leapfrog** | Dip Direction (0–360°, CW from N) | Dip (0–90°) | Convenção geológica padrão RHR |
| **Isatis.neo** | Azimute (0–360°, CW from N) | Dip (0–90°) | Idêntico ao Leapfrog |
| **Vulcan** | Bearing (0–360°, CW from N) | Plunge (0–90°) | Bearing é o azimute da **normal ao plano**, não do mergulho |

### 2.3 Diferença crítica: Vulcan usa a normal ao plano

```
Plunge da normal = 90° − Dip do plano
Azimute da normal = (Dip Direction + 180°) mod 360°
```

### 2.4 Equações de conversão

**Leapfrog/Isatis.neo → Vulcan:**
```
plunge_normal = 90° − dip
bearing_normal = (dip_direction + 180°) mod 360°
```

**Vulcan → Leapfrog/Isatis.neo:**
```
dip = 90° − plunge_normal
dip_direction = (bearing_normal + 180°) mod 360°
```

**Vetor normal unitário (sistema interno X=E, Y=N, Z=Up):**
```
nx = −sin(dip) · sin(dip_direction)
ny = −sin(dip) · cos(dip_direction)
nz = cos(dip)
```
*A normal aponta para o lado oposto ao mergulho no plano horizontal.*

---

## 3. Parâmetros de Variograma (Anisotropia)

### 3.1 Conceito

A elipsoide de anisotropia define as direções e alcances de continuidade espacial:
- **a₁** — maior alcance (máxima continuidade)
- **a₂** — alcance intermediário
- **a₃** — menor alcance (mínima continuidade, geralmente vertical)

### 3.2 Matrizes de rotação elementares

```
        ┌ 1    0       0    ┐
Rx(θ) = │ 0  cos(θ) −sin(θ) │
        └ 0  sin(θ)  cos(θ) ┘

        ┌  cos(θ)  0  sin(θ) ┐
Ry(θ) = │    0     1    0    │
        └ −sin(θ)  0  cos(θ) ┘

        ┌ cos(θ) −sin(θ)  0 ┐
Rz(θ) = │ sin(θ)  cos(θ)  0 │
        └   0       0     1 ┘
```

### 3.3 Convenções por software

| Software | Sequência | Fórmula |
|---|---|---|
| **Leapfrog** | Azimute → Plunge → Rake (Z-X-Z) | R = Rz(−α) · Rx(−β) · Rz(γ) |
| **Isatis.neo** | Azimute → Mergulho → Rake (Z-X-X) | R = Rz(−α) · Rx(−β) · Rx(ω) ⚠️ sinal de β a confirmar |
| **Vulcan** | Bearing → Plunge → Dip (X-Y-Z) | R = Rx(α) · Ry(β) · Rz(γ) |

### 3.4 Estratégia de conversão

```
1. Calcular matriz R completa com os ângulos do software de origem
2. Decompor R na sequência de ângulos do software de destino
3. Tratar gimbal lock (β = 0° ou 90°) explicitamente
```

---

## 4. Rotação de Modelo de Blocos

| Software | Parâmetros | Ordem |
|---|---|---|
| **Leapfrog** | Bearing, Plunge, Dip | Z-X-Z: R = Rz(α) · Rx(β) · Rz(γ) |
| **Isatis.neo** | Azimute, Mergulho, Rake | Z-X-Z (mesma ordem, verificar sinais) |
| **Vulcan** | Bearing, Plunge, Dip | X-Y-Z: R = Rx(α) · Ry(β) · Rz(γ) |

---

## 5. Coordenadas de Pontos e Sondagens

Os três softwares usam o mesmo sistema cartesiano geográfico (X=Leste, Y=Norte, Z=Cota). Para projetos no Brasil em SIRGAS 2000/UTM, não há conversão matemática — apenas reformatação de colunas.

**Casos que requerem conversão real:**
- Troca de fuso UTM → reprojeção via `pyproj`
- SAD69 → SIRGAS 2000 → transformação de datum (~0–3 m de shift)
- Coordenadas locais de mina → UTM → translação + rotação de grid
- Z positivo para baixo (Vulcan sondagens) → Z geográfico: `Z_geo = −Profundidade`

---

## 6. Validação Visual

### 6.1 Esteronet — Discos Estruturais
- Projeção equiárea de Schmidt, hemisfério inferior (convenção geológica padrão)
- Centro = vertical (dip = 90°), borda = horizontal (dip = 0°)
- **Critério:** polo original (triângulo azul) e polo convertido (círculo vermelho) devem se sobrepor perfeitamente

### 6.2 Elipsoide 3D — Variograma
- Elipsoide de anisotropia plotado com eixos N/E/Z de referência
- **Critério:** elipsoide original (azul semitransparente) e convertido (vermelho) devem coincidir

### 6.3 Caixa 3D — Modelo de Blocos
- Bloco unitário com vetores dos eixos locais (U=vermelho, V=verde, W=azul)
- **Critério:** vetores dos eixos locais apontam na mesma direção antes e depois da conversão

---

## 7. Casos de Teste

| Caso | Dip | Dip Direction | Bearing Vulcan | Plunge Vulcan | Normal (X,Y,Z) |
|---|---|---|---|---|---|
| Horizontal | 0° | qualquer | qualquer | 90° | (0, 0, 1) |
| Vertical N-S, para Norte | 90° | 0° | 180° | 0° | (0, −1, 0) |
| Vertical E-W, para Leste | 90° | 90° | 270° | 0° | (1, 0, 0) |
| 45° para Norte | 45° | 0° | 180° | 45° | (0, −0.707, 0.707) |

---

## 8. Referências

- Davis, J.C. (2002). *Statistics and Data Analysis in Geology*, 3rd ed. Wiley.
- Isaaks, E.H. & Srivastava, R.M. (1989). *Applied Geostatistics*. Oxford University Press.
- Documentação oficial: Leapfrog Geo, Isatis.neo, Vulcan (Maptek)

---
*GeoRoset — open-source. Contribuições via GitHub Issues.*
