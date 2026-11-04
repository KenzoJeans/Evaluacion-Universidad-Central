import base64
import os

import streamlit as st

LOGO_UNIVERSIDAD = "logo_universidad.png"  # subir este archivo a la raíz del repositorio
LOGO_KENZO = "logonegro.png"

CSS = """
.stApp { background: radial-gradient(circle at 20% 10%, #12304f 0%, #0e1117 55%), #0e1117; }
section[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none; }
.hero { text-align: center; padding: 2.5rem 1rem 1rem; position: relative; z-index: 2; }
.logos { display: flex; align-items: center; justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.logo-card { background: #fff; border-radius: 16px; padding: 14px 22px; box-shadow: 0 8px 30px rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; min-width: 180px; min-height: 90px; }
.logo-card img { max-height: 90px; max-width: 260px; }
.logo-texto { color: #0e1117; font-weight: 700; font-size: 1.2rem; }
.x { color: #58a6ff; font-size: 2rem; }
.kicker { letter-spacing: .35em; color: #58a6ff; font-weight: 600; margin: .5rem 0 0; }
.hero h1 { font-size: clamp(2.2rem, 6vw, 3.8rem); margin: .2rem 0; color: #fafafa; }
.hero h2 { font-size: clamp(1.1rem, 2.6vw, 1.6rem); font-weight: 400; color: #c9d1d9; max-width: 820px; margin: 0 auto 1.2rem; }
.msg { max-width: 760px; margin: 0 auto 1.5rem; color: #8b949e; font-size: 1.1rem; line-height: 1.6; }
.waves { position: fixed; left: 0; right: 0; bottom: 0; height: 120px; z-index: 0; pointer-events: none; overflow: hidden; opacity: .55; }
.waves svg { position: absolute; bottom: 0; width: 200%; height: 100%; animation: ola 14s linear infinite; }
.waves svg.b { animation-duration: 22s; animation-direction: reverse; opacity: .6; }
@keyframes ola { from { transform: translateX(0); } to { transform: translateX(-50%); } }
div.stButton { width: 100%; position: relative; z-index: 2; }
div.stButton > button { width: 100%; font-size: 1.35rem; font-weight: 700; padding: .9rem 1.5rem; border-radius: 999px; border: 0;
  color: #fff; background: linear-gradient(90deg, #1f6feb, #00b4d8); box-shadow: 0 0 28px rgba(0,180,216,.45);
  transition: transform .15s, box-shadow .15s; }
div.stButton > button:hover { transform: scale(1.04); box-shadow: 0 0 40px rgba(0,180,216,.7); color: #fff; }
"""

OLA = ('<svg viewBox="0 0 2400 120" preserveAspectRatio="none"><path fill="%s" d="M0,60 C150,100 350,20 600,60 '
       'C850,100 1050,20 1200,60 C1350,100 1550,20 1800,60 C2050,100 2250,20 2400,60 L2400,120 L0,120 Z"/></svg>')


def _logo(path, alt):
    if os.path.exists(path):
        ext = path.rsplit(".", 1)[-1].lower()
        mime = "image/svg+xml" if ext == "svg" else "image/" + ("jpeg" if ext in ("jpg", "jpeg") else ext)
        with open(path, "rb") as f:
            datos = base64.b64encode(f.read()).decode()
        return f'<div class="logo-card"><img src="data:{mime};base64,{datos}" alt="{alt}"></div>'
    return f'<div class="logo-card logo-texto">{alt}</div>'


def portada_activa():
    """Muestra la portada y devuelve True mientras el estudiante no haya ingresado.
    Los enlaces de los QR (?equipo=...) y el modo ?admin=1 saltan la portada."""
    if st.session_state.get("entrado") or any(k in st.query_params for k in ("equipo", "admin")):
        return False
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    html = (
        '<div class="hero">'
        f'<div class="logos">{_logo(LOGO_UNIVERSIDAD, "Universidad Central")}<span class="x">×</span>{_logo(LOGO_KENZO, "Kenzo Jeans")}</div>'
        '<p class="kicker">BIENVENIDOS</p>'
        '<h1>Universidad Central</h1>'
        '<h2>al recorrido por la Planta de Tratamiento de Aguas Residuales de <b>Kenzo Jeans</b></h2>'
        '<p class="msg">Hoy conocerán cómo el agua de nuestra tintorería recibe tratamiento antes de su descarga. '
        'Presten atención, observen cada equipo y hagan todas las preguntas que necesiten: cada duda es parte del aprendizaje. '
        'Y no dejen de trabajar por el medio ambiente: el agua que cuidamos hoy es el futuro de todos.</p>'
        '</div>'
        f'<div class="waves">{OLA % "#1f6feb"}{OLA % "#00b4d8"}</div>'
    )
    html = html.replace('</svg><svg', '</svg><svg class="b"', 1)
    st.markdown(html, unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        if st.button("¡Click acá para ingresar! 💧"):
            st.session_state["entrado"] = True
            st.rerun()
    return True
