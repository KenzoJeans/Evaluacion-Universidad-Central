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
def _homogenizacion():
    L, B, H = 5.1, 2.4, HOMO_H
    return [_tr(_caja(0, 0, 0, L, B, H)), _tr(_rect(0, 0, H - HOMO_FRANCO, L, B), NIVEL, 3),
            _txt(L / 2, -0.4, 0, f"{L} m"), _txt(L + 0.3, B / 2, 0, f"{B} m"), _txt(-0.4, 0, H / 2, f"{H:.2f} m (prov.)")]


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


PLANOS = {"homogenizacion": _homogenizacion, "coagulacion": _coagulacion,
          "sedimentador": _sedimentador, "oxidacion": _oxidacion}
LEYENDA = "Azul: estructura · Verde: nivel de agua · Naranja: paneles / agitador · Lila: tuberías perforadas. Arrastra para girar."


def plano_3d(clave):
    f = go.Figure(PLANOS[clave]())
    ejes = dict(visible=False)
    f.update_layout(template="plotly_dark", paper_bgcolor="#0e1117", height=480, margin=dict(l=0, r=0, t=0, b=0),
                    scene=dict(aspectmode="data", bgcolor="#0e1117", xaxis=ejes, yaxis=ejes, zaxis=ejes,
                               camera=dict(eye=dict(x=1.6, y=-1.6, z=0.9))))
    return f


def mostrar_plano(clave):
    if clave in PLANOS:
        st.subheader("🧊 Plano 3D")
        st.plotly_chart(plano_3d(clave), use_container_width=True)
        st.caption(LEYENDA)
