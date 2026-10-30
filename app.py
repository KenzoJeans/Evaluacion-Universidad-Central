import io

import qrcode
import streamlit as st

st.set_page_config(page_title="Fichas técnicas PTAR", page_icon="💧", layout="centered")

# ---------------------------------------------------------------------------
# DATOS DE LA PLANTA (editar aquí cuando se verifiquen las medidas)
# V = volumen útil en m³
# ---------------------------------------------------------------------------
EQUIPOS = {
    "homogenizacion": {
        "nombre": "Tanque de homogenización",
        "V": 40.0,
        "nota": "PROVISIONAL: 45 m³ totales con franco libre supuesto de 0.4 m. Verificar altura en sitio.",
    },
    "coagulacion": {"nombre": "Tanque de coagulación", "V": 2.89, "nota": "Volumen útil según tabla de diseño."},
    "sedimentador": {"nombre": "Sedimentador clarificador", "V": 9.11, "nota": "Volumen útil según tabla de diseño."},
    "oxidacion": {"nombre": "Tanque de oxidación", "V": 5.8, "nota": "Volumen útil según tabla de diseño."},
}
CAUDAL_DEFECTO_LMIN = 100.0  # PENDIENTE DE VERIFICAR
SED_L, SED_B = 3.8, 1.5  # largo y ancho del sedimentador (m)

# ---------------------------------------------------------------------------
# BARRA LATERAL: caudal editable y navegación
# ---------------------------------------------------------------------------
st.sidebar.title("💧 PTAR Tintorería")
q_lmin = st.sidebar.number_input("Caudal de trabajo (L/min)", 1.0, 5000.0, CAUDAL_DEFECTO_LMIN, 5.0)
st.sidebar.warning("Caudal de referencia pendiente de verificar. Cámbialo para explorar escenarios.")
q_m3h = q_lmin * 60 / 1000
q_m3d = q_lmin * 1.44

paginas = ["inicio"] + list(EQUIPOS) + ["qr"]
etiquetas = {"inicio": "Inicio", "qr": "Generar códigos QR", **{k: v["nombre"] for k, v in EQUIPOS.items()}}
inicial = st.query_params.get("equipo", "inicio")
if inicial not in paginas:
    inicial = "inicio"
pagina = st.sidebar.selectbox("Equipo", paginas, index=paginas.index(inicial), format_func=etiquetas.get)


# ---------------------------------------------------------------------------
# FICHAS
# ---------------------------------------------------------------------------
def ficha_sedimentador():
    area = SED_L * SED_B
    v = EQUIPOS["sedimentador"]["V"]
    st.header("Sedimentador clarificador")

    st.subheader("1. Qué es y para qué sirve")
    st.write(
        "Separa por gravedad los flóculos formados en la coagulación-floculación, "
        "produciendo agua clarificada arriba y lodo concentrado abajo."
    )

    st.subheader("2. Cómo funciona (en nuestra planta)")
    st.write(
        "El agua floculada entra por una tubería perforada ubicada bajo los paneles de sedimentación acelerada. "
        "Los flóculos caen hacia las dos bases piramidales y se purgan por dos válvulas de 3\" hacia las bandejas "
        "de deshidratación. El clarificado sale por dos tubos perforados de 3\" unidos con una TEE hacia el tanque de oxidación."
    )

    st.subheader("3. Cuándo sí y cuándo no")
    st.markdown(
        "- **Sí:** flóculos densos, caudal estable (por eso se homogeniza antes), SST moderados.\n"
        "- **No (o con apoyo):** partículas livianas o flotantes como grasas, flóculos frágiles, "
        "picos de caudal que arrastran el lodo.\n"
        "- **Alternativa:** flotación por aire disuelto (DAF) cuando el sólido flota en vez de sedimentar."
    )

    st.subheader("4. Dimensionamiento")
    st.latex(r"A = L \times B \qquad CS = \frac{Q}{A} \qquad TRH = \frac{V}{Q}")
    st.caption(
        "A: área superficial (m²) · CS: carga superficial (m³/m²·d) · Q: caudal · V: volumen útil · "
        "Una partícula se retiene si su velocidad de sedimentación es mayor o igual a CS (principio de Hazen)."
    )
    st.info("Rango típico de CS para sedimentadores convencionales: ~20-40 m³/m²·d (verificar en Metcalf & Eddy o RAS antes de usar como criterio de nota). Con paneles inclinados el área efectiva aumenta.")

    st.subheader("5. Calculadora")
    extra = st.number_input("Área efectiva adicional de los paneles inclinados (m²)", 0.0, 200.0, 0.0, 0.5,
                            help="Proyección horizontal de los paneles. Dato pendiente de medir.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Área superficial", f"{area + extra:.2f} m²")
    c2.metric("TRH", f"{v / q_m3h:.2f} h")
    c3.metric("Carga superficial", f"{q_m3d / (area + extra):.1f} m³/m²·d")

    st.subheader("6. En nuestra planta")
    st.write(f"Dimensiones: {SED_L} × {SED_B} m, 2 bases piramidales de 0.75 m de alto, volumen útil {v} m³.")

    st.subheader("7. Pregunta pista")
    resp = st.number_input("¿Cuál es la carga superficial (m³/m²·d) con el caudal actual, sin paneles?", 0.0, 1000.0, 0.0, 0.1)
    if st.button("Verificar respuesta"):
        correcta = q_m3d / area
        if abs(resp - correcta) <= 0.03 * correcta:
            st.success("¡Correcto!")
        else:
            st.error("No coincide. Revisa las unidades de caudal y el área superficial.")


def ficha_generica(clave):
    e = EQUIPOS[clave]
    st.header(e["nombre"])
    st.info("Ficha en construcción.")
    c1, c2 = st.columns(2)
    c1.metric("Volumen útil", f"{e['V']} m³")
    c2.metric("TRH con el caudal actual", f"{e['V'] / q_m3h:.2f} h")
    st.caption(e["nota"])


def pagina_qr():
    st.header("Códigos QR por equipo")
    base = st.text_input("URL base de la app", "https://TU-APP.streamlit.app").rstrip("/")
    for clave, e in EQUIPOS.items():
        buf = io.BytesIO()
        qrcode.make(f"{base}/?equipo={clave}").save(buf, format="PNG")
        col1, col2 = st.columns([1, 2])
        col1.image(buf.getvalue(), width=150)
        col2.write(f"**{e['nombre']}**")
        col2.download_button("Descargar PNG", buf.getvalue(), f"qr_{clave}.png", "image/png", key=f"dl_{clave}")


# ---------------------------------------------------------------------------
# ENRUTADOR
# ---------------------------------------------------------------------------
if pagina == "inicio":
    st.title("Fichas técnicas de la PTAR")
    st.write("Escanea el QR de cada equipo o elige uno en el menú lateral. El caudal de la barra lateral se puede modificar para explorar escenarios.")
elif pagina == "sedimentador":
    ficha_sedimentador()
elif pagina == "qr":
    pagina_qr()
else:
    ficha_generica(pagina)
