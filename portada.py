import base64
import io
import os
import time

import streamlit as st

LOGO_UNIVERSIDAD = "logo_universidad.png"  # subir este archivo a la raíz del repositorio
LOGO_KENZO = "logo.png"
DURACION_TRANSICION = 1.3  # segundos

CSS = """
.stApp { background: radial-gradient(circle at 20% 10%, #12304f 0%, #0e1117 55%), #0e1117; }
section[data-testid="stSidebar"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
.hero { display: flex !important; flex-direction: column; align-items: center; text-align: center; width: 100%;
  padding: 2.5rem 1rem 1rem; position: relative; z-index: 2; }
.logos { display: flex; align-items: center; justify-content: center; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.logo-card { background: #fff; border-radius: 16px; padding: 14px 26px; box-shadow: 0 8px 30px rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center; height: 120px; box-sizing: border-box; min-width: 220px; }
.logo-card img { height: 70px; width: auto; max-width: 300px; object-fit: contain; }
.logo-texto { color: #0e1117; font-weight: 700; font-size: 1.2rem; }
.x { color: #58a6ff; font-size: 2rem; }
.kicker { letter-spacing: .35em; color: #58a6ff; font-weight: 600; margin: .5rem 0 0; }
.hero h1 { font-size: clamp(2.2rem, 6vw, 3.8rem); margin: .2rem 0; color: #fafafa; text-align: center; }
.hero h2 { font-size: clamp(1.1rem, 2.6vw, 1.6rem); font-weight: 400; color: #c9d1d9; max-width: 820px; margin: 0 auto 1.2rem; text-align: center; }
.hero .msg { max-width: 760px !important; width: 100%; margin: 0 auto 1.5rem !important; text-align: center !important;
  color: #8b949e; font-size: 1.1rem; line-height: 1.6; }
.waves { position: fixed; left: 0; right: 0; bottom: 0; height: 120px; z-index: 0; pointer-events: none; overflow: hidden; opacity: .55; }
.waves svg { position: absolute; bottom: 0; width: 200%; height: 100%; animation: ola 14s linear infinite; }
.waves svg.b { animation-duration: 22s; animation-direction: reverse; opacity: .6; }
@keyframes ola { from { transform: translateX(0); } to { transform: translateX(-50%); } }
div.stButton, div[data-testid="stButton"] { display: flex !important; justify-content: center !important; width: 100% !important;
  position: relative; z-index: 2; }
div.stButton > button, div[data-testid="stButton"] > button { width: auto !important; min-width: 340px; font-size: 1.35rem; font-weight: 700;
  padding: .9rem 1.5rem; border-radius: 999px; border: 0; color: #fff; background: linear-gradient(90deg, #1f6feb, #00b4d8);
  box-shadow: 0 0 28px rgba(0,180,216,.45); transition: transform .15s, box-shadow .15s; }
div.stButton > button:hover, div[data-testid="stButton"] > button:hover { transform: scale(1.04); box-shadow: 0 0 40px rgba(0,180,216,.7); color: #fff; }
"""

# Transición al ingresar: el "agua" sube y cubre la pantalla
CSS_TRANSICION = """
.transicion { position: fixed; inset: 0; z-index: 9999; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(180deg, #00b4d8 0%, #1f6feb 55%, #0e2a4d 100%); transform: translateY(105%);
  animation: subir 1.1s cubic-bezier(.6,.05,.4,1) forwards; }
.transicion::before { content: ""; position: absolute; left: 0; right: 0; top: -58px; height: 60px;
  background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 60' preserveAspectRatio='none'><path fill='%2300b4d8' d='M0,30 C150,60 350,0 600,30 C850,60 1050,0 1200,30 L1200,60 L0,60 Z'/></svg>") repeat-x; background-size: 100% 100%; }
.transicion span { color: #fff; font-size: 1.8rem; font-weight: 700; letter-spacing: .05em; opacity: 0; animation: texto .6s .5s forwards; }
@keyframes subir { to { transform: translateY(0); } }
@keyframes texto { to { opacity: 1; } }
"""

CSS_APARECER = """
.block-container { animation: aparecer .8s ease; }
@keyframes aparecer { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
"""

OLA = ('<svg viewBox="0 0 2400 120" preserveAspectRatio="none"><path fill="%s" d="M0,60 C150,100 350,20 600,60 '
       'C850,100 1050,20 1200,60 C1350,100 1550,20 1800,60 C2050,100 2250,20 2400,60 L2400,120 L0,120 Z"/></svg>')


def _recortar(datos):
    """Quita los márgenes blancos o transparentes del logo para que no se vea pequeño dentro de su tarjeta."""
    try:
        from PIL import Image, ImageChops
        im = Image.open(io.BytesIO(datos)).convert("RGBA")
        sobre_blanco = Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im).convert("RGB")
        dif = ImageChops.difference(sobre_blanco, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda p: 255 if p > 12 else 0)
        caja = dif.getbbox()
        if caja:
            im = im.crop(caja)
        salida = io.BytesIO()
        im.save(salida, format="PNG")
        return salida.getvalue(), "image/png"
    except Exception:
        return datos, None


def _logo(path, alt):
    if os.path.exists(path):
        ext = path.rsplit(".", 1)[-1].lower()
        with open(path, "rb") as f:
            datos = f.read()
        mime = "image/svg+xml" if ext == "svg" else "image/" + ("jpeg" if ext in ("jpg", "jpeg") else ext)
        if ext != "svg":
            datos, mime_nuevo = _recortar(datos)
            mime = mime_nuevo or mime
        return f'<div class="logo-card"><img src="data:{mime};base64,{base64.b64encode(datos).decode()}" alt="{alt}"></div>'
    return f'<div class="logo-card logo-texto">{alt}</div>'


def portada_activa():
    """Muestra la portada y devuelve True mientras el estudiante no haya ingresado.
    Los enlaces de los QR (?equipo=...) y el modo ?admin=1 saltan la portada."""
    if st.session_state.get("entrado") or any(k in st.query_params for k in ("equipo", "admin")):
        if st.session_state.pop("recien_entrado", False):
            st.markdown(f"<style>{CSS_APARECER}</style>", unsafe_allow_html=True)
        return False
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    html = (
        '<div class="hero">'
        f'<div class="logos">{_logo(LOGO_UNIVERSIDAD, "Universidad Central")}<span class="x">×</span>{_logo(LOGO_KENZO, "Kenzo Jeans")}</div>'
        '<div class="kicker">BIENVENIDOS</div>'
        '<h1>Universidad Central</h1>'
        '<h2>al recorrido por la Planta de Tratamiento de Aguas Residuales de <b>Kenzo Jeans</b></h2>'
        '<div class="msg">Hoy conocerán cómo el agua de nuestra tintorería recibe tratamiento antes de su descarga. '
        'Presten atención, observen cada equipo y hagan todas las preguntas que necesiten: cada duda es parte del aprendizaje. '
        'Y no dejen de trabajar por el medio ambiente: el agua que cuidamos hoy es el futuro de todos.</div>'
        '</div>'
        f'<div class="waves">{OLA % "#1f6feb"}{OLA % "#00b4d8"}</div>'
    )
    html = html.replace('</svg><svg', '</svg><svg class="b"', 1)
    st.markdown(html, unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        if st.button("¡Click acá para ingresar! 💧"):
            st.markdown(f"<style>{CSS_TRANSICION}</style><div class='transicion'><span>💧 Ingresando al recorrido…</span></div>",
                        unsafe_allow_html=True)
            time.sleep(DURACION_TRANSICION)
            st.session_state["entrado"] = True
            st.session_state["recien_entrado"] = True
            st.rerun()
    return True
