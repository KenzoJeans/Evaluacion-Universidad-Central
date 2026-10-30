import io
import qrcode
import streamlit as st
from planos3d import mostrar_plano

st.set_page_config(
    page_title="Fichas técnicas PTAR - Kenzo Jeans", 
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
# DATOS TÉCNICOS DEL TREN DE TRATAMIENTO (Llaves corregidas y unificadas)
# ---------------------------------------------------------------------------
EQUIPOS = {
    "draga_rejillas": {
        "nombre": "Draga y Rejillas de Desbaste",
        "tipo": "preliminar",
        "V": 0.0,
        "nota": "Sistema preliminar de retención de sólidos gruesos en serie paralela.",
        "industria": "Industrial / Tratamiento Preliminar Textil",
        "uso_general": (
            "Primera fase del sistema encargada de la remoción de sólidos de gran tamaño provenientes "
            "del área de tintorería, constituida por una draga y una serie en paralelo de cuatro rejillas "
            "con diferentes diámetros para la retención de sólidos menores."
        ),
        "cuando_si": (
            "De forma permanente durante la recepción de las aguas residuales crudas (ARND) para evitar "
            "obstrucciones y daños mecánicos en las motobombas y equipos posteriores."
        ),
        "cuando_no": (
            "No se debe operar sin la revisión periódica de acumulación de sólidos, ya que un bloqueo total "
            "provocaría desbordamientos en la cabecera de la planta."
        ),
        "dato_curioso": (
            "Las rejillas de diferentes diámetros actúan como un filtro progresivo para proteger los impulsores "
            "de las bombas de transferencia frente a hilos y retazos textiles."
        ),
        "specs_mecanicas": [
            "**Componentes:** Draga de limpieza y 4 rejillas en paralelo.",
            "**Función:** Retención de sólidos gruesos y menores.",
            "**Mantenimiento:** Retiro periódico de residuos retenidos."
        ]
    },
    "torre_enfriamiento": {
        "nombre": "Torre de Enfriamiento",
        "tipo": "preliminar",
        "V": 0.0,
        "nota": "Incluye 12 paneles de polipropileno de alta densidad y ventilador superior.",
        "industria": "Industrial / Acondicionamiento Térmico",
        "uso_general": (
            "Recibe el agua succionada por motobomba accionada por flotador para disminuir la temperatura "
            "del vertimiento por debajo de los 30 °C mediante caída y flujo de aire ascendente generado por un ventilador en la parte más alta."
        ),
        "cuando_si": (
            "Siempre que el agua de tintorería ingrese a altas temperaturas, asegurando que los procesos "
            "biológicos y químicos posteriores no sufran choques térmicos."
        ),
        "cuando_no": (
            "Cuando el efluente ya se encuentre a temperatura ambiente y no requiera disipación térmica."
        ),
        "dato_curioso": (
            "Los 12 paneles de polipropileno de alta densidad ubicados en su interior no solo optimizan el intercambio "
            "térmico, sino que actúan como trampa final para retirar sólidos flotantes que pasaron la draga."
        ),
        "specs_mecanicas": [
            "**Rendimiento térmico:** Disminución del vertimiento por debajo de 30 °C.",
            "**Medio de contacto:** 12 paneles de polipropileno de alta densidad.",
            "**Sistema de aire:** Ventilador superior de tiro forzado."
        ]
    },
    "homogenizacion": {
        "nombre": "Tanque de Homogenización",
        "tipo": "diseno",
        "V": 12.0,  # Volumen útil m³ según Tabla 1[cite: 7]
        "V_total": 14.0,
        "nota": "Dimensiones: 5.1 m largo × 2.4 m ancho × 1.2 m altura total (1.0 m útil)[cite: 7].",
        "industria": "Industrial / Ecualización de Carga",
        "uso_general": (
            "Almacena y mezcla el efluente proveniente de la torre de enfriamiento para estandarizar el caudal, "
            "la temperatura y amortiguar las fluctuaciones drásticas del pH características de los baños de tinte."
        ),
        "cuando_si": (
            "Para evitar picos de carga hidráulica y química que desestabilicen el tratamiento fisicoquímico posterior."
        ),
        "cuando_no": (
            "Cuando el tanque requiera mantenimiento correctivo o vaciado total por acumulación de sedimentos pesados."
        ),
        "dato_curioso": (
            "La bomba sumergible de 3 HP cuenta con una tubería de recirculación que permite regular con precisión "
            "el caudal exacto que se envía hacia el tanque de coagulación."
        ),
    },
    "coagulacion": {
        "nombre": "Tanque de Coagulación-Floculación",
        "tipo": "diseno",
        "V": 2.89,  # Volumen útil m³ según Tabla 1[cite: 8]
        "V_total": 3.74,
        "nota": "Cilíndrico con base cónica. Diámetro: 1.5 m, Altura recta: 1.5 m, Altura cono: 0.5 m, Altura total con patas: 3.2 m[cite: 8].",
        "industria": "Industrial / Tratamiento Fisicoquímico",
        "uso_general": (
            "Tanque cilíndrico con base cónica y un agitador interno accionado por un motor de 0.5 HP a velocidad constante. "
            "Realiza la mezcla rápida del producto coagulante y solución alcalina para la regulación del pH y desestabilización de coloides."
        ),
        "cuando_si": (
            "Para la remoción eficaz de color verdadero, color aparente y sólidos coloidales suspendidos en el agua textil."
        ),
        "cuando_no": (
            "Cuando el tren opere sin flujo de agua o sin dosificación de químicos, para evitar daños en el eje del agitador."
        ),
        "dato_curioso": (
            "El agitador de 0.5 HP permanece encendido a velocidad constante mientras ingresa el agua, garantizando "
            "una mezcla química homogénea antes del paso al sedimentador."
        ),
    },
    "sedimentador": {
        "nombre": "Sedimentador Clarificador",
        "tipo": "diseno",
        "V": 9.11,  # Volumen útil m³ según Tabla 3[cite: 9]
        "V_total": 10.8,
        "nota": "Dimensiones: 3.8 m largo × 1.5 m ancho × 1.7 m alto. 2 bases piramidales de 0.75 m de alto.",
        "industria": "Industrial y Municipal / Separación Sólido-Líquido",
        "uso_general": (
            "Separa por gravedad los flóculos formados en la coagulación, obteniendo agua clarificada en la parte superior "
            "y lodos concentrados en sus bases piramidales."
        ),
        "cuando_si": (
            "Cuando se obtienen flóculos densos gracias a una correcta dosificación en el tanque de coagulación."
        ),
        "cuando_no": (
            "Cuando se presentan picos de caudal extremo que generen turbulencia e impidan la decantación de los lodos."
        ),
        "dato_curioso": (
            "Emplea el principio de Hazen y velocidad de sedimentación para garantizar que el agua clarificada cumpla "
            "con los estándares estéticos antes de pasar a la oxidación."
        ),
    },
    "oxidacion": {
        "nombre": "Tanque de Oxidación",
        "tipo": "diseno",
        "V": 5.8,   # Volumen útil m³ según Tabla 3[cite: 10]
        "V_total": 6.1,
        "nota": "Dimensiones: Diámetro 1.8 m, Altura recta 2.4 m[cite: 10].",
        "industria": "Industrial / Tratamiento Avanzado o Afinado",
        "uso_general": (
            "Permite llevar a cabo reacciones de oxidación química o biológica para reducir la Demanda "
            "Química de Oxígeno (DQO) remanente y eliminar trazas finales de color."
        ),
        "cuando_si": (
            "Cuando los límites de vertimiento exigidos por la autoridad ambiental son estrictos en DQO y color residual."
        ),
        "cuando_no": (
            "Cuando la carga orgánica ya cumple con los parámetros normativos tras la etapa fisicoquímica."
        ),
        "dato_curioso": (
            "Actúa como la barrera final de seguridad dentro del tren de tratamiento de la PTAR antes de la disposición final."
        ),
    },
}

CAUDAL_DEFECTO_LMIN = 100.0  
SED_L, SED_B = 3.0, 1.5  

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
    st.markdown("### 🎛️ Navegación del Tren")
    pagina = st.selectbox("Seleccionar Etapa / Equipo", paginas, index=paginas.index(inicial), format_func=etiquetas.get)

# ---------------------------------------------------------------------------
# PLANTILLA DE FICHA GENÉRICA
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

        if e.get("tipo") == "preliminar":
            st.markdown(f"### 🔧 4. Especificaciones Operativas")
            for spec in e.get("specs_mecanicas", []):
                st.markdown(f"- {spec}")

        st.success(f"💡 **Dato curioso:** {e['dato_curioso']}")

    mostrar_plano(clave)
    if e.get("tipo") == "diseno":
        st.markdown("---")
        st.subheader("📊 Parámetros de diseño y cálculo rápido")
        c1, c2 = st.columns(2)
        c1.metric("Volumen Útil", f"{e['V']} m³")
        c2.metric("TRH (Caudal actual)", f"{e['V'] / q_m3h:.2f} h" if q_m3h > 0 else "N/A")
        if "V_total" in e:
            st.caption(f"Volumen total: {e['V_total']} m³ | {e['nota']}")
        else:
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

    mostrar_plano("sedimentador")
    st.markdown("---")
    st.subheader("📊 Parámetros de diseño y cálculo rápido")
    c1, c2 = st.columns(2)
    c1.metric("Volumen Útil", f"{v} m³")
    c2.metric("TRH (Caudal actual)", f"{v / q_m3h:.2f} h" if q_m3h > 0 else "N/A")
    st.caption(e["nota"])

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
    st.header("📱 Códigos QR por etapa y equipo")
    base = st.text_input("URL base de la app", "https://TU-APP.streamlit.app").rstrip("/")
    for clave, e in EQUIPOS.items():
        buf = io.BytesIO()
        qrcode.make(f"{base}/?equipo={clave}").save(buf, format="PNG")
        col1, col2 = st.columns([1, 2])
        col1.image(buf.getvalue(), width=150)
        col2.write(f"**{e['nombre']}**")
        col2.download_button("Descargar PNG", buf.getvalue(), f"qr_{clave}.png", "image/png", key=f"dl_{clave}")

# ---------------------------------------------------------------------------
# ENRUTADOR PRINCIPAL
# ---------------------------------------------------------------------------
if pagina == "inicio":
    st.title("💧 Fichas técnicas de la PTAR - Kenzo Jeans")
    
    st.markdown("""
    ### 🌿 Compromiso Ambiental y Sostenibilidad
    En **Kenzo Jeans**, entendemos que la moda y la innovación industrial deben marchar de la mano con la protección de los recursos naturales. Nuestro compromiso con el medio ambiente se refleja en la gestión integral de nuestros procesos productivos, asegurando que cada gota de agua utilizada en las etapas de lavandería y tintorería reciba un tratamiento riguroso antes de su retorno al sistema.
    
    El tren de tratamiento de aguas residuales (**PTAR**) representa el núcleo de nuestra política de producción limpia y economía circular, garantizando el cumplimiento estricto de las normativas ambientales vigentes y minimizando nuestra huella hídrica.
    """)

    st.markdown("---")
    st.info("👉 **Instrucciones:** Selecciona un equipo o etapa en el menú de la barra lateral para explorar sus especificaciones técnicas detalladas, o escanea los códigos QR ubicados en planta para acceder de forma rápida desde dispositivos móviles.")

elif pagina == "sedimentador":
    ficha_sedimentador()
elif pagina == "qr":
    pagina_qr()
else:
    ficha_generica(pagina)
