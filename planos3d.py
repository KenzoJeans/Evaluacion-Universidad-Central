import math

import plotly.graph_objects as go
import streamlit as st

CIAN, NIVEL, PANEL, TUBO = "#58a6ff", "#3fb950", "#f0883e", "#d2a8ff"
HOMO_H = 45 / (5.1 * 2.4)  # altura PROVISIONAL del tanque de homogenización (m); reemplazar al medir
HOMO_FRANCO = 0.4  # franco libre supuesto (m)


# ---------------------------- primitivas ----------------------------
def _tr(segs, color=CIAN, w=4):
    x, y, z = [], [], []
    for a, b in segs:
        x += [a[0], b[0], None]
        y += [a[1], b[1], None]
        z += [a[2], b[2], None]
    return go.Scatter3d(x=x, y=y, z=z, mode="lines", line=dict(color=color, width=w), hoverinfo="skip", showlegend=False)


def _txt(x, y, z, t):
    return go.Scatter3d(x=[x], y=[y], z=[z], mode="text", text=[t], textfont=dict(color="#8b949e", size=11),
                        hoverinfo="skip", showlegend=False)


def _rect(x0, y0, z, L, B):
    p = [(x0, y0, z), (x0 + L, y0, z), (x0 + L, y0 + B, z), (x0, y0 + B, z)]
    return [(p[i], p[(i + 1) % 4]) for i in range(4)]


def _caja(x0, y0, z0, L, B, H):
    s = _rect(x0, y0, z0, L, B) + _rect(x0, y0, z0 + H, L, B)
    for (a, _) in _rect(x0, y0, z0, L, B):
        s.append((a, (a[0], a[1], z0 + H)))
    return s


def _circ(cx, cy, z, r, n=48):
    p = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n + 1)]
    return list(zip(p[:-1], p[1:]))


def _gen(cx, cy, r1, z1, r2, z2, n=8):
    return [((cx + r1 * math.cos(2 * math.pi * k / n), cy + r1 * math.sin(2 * math.pi * k / n), z1),
             (cx + r2 * math.cos(2 * math.pi * k / n), cy + r2 * math.sin(2 * math.pi * k / n), z2)) for k in range(n)]


def _cilindro(cx, cy, z0, r, H):
    return _circ(cx, cy, z0, r) + _circ(cx, cy, z0 + H, r) + _gen(cx, cy, r, z0, r, z0 + H)


def _piramide(xi, B, L, zb, sal=0.2):
    cx, cy = xi + L / 2, B / 2
    top = [(xi, 0, zb), (xi + L, 0, zb), (xi + L, B, zb), (xi, B, zb)]
    bot = [(cx - sal / 2, cy - sal / 2, 0), (cx + sal / 2, cy - sal / 2, 0),
           (cx + sal / 2, cy + sal / 2, 0), (cx - sal / 2, cy + sal / 2, 0)]
    return ([(top[i], top[(i + 1) % 4]) for i in range(4)] + [(top[i], bot[i]) for i in range(4)]
            + [(bot[i], bot[(i + 1) % 4]) for i in range(4)])


# ---------------------------- equipos (medidas en m) ----------------------------
def _homogenizacion():  # enterrado: la boca queda a nivel del piso (z = 0)
    L, B, H = 5.1, 2.4, HOMO_H
    piso = _rect(-1.0, -1.0, 0, L + 2, B + 2)
    return [_tr(_caja(0, 0, -H, L, B, H)), _tr(_rect(0, 0, -HOMO_FRANCO, L, B), NIVEL, 3), _tr(piso, GRIS, 3),
            _txt(L / 2, -0.4, 0.1, f"{L} m"), _txt(L + 0.3, B / 2, 0.1, f"{B} m"),
            _txt(-0.5, 0, -H / 2, f"{H:.2f} m (prov.)"), _txt(L / 2, B + 1.2, 0, "nivel del piso")]


def _coagulacion():
    R = 0.75
    legs = [((0.65 * math.cos(a), 0.65 * math.sin(a), 1.5), (0.65 * math.cos(a), 0.65 * math.sin(a), 0))
            for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    agit = [((0, 0, 3.3), (0, 0, 1.1))] + _circ(0, 0, 1.2, 0.3) + _circ(0, 0, 2.1, 0.3)
    return [_tr(_cilindro(0, 0, 1.5, R, 1.5)), _tr(_gen(0, 0, R, 1.5, 0.08, 1.0)), _tr(legs),
            _tr(agit + _caja(-0.15, -0.1, 3.0, 0.3, 0.2, 0.25), PANEL, 3), _tr(_circ(0, 0, 2.7, R), NIVEL, 3),
            _txt(R + 0.2, 0, 3.0, "Ø 1.5 m"), _txt(-R - 0.4, 0, 0, "3.0 m total")]


def _sedimentador():
    B, x0, zt, zb = 1.5, 0.8, 2.95, 0.75
    pir = _piramide(0.8, B, 1.5, zb) + _piramide(2.3, B, 1.5, zb)
    tubos = [((x0, B / 2, 2.65), (3.8, B / 2, 2.65)), ((x0, B / 2, 1.30), (3.8, B / 2, 1.30))]
    return [_tr(_caja(x0, 0, zb, 3.0, B, zt - zb)), _tr(_caja(0, 0, zt - 1.7, 0.8, B, 1.7)), _tr(pir),
            _tr(_caja(x0, 0, 1.51, 3.0, B, 0.55), PANEL, 3), _tr(tubos, TUBO, 5), _tr(_rect(0, 0, 2.65, 3.8, B), NIVEL, 3),
            _txt(0.4, -0.3, zt, "0.80"), _txt(2.3, -0.3, zt, "3.00 m zona de sedimentación"),
            _txt(2.3, B / 2, 1.8, "paneles")]


def _oxidacion():
    R, H = 0.9, 2.4
    nivel = 5.8 / (math.pi * R ** 2)
    return [_tr(_cilindro(0, 0, 0, R, H)), _tr(_circ(0, 0, nivel, R), NIVEL, 3),
            _txt(R + 0.2, 0, H, "Ø 1.8 m"), _txt(-R - 0.4, 0, H / 2, "2.4 m")]


def _filtro(cx, H, r=0.3, neck=0.12):
    return (_cilindro(cx, 0, 0, r, 1.5) + _circ(cx, 0, 0.25, r) + _gen(cx, 0, r, 1.5, neck, H - 0.05)
            + _cilindro(cx, 0, H - 0.05, neck, 0.05) + _circ(cx, 0, H, 0.18))


def _filtros():
    fs = [(0.0, 1.81, "Filtro 1 · arena 1.81 m"), (0.9, 1.81, "Filtro 2 · arena 1.81 m"),
          (1.8, 1.97, "Filtro 3 · carbón 1.97 m")]
    t = [_tr(_filtro(x, h)) for x, h, _ in fs]
    t += [_tr(_caja(x + 0.3, -0.1, 0.35, 0.08, 0.2, 0.25), PANEL, 3) for x, _, _ in fs]
    return t + [_txt(x, 0, h + 0.2, n) for x, h, n in fs]


def _torre():  # ILUSTRATIVA: medidas provisionales hasta medir la torre real
    ventilador = _circ(0.8, 0.6, 4.55, 0.4) + [((0.4, 0.6, 4.55), (1.2, 0.6, 4.55)), ((0.8, 0.2, 4.55), (0.8, 1.0, 4.55))]
    return [_tr(_caja(0, 0, 0, 1.6, 1.2, 1.3)), _tr(_caja(0.3, 0.2, 1.3, 1.0, 0.8, 3.0)),
            _tr(_caja(0.3, -0.02, 0.4, 1.0, 0.02, 0.5), PANEL, 3), _tr(_cilindro(0.8, 0.6, 4.3, 0.4, 0.25)),
            _tr(ventilador, PANEL, 3), _txt(0.8, 0.6, 5.0, "ILUSTRATIVO · medidas por confirmar")]


PLANOS = {"homogenizacion": _homogenizacion, "coagulacion": _coagulacion, "sedimentador": _sedimentador,
          "oxidacion": _oxidacion, "filtros": _filtros, "torre_enfriamiento": _torre}
LEYENDA = "Azul: estructura · Verde: nivel de agua · Naranja: paneles / agitador · Lila: tuberías perforadas. Arrastra para girar."


def plano_3d(clave, solido=False):
    f = go.Figure((SOLIDOS if solido else PLANOS)[clave]())
    ejes = dict(visible=False)
    f.update_layout(template="plotly_dark", paper_bgcolor="#0e1117", height=480, margin=dict(l=0, r=0, t=0, b=0),
                    scene=dict(aspectmode="data", bgcolor="#0e1117", xaxis=ejes, yaxis=ejes, zaxis=ejes,
                               camera=dict(eye=dict(x=1.6, y=-1.6, z=0.9))))
    return f


def mostrar_plano(clave):
    if clave in PLANOS:
        st.subheader("🧊 Plano 3D")
        vista = "Alambre"
        if clave in SOLIDOS:
            vistas = ["Alambre", "Sólido"] + (["Three.js (prueba)"] if clave == "sedimentador" else [])
            vista = st.radio("Vista", vistas, horizontal=True, key=f"vista_{clave}")
        if vista.startswith("Three"):
            from visor3d import visor_sedimentador
            visor_sedimentador()
        else:
            st.plotly_chart(plano_3d(clave, vista == "Sólido"), width="stretch")
            st.caption(LEYENDA)


# ---------------------------- vista sólida (prototipo: sedimentador) ----------------------------
AZUL, ACERO, GRIS = "#1f6feb", "#c9d1d9", "#6e7681"


def _mesh(X, Y, Z, I, J, K, color, op=1.0):
    return go.Mesh3d(x=X, y=Y, z=Z, i=I, j=J, k=K, color=color, opacity=op, flatshading=True,
                     lighting=dict(ambient=0.6, diffuse=0.8, specular=0.2), hoverinfo="skip")


def _mcaja(x0, y0, z0, L, B, H, color, op=1.0):
    X = [x0, x0 + L, x0 + L, x0, x0, x0 + L, x0 + L, x0]
    Y = [y0, y0, y0 + B, y0 + B, y0, y0, y0 + B, y0 + B]
    Z = [z0] * 4 + [z0 + H] * 4
    return _mesh(X, Y, Z, [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3], [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4],
                 [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7], color, op)


def _mtronco(xi, B, L, zb, sal, color, op=1.0):
    cx, cy, h = xi + L / 2, B / 2, sal / 2
    X = [xi, xi + L, xi + L, xi, cx - h, cx + h, cx + h, cx - h]
    Y = [0, 0, B, B, cy - h, cy - h, cy + h, cy + h]
    return _mesh(X, Y, [zb] * 4 + [0] * 4, [0, 0, 1, 1, 2, 2, 3, 3], [1, 5, 2, 6, 3, 7, 0, 4],
                 [5, 4, 6, 5, 7, 6, 4, 7], color, op)


def _mcil(cx, cy, cz, L, r, eje, color, n=16):
    X, Y, Z = [], [], []
    for s in (0, 1):
        for k in range(n):
            u, v = r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)
            if eje == "z":
                X.append(cx + u); Y.append(cy + v); Z.append(cz + s * L)
            else:
                X.append(cx + s * L); Y.append(cy + u); Z.append(cz + v)
    I, J, K = [], [], []
    for k in range(n):
        k2 = (k + 1) % n
        I += [k, k]; J += [k2, k2 + n]; K += [k2 + n, k + n]
    return _mesh(X, Y, Z, I, J, K, color)


def _hex_top(x0, y0, L, B, z, s=0.07):
    segs, dx, dy, i, cx = [], 1.5 * s, math.sqrt(3) * s, 0, x0 + s
    while cx <= x0 + L - s:
        cy = y0 + s + (dy / 2 if i % 2 else 0)
        while cy <= y0 + B - s:
            q = [(cx + s * math.cos(math.pi / 3 * k), cy + s * math.sin(math.pi / 3 * k), z) for k in range(6)]
            segs += [(q[k], q[(k + 1) % 6]) for k in range(6)]
            cy += dy
        cx += dx
        i += 1
    return segs


def _sedimentador_solido():
    B, x0, zt, zb = 1.5, 0.8, 2.95, 0.75
    t = [_mcaja(x0, 0, zb, 3.0, B, zt - zb, AZUL, 0.25), _mcaja(0, 0, zt - 1.7, 0.8, B, 1.7, AZUL, 0.3),
         _mtronco(0.8, B, 1.5, zb, 0.2, AZUL, 0.95), _mtronco(2.3, B, 1.5, zb, 0.2, AZUL, 0.95),
         _mcaja(x0, 0, 1.51, 3.0, B, 0.55, "#2f81f7", 0.95)]
    t += [_mcaja(x - 0.05, y - 0.05, 0, 0.1, 0.1, 0.8, GRIS) for x in (0.85, 3.7) for y in (0.05, B - 0.05)]
    t += [_mcil(x0, B / 2, 2.65, 3.0, 0.045, "x", ACERO), _mcil(x0, B / 2, 1.30, 3.0, 0.045, "x", ACERO),
          _mcil(-0.3, B / 2, 2.65, 0.3, 0.08, "x", GRIS),
          _mcil(1.55, 0.75, -0.1, 0.1, 0.045, "z", GRIS), _mcil(3.05, 0.75, -0.1, 0.1, 0.045, "z", GRIS)]
    borde = _caja(x0, 0, zb, 3.0, B, zt - zb) + _caja(0, 0, zt - 1.7, 0.8, B, 1.7) + _piramide(0.8, B, 1.5, zb) + _piramide(2.3, B, 1.5, zb)
    t += [_tr(borde, CIAN, 2), _tr(_hex_top(x0, 0, 3.0, B, 2.06), "#a5d6ff", 1), _tr(_rect(0, 0, 2.65, 3.8, B), NIVEL, 3)]
    return t


SOLIDOS = {"sedimentador": _sedimentador_solido}
