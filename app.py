import io
import qrcode
import streamlit as st

st.set_page_config(
    page_title="Fichas técnicas PTAR", 
    page_icon="💧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (Diseño moderno, oscuro y vistoso)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* Tarjetas de contenido estilizadas nativas */
    div.element-container div.stMarkdown {
        color: #fafafa;
    }
    
    /* Métricas con diseño corporativo */
    div[data-testid="stMetric"] {
        background-color: #1f242d;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        border: 1px solid #30363d;
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# DATOS DE LA PLANTA Y EQUIPOS
# ---------------------------------------------------------------------------
EQUIPOS = {
    "homogenizacion": {
        "nombre": "Tanque de homogenización",
        "V": 40.0,
        "nota": "PROVISIONAL: 45 m³ totales con franco libre supuesto de 0.4 m. Verificar altura en sitio.",
        "industria": "Industrial / Textil y Tintorería",
        "uso_general": (
            "Almacena y mezcla el agua residual proveniente de los diferentes procesos productivos "
            "(lavado, teñido, rebosaderos) para estandarizar el caudal, la temperatura, el pH y la concentración "
            "de contaminantes antes de que ingresen al sistema fisicoquímico."
        ),
        "cuando_si": (
            "Siempre que existan descargas discontinuas o con alta variabilidad en color, temperatura "
            "y carga orgánica (típico en tintorerías por el cambio de baches o lotes de producción)."
        ),
        "cuando_no": (
            "Cuando el efluente tenga una concentración extrema de sólidos sedimentables pesados que deban "
            "retirarse previamente en un desarenador para evitar acumulación excesiva en el fondo."
        ),
        "dato_curioso": (
            "En la industria textil, los baños de tinte cambian drásticamente de pH (ácido a básico) "
            "en cuestión de minutos. Sin este tanque, los equipos de coagulación posteriores colapsarían "
            "por falta de estabilidad química."
        ),
    },
    "coagulacion": {
        "nombre": "Tanque de coagulación",
        "V": 2.89,
        "nota": "Volumen útil según tabla de diseño.",
        "industria": "Industrial / Tratamiento Fisicoquímico",
        "uso_general": (
            "Espacio donde se dosifican y mezclan rápidamente productos químicos (coagulantes como policloruro "
            "de aluminio o sales de fierro) para desestabilizar las cargas eléctricas de los coloides suspendidos "
            "y colorantes disueltos."
        ),
        "cuando_si": (
            "Para remover color verdadero, color aparente, turbiedad fina y materia orgánica coloidal "
            "que no se retiene por gravedad simple."
        ),
        "cuando_no": (
            "Cuando el agua contiene exclusivamente contaminantes disueltos biodegradables que se eliminan "
            "mejor mediante tratamientos biológicos directos sin consumo alto de químicos."
        ),
        "dato_curioso": (
            "La mezcla en este tanque debe ser ultra rápida y turbulenta (usualmente con tiempos de retención "
            "de segundos) porque si la agitación es lenta, el químico no se desparrama bien y se desaprovecha."
        ),
    },
    "sedimentador": {
        "nombre": "Sedimentador clarificador",
        "V": 9.11,
        "nota": "Volumen útil según tabla de diseño.",
        "industria": "Industrial y Municipal / Separación Sólido-Líquido",
        "uso_general": (
            "Separa por gravedad los flóculos formados en la etapa de coagulación-floculación, "
            "produciendo agua clarificada en la parte superior y lodo concentrado en las tolvas inferiores."
        ),
        "cuando_si": (
            "Cuando se obtienen flóculos densos y pesados, con un caudal de alimentación estable "
            "garantizado por el tanque de homogenización."
        ),
        "cuando_no": (
            "Cuando predominan partículas livianas o emulsiones de grasas/aceites que tienden a flotar "
            "en lugar de hundirse (para eso se requiere flotación por aire disuelto - DAF)."
        ),
        "dato_curioso": (
            "El principio físico detrás de los sedimentadores modernos se basa en la ley de Stokes "
            "y los criterios de Hazen desarrollados hace más de un siglo, los cuales siguen vigentes."
        ),
    },
    "oxidacion": {
        "nombre": "Tanque de oxidación",
        "V": 5.8,
        "nota": "Volumen útil según tabla de diseño.",
        "industria": "Industrial / Tratamiento Avanzado o Afinado",
        "uso_general": (
            "Permite llevar a cabo reacciones de oxidación química o biológica para reducir la Demanda "
            "Química de Oxígeno (DQO) remanente, destruir compuestos recalcitrantes o eliminar trazas de color "
            "que sobrevivieron al proceso fisicoquímico."
        ),
        "cuando_si": (
            "Cuando los límites de vertimiento exigidos por la autoridad ambiental son muy estrictos "
            "en cuanto a DQO residual y color."
        ),
        "cuando_no": (
            "Cuando la carga orgánica principal es fácilmente tratable solo con los procesos primarios y "
            "secundarios, o cuando el costo energético/químico de la oxidación avanzada no se justifica."
        ),
        "dato_curioso": (
            "En aguas textiles, este paso actúa como la 'barrera final' para asegurar que el agua cumpla "
            "con los parámetros estéticos y normativos antes de su descarga o reúso."
        ),
    },
}

CAUDAL_DEFECTO_LMIN = 100.0  
SED_L, SED_B = 3.8, 1.5  

# ---------------------------------------------------------------------------
# BARRA LATERAL: Logo grande y controles
# ---------------------------------------------------------------------------
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        st.info("💡 Coloca tu archivo 'logo.png' en la raíz del proyecto para visualizarlo aquí.")

    st.markdown("---")
    q_lmin = st.number_input("💧 Caudal de trabajo (L/min)", 1.0, 5000.0, CAUDAL_DEFECTO_LMIN, 5.0)
    st.caption("Caudal de referencia para simulaciones de escenarios.")

q_m3h = q_lmin * 60 / 1000
q_m3d = q_lmin * 1.44

paginas = ["inicio"] + list(EQUIPOS) + ["qr"]
etiquetas = {"inicio": "🏠 Inicio", "qr": "📱 Generar códigos QR", **{k: v["nombre"] for k, v in EQUIPOS.items()}}
inicial = st.query_params.get("equipo", "inicio")
if inicial not in paginas:
    inicial = "inicio"

with st.sidebar:
    st.markdown("### 🎛️ Navegación")
    pagina = st.selectbox("Seleccionar Equipo", paginas, index=paginas.index(inicial), format_func=etiquetas.get)

# ---------------------------------------------------------------------------
# PLANTILLA DE FICHA GENÉRICA (Corregida con Markdown nativo y vistoso)
# ---------------------------------------------------------------------------
def ficha_generica(clave):
    e = EQUIPOS[clave]
    st.header(e["nombre"])

    with st.container():
        st.markdown(f"### 🏭 1. Tipo de industria")
        st.info(e["industria"])

        st.markdown(f"### ⚙️ 2. Qué es y para qué sirve (Uso general)")
        st.write(e["uso_general"])

        st.markdown(f"### ⚖️ 3. Cuándo sí y cuándo no se usa")
        st.markdown(f"- **Cuándo sí:** {e['cuando_si']}")
        st.markdown(f"- **Cuándo no:** {e['cuando_no']}")

        format_curioso = f"💡 **Dato curioso:** {e['dato_curioso']}"
        st.success(format_curioso)

    st.markdown("---")
    st.subheader("📊 Parámetros de diseño y cálculo rápido")
    c1, c2 = st.columns(2)
    c1.metric("Volumen útil", f"{e['V']} m³")
    c2.metric("TRH (Caudal actual)", f"{e['V'] / q_m3h:.2f} h")
    st.caption(e["nota"])

# ---------------------------------------------------------------------------
# FICHA ESPECÍFICA: SEDIMENTADOR
# ---------------------------------------------------------------------------
def ficha_sedimentador():
    area = SED_L * SED_B
    v = EQUIPOS["sedimentador"]["V"]
    e = EQUIPOS["sedimentador"]
    
    st.header(e["nombre"])

    with st.container():
        st.markdown(f"### 🏭 1. Tipo de industria")
        st.info(e["industria"])

        st.markdown(f"### ⚙️ 2. Qué es y para qué sirve (Uso general)")
        st.write(e["uso_general"])
        st.write("**En nuestra planta:** El agua floculada entra por una tubería perforada ubicada bajo los paneles de sedimentación acelerada. Los flóculos caen hacia las dos bases piramidales y se purgan por dos válvulas de 3\" hacia las bandejas de deshidratación.")

        st.markdown(f"### ⚖️ 3. Cuándo sí y cuándo no se usa")
        st.markdown("- **Cuándo sí:** Flóculos densos, caudal estable y SST moderados.")
        st.markdown("- **Cuándo no:** Partículas livianas, grasas o picos de caudal fuertes.")

        st.success(f"💡 **Dato curioso:** {e['dato_curioso']}")

    st.markdown("---")
    st.subheader("📐 Dimensionamiento y Fórmulas")
    st.latex(r"A = L \times B \qquad CS = \frac{Q}{A} \qquad TRH = \frac{V}{Q}")
    st.caption("A: área superficial (m²) · CS: carga superficial (m³/m²·d) · Q: caudal · V: volumen útil")

    st.subheader("🧮 Calculadora de rendimiento")
    extra = st.number_input("Área efectiva adicional de paneles inclinados (m²)", 0.0, 200.0, 0.0, 0.5)
    c1, c2, c3 = st.columns(3)
    c1.metric("Área superficial", f"{area + extra:.2f} m²")
    c2.metric("TRH", f"{v / q_m3h:.2f} h")
    c3.metric("Carga superficial", f"{q_m3d / (area + extra):.1f} m³/m²·d")

    st.subheader("🎯 Pregunta pista")
    resp = st.number_input("¿Cuál es la carga superficial (m³/m²·d) con el caudal actual, sin paneles?", 0.0, 1000.0, 0.0, 0.1)
    if st.button("Verificar respuesta"):
        correcta = q_m3d / area
        if abs(resp - correcta) <= 0.03 * correcta:
            st.success("¡Correcto!")
        else:
            st.error("No coincide. Revisa las unidades de caudal y el área superficial.")

# ---------------------------------------------------------------------------
# GENERADOR DE QR
# ---------------------------------------------------------------------------
def pagina_qr():
    st.header("📱 Códigos QR por equipo")
    base = st.text_input("URL base de la app", "https://TU-APP.streamlit.app").rstrip("/")
    for clave, e in EQUIPOS.items():
        buf = io.BytesIO()
        qrcode.make(f"{base}/?equipo={clave}").save(buf, format="PNG")
        col1, col2 = st.columns([1, 2])
        col1.image(buf.getvalue(), width=150)
        col2.write(f"**{e['nombre']}**")
        col2.download_button("Descargar PNG", buf.getvalue(), f"qr_{clave}.png", "image/png", key=f"dl_{clave}")

# ---------------------------------------------------------------------------
# ENRUTADOR PRINCIPAL (Con sección de Kenzo Jeans y compromiso ambiental)
# ---------------------------------------------------------------------------
if pagina == "inicio":
    st.title("💧 Fichas técnicas de la PTAR - Kenzo Jeans")
    
    st.markdown("""
    ### 🌿 Compromiso Ambiental y Sostenibilidad
    En **Kenzo Jeans**, entendemos que la moda y la innovación industrial deben marchar de la mano con la protección de los recursos naturales. Nuestro compromiso con el medio ambiente se refleja en la gestión integral de nuestros procesos productivos, asegurando que cada gota de agua utilizada en las etapas de lavandería y tintorería reciba un tratamiento riguroso antes de su retorno al sistema.
    
    El sistema de tratamiento de aguas residuales (**PTAR**) representa el núcleo de nuestra política de producción limpia y economía circular, garantizando el cumplimiento estricto de las normativas ambientales vigentes y minimizando nuestra huella hídrica.
    """)

    st.markdown("---")
    st.info("👉 **Instrucciones:** Selecciona un equipo en el menú de la barra lateral para explorar sus especificaciones técnicas detalladas, o escanea los códigos QR ubicados en planta para acceder de forma rápida desde dispositivos móviles.")

elif pagina == "sedimentador":
    ficha_sedimentador()
elif pagina == "qr":
    pagina_qr()
else:
    ficha_generica(pagina)
