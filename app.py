import io
import math
import requests
from evaluacion import pagina_evaluacion# <- Librería para enviar los datos al Webhook

import qrcode
import streamlit as st

from planos3d import mostrar_plano

APP_URL = "https://evaluacion-universidad-central-k7pajrjvmfi3wcverutpfp.streamlit.app/"  # <- poner la URL real de la app
WEBHOOK_SHEET_URL = "https://script.google.com/macros/s/AKfycbxI8178gRI44TBgtZfS4leESFAxgoa4vrVYSC1wy8h4FkdujtewyHrcoq69GaWvJaOnkA/exec"  # <- Poner tu URL de Apps Script
st.set_page_config(page_title="Planta de Tratamiento de Agua Residual - Kenzo Jeans", page_icon="💧", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    div[data-testid="stMetric"] { background-color: #1f242d; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 1px solid #30363d; }
    div[data-testid="stMetric"] label { color: #8b949e !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #58a6ff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

from portada import portada_activa
if portada_activa():
    st.stop()

# ---------------------------------------------------------------------------
# DATOS (medidas en m, volúmenes en m³). Editar aquí al verificar datos.
# ---------------------------------------------------------------------------
EQUIPOS = {
    "draga_rejillas": {
        "nombre": "Draga y rejillas", "tipo": "preliminar",
        "industria": "Textil / Marítima / Tratamiento de agua / Construcción / Minera",
        "uso_general": "Primera fase: retira los sólidos gruesos del agua de tintorería con una draga y cuatro rejillas "
                       "en paralelo de diferentes diámetros que retienen sólidos cada vez menores.",
        "cuando_si": "Siempre en la cabecera de la planta, para proteger bombas y equipos posteriores de obstrucciones.",
        "cuando_no": "Cuando el agua ya llega libre de sólidos gruesos (poco común en tintorería). Sin limpieza periódica "
                     "pierde su función y puede desbordarse.",
        "dato_curioso": "Las rejillas de distinto diámetro actúan como un filtro progresivo: cada una retiene un tamaño de sólido diferente.",
        "specs": ["**Componentes:** draga y 4 rejillas en paralelo.", "**Función:** retención de sólidos gruesos y menores.",
                  "**Mantenimiento:** retiro periódico de los residuos retenidos.",
                  "**Palas:** separadas unos 60 cm; elevan los sólidos por una rampa hasta una tolva de lodos.",
                  "**Dimensiones (estimadas):** canal de unos 4 m de largo y 2 m de profundidad."],
    },
    "torre_enfriamiento": {
        "nombre": "Torre de enfriamiento", "tipo": "preliminar",
        "industria": "Industrial / Acondicionamiento térmico",
        "uso_general": "Una motobomba activada por flotador sube el agua a la parte alta; al caer, un ventilador superior "
                       "genera un flujo de aire ascendente que baja la temperatura del vertimiento por debajo de 30 °C.",
        "cuando_si": "Cuando el agua de tintorería llega caliente: la coagulación y los módulos de filtración posteriores "
                     "funcionan mejor (y están más protegidos) con el agua fría.",
        "cuando_no": "Cuando el efluente ya llega a temperatura ambiente y no requiere disipar calor.",
        "dato_curioso": "Sus 12 paneles de polipropileno de alta densidad no solo mejoran el contacto aire-agua: también "
                        "retiran sólidos que pasaron la draga.",
        "specs": ["**Rendimiento:** vertimiento por debajo de 30 °C.", "**Relleno:** 12 paneles de polipropileno de alta densidad.",
                  "**Aire:** ventilador en la parte superior, que jala el aire hacia arriba (tiro inducido).",
                  "**Bombeo:** motobomba con accionamiento por flotador.",
                  "**Dimensiones (estimadas):** unos 6 m de alto y 1.3 × 1.3 m en planta."],
    },
    "homogenizacion": {
        "nombre": "Tanque de homogenización y neutralización", "tipo": "diseno", "V": 40.0, "V_total": 45.0,
        "nota": "45 m³ totales; útil estimado con 0.4 m de volumen libre. Tanque enterrado: la boca queda al nivel del piso.",
        "industria": "Industrial / Tratamiento de agua",
        "uso_general": "Recibe el agua de la torre y amortigua las variaciones de caudal, pH y carga de los procesos de Tintorería. "
                       "Aquí se ajusta el pH aplicando cal hidratada de forma manual (no hay un sistema de dosificación ni de respaldo automático).",
        "cuando_si": "Cuando hay picos de carga hidráulica o química que desestabilizarían el tratamiento fisicoquímico posterior.",
        "cuando_no": "Cuando el caudal y la calidad del agua ya son constantes, o el tanque está en limpieza por sedimentos acumulados.",
        "dato_curioso": "La bomba de 3 HP tiene una línea de recirculación al mismo tanque: sirve para regular el caudal "
                        "enviado a coagulación y para mezclar la cal.",
    },
    "coagulacion": {
        "nombre": "Tanque de coagulación", "tipo": "diseno", "V": 2.89, "V_total": 3.74,
        "nota": "Cilíndrico con base cónica: Ø 1.5 m, altura recta 1.5 m, cono 0.5 m, altura total 3.0 m con patas (plano). "
                "El volumen total incluye franco libre.",
        "industria": "Industrial / Tratamiento fisicoquímico",
        "uso_general": "Un agitador de 0.5 HP mezcla el coagulante (PAC) con el agua para desestabilizar los coloides. "
                       "La floculación ocurre después, en la tubería en U y en el primer compartimiento del sedimentador.",
        "cuando_si": "Para remover color y sólidos coloidales que no sedimentan solos.",
        "cuando_no": "Cuando el pH está fuera del rango en que el coagulante actúa bien, o no hay coloides que desestabilizar.",
        "dato_curioso": "La dosis óptima no se calcula: se determina con ensayo de jarras (100 rpm por 30 s, 33 rpm por 15 min, "
                        "15 min de sedimentación).",
    },
    "sedimentador": {
        "nombre": "Sedimentador clarificador", "tipo": "diseno", "V": 9.11, "V_total": 10.8,
        "nota": "Largo total 3.8 m = 0.8 m de entrada + 3.0 m de zona de sedimentación; ancho 1.5 m; pared recta 2.2 m y "
                "2 pirámides de 0.75 m.",
        "industria": "Industrial y municipal / Separación sólido-líquido",
        "uso_general": "Separa por gravedad los flóculos: agua clarificada arriba y lodo concentrado en las dos bases piramidales.",
        "cuando_si": "Con flóculos densos, caudal estable y sólidos suspendidos moderados.",
        "cuando_no": "Con partículas livianas o grasas que flotan, o picos de caudal que generan turbulencia.",
        "dato_curioso": "El principio de Hazen dice que una partícula se retiene si su velocidad de sedimentación es mayor o igual "
                        "a la carga superficial: por eso los paneles inclinados, que aumentan el área efectiva, mejoran la separación.",
    },
    "oxidacion": {
        "nombre": "Tanque de oxidación", "tipo": "diseno", "V": 5.8, "V_total": 6.1,
        "nota": "Cilindro de Ø 1.8 m y 2.4 m de altura recta, en PRFV.",
        "industria": "Industrial / Tratamiento avanzado",
        "uso_general": "Oxidación química con peróxido de hidrógeno, dosificado con bomba de diafragma en la línea de "
                       "recirculación (bomba B1, que también mezcla el peróxido), para reducir DQO y color remanentes.",
        "cuando_si": "Cuando después del tratamiento fisicoquímico quedan color y materia orgánica oxidable que superan los límites.",
        "cuando_no": "Cuando la carga orgánica y el color ya cumplen la norma tras sedimentar.",
        "dato_curioso": "No es la última barrera: después vienen los filtros de arena, el de carbón y la salida. "
                        "Pregunta para pensar: ¿qué pasa con el peróxido residual cuando llega al carbón activado?",
    },
    "filtros": {
        "nombre": "Filtración (arena y carbón activado)", "tipo": "filtros",
        "nota": "3 filtros a presión de Ø 0.6 m y 1.5 m de altura recta: 2 de arena/grava (1.81 m totales) y 1 de carbón "
                "activado (1.97 m totales). Alimentados por las bombas B2 y B3 (1.5 HP), que alternan.",
        "industria": "Industrial y municipal / Mejora del efluente",
        "uso_general": "Los filtros de arena retienen los flóculos que escapan del sedimentador; el de carbón activado "
                       "adsorbe color, tensoactivos y olor. Se limpian con retrolavado.",
        "cuando_si": "Para 'pulir' el agua clarificada antes de la descarga, cuando aún arrastra sólidos finos o color.",
        "cuando_no": "Cuando el agua llega con muchos sólidos (se colmata rápido): deben retirarse antes, en el sedimentador.",
        "dato_curioso": "Durante la filtración las válvulas de ½\" de la parte superior deben estar cerradas, y la válvula de alivio "
                        "limita la presión interna a 60 psi.",
    },
}

EQUIPOS["mf_uf"] = {
    "nombre": "Microfiltración y ultrafiltración", "tipo": "membranas",
    "nota": "Datos de la planta pendientes: tipo de membrana, área y flujo de diseño. Plano pendiente.",
    "industria": "Industrial y municipal / Química",
    "uso_general": "Membranas que retienen por tamaño las partículas finas y coloides que pasaron los filtros. "
                   "La microfiltración trabaja con poros de ~0.1-10 µm y la ultrafiltración de ~0.01-0.1 µm. "
                   "Después de ellas el agua se almacena en el tanque de agua tratada.",
    "cuando_si": "Cuando se necesita un efluente muy clarificado, con pocos sólidos finos y coloides.",
    "cuando_no": "Cuando el agua llega con muchos sólidos o con oxidantes o temperaturas que la membrana no tolera: "
                 "se ensucia rápido o se daña.",
    "dato_curioso": "Su gran enemigo es el ensuciamiento (fouling): por eso se limpia con retrolavados y por eso todo el tren "
                    "anterior existe, para entregarle un agua lo más limpia posible.",
}

SED_L, SED_B = 3.0, 1.5  # zona de sedimentación (m), según plano
FILTRO_AREA = math.pi * 0.3 ** 2  # Ø 0.6 m

# ---------------------------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------------------------
with st.sidebar:
    try:
        st.image("logo.png", width="stretch")
    except Exception:
        st.info("💡 Coloca 'logo.png' en la raíz del proyecto para verlo aquí.")
    st.markdown("---")
    q_lmin = st.number_input("💧 Caudal de trabajo (L/min)", 1.0, 5000.0, 100.0, 5.0)
    st.warning("Caudal de referencia pendiente de verificar. Cámbialo para explorar escenarios.")

q_m3h = q_lmin * 60 / 1000
q_m3d = q_lmin * 1.44

admin = st.query_params.get("admin") == "1"
paginas = ["inicio"] + list(EQUIPOS) + ["evaluacion"] + (["qr"] if admin else [])
etiquetas = {
    "inicio": "🏠 Inicio", 
    "evaluacion": "🎓 Evaluación Recorrido PTAR", 
    "qr": "📱 Generar códigos QR", 
    **{k: v["nombre"] for k, v in EQUIPOS.items()}
}
inicial = st.query_params.get("equipo", "inicio")
if inicial not in paginas:
    inicial = "inicio"
with st.sidebar:
    st.markdown("### 🎛️ Navegación del tren")
    pagina = st.selectbox("Seleccionar etapa / equipo", paginas, index=paginas.index(inicial), format_func=etiquetas.get)


# ---------------------------------------------------------------------------
# CALCULADORAS
# ---------------------------------------------------------------------------
def calc_homogenizacion():
    st.subheader("🧮 Dosis de cal hidratada")
    kg = st.number_input("Cal aplicada en seco (kg)", 0.0, 20.0, 4.0, 0.5)
    st.metric("Dosis con el tanque lleno", f"{kg * 1000 / EQUIPOS['homogenizacion']['V']:.0f} g/m³")
    st.caption("Se aplica manualmente, de 3 a 5 kg según el pH, hasta llegar a pH 9. A esta dosis se disuelve en el volumen "
               "del tanque, pero necesita mezcla (recirculación). Manipular con EPP: el polvo es irritante y alcalino.")


def calc_coagulacion():
    st.subheader("🧮 Dosificación de PAC:  Q2 = Q1 · C1 / C2")
    dosis = st.number_input("Dosis requerida C1 (mg/L)", 1.0, 1000.0, 100.0, 5.0)
    pct = st.number_input("Concentración de la solución de PAC (%)", 1.0, 15.0, 10.0, 1.0)
    q2 = q_lmin * 60 * dosis / (pct * 10000)
    st.metric("Caudal de la bomba dosificadora", f"{q2:.1f} L/h")
    if q2 > 10:
        st.warning("Supera los 10 L/h de la bomba dosificadora: usa una solución más concentrada.")
    st.caption("1 % de solución equivale a 10 000 mg/L. C1 y C2 deben ir en las mismas unidades.")


def calc_sedimentador():
    area = SED_L * SED_B
    v = EQUIPOS["sedimentador"]["V"]
    st.subheader("📐 Dimensionamiento")
    st.latex(r"A = L \times B \qquad CS = \frac{Q}{A} \qquad TRH = \frac{V}{Q}")
    st.caption("A: área superficial (m²) · CS: carga superficial (m³/m²·d) · Q: caudal · V: volumen útil. "
               "Referencia orientativa para sedimentadores convencionales: ~20-40 m³/m²·d (verificar en Metcalf & Eddy o RAS).")
    st.subheader("🧮 Calculadora")
    extra = st.number_input("Área efectiva adicional de los paneles inclinados (m²)", 0.0, 200.0, 0.0, 0.5)
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
            st.error("No coincide. Revisa las unidades del caudal y el área de la zona de sedimentación.")


def calc_filtros():
    st.subheader("🧮 Tasa de filtración y contacto en el carbón")
    n = st.radio("Filtros de arena trabajando en paralelo", [1, 2], index=1, horizontal=True)
    st.metric("Tasa de filtración por filtro", f"{q_m3h / (n * FILTRO_AREA):.1f} m/h")
    st.caption("Referencia típica de filtros rápidos: ~5-15 m/h (verificar).")
    lecho = st.number_input("Altura del lecho de carbón (m) — valor de ejemplo, pendiente de medir", 0.1, 1.5, 0.8, 0.1)
    st.metric("Tiempo de contacto en lecho vacío (EBCT)", f"{FILTRO_AREA * lecho / q_m3h * 60:.1f} min")
    st.caption("EBCT = volumen del lecho / caudal. Referencia típica para carbón: ~5-30 min (verificar).")


def calc_mf():
    st.subheader("🧮 Flujo por membrana:  J = Q / A")
    area = st.number_input("Área de membrana (m²) — valor de ejemplo, pendiente de medir", 0.5, 500.0, 10.0, 0.5)
    st.metric("Flujo (J)", f"{q_lmin * 60 / area:.1f} L/m²·h")
    st.caption("Si el flujo es mayor al de diseño del fabricante, la membrana se ensucia más rápido.")


CALCULOS = {"mf_uf": calc_mf, "homogenizacion": calc_homogenizacion, "coagulacion": calc_coagulacion,
            "sedimentador": calc_sedimentador, "filtros": calc_filtros}


# ---------------------------------------------------------------------------
# FICHA
# ---------------------------------------------------------------------------
def ficha(clave):
    e = EQUIPOS[clave]
    st.header(e["nombre"])
    st.markdown("### 🏭 Tipo de industria")
    st.info(e["industria"])
    st.markdown("### ⚙️ Qué es y para qué sirve")
    st.write(e["uso_general"])
    st.markdown("### ⚖️ Cuándo sí y cuándo no se usa")
    st.markdown(f"- **Cuándo sí:** {e['cuando_si']}")
    st.markdown(f"- **Cuándo no:** {e['cuando_no']}")
    if e.get("specs"):
        st.markdown("### 🔧 Especificaciones")
        for s in e["specs"]:
            st.markdown(f"- {s}")
    st.success(f"💡 **Dato curioso:** {e['dato_curioso']}")

    mostrar_plano(clave)

    if e["tipo"] == "diseno":
        st.markdown("---")
        st.subheader("📊 Parámetros de diseño")
        c1, c2 = st.columns(2)
        c1.metric("Volumen útil", f"{e['V']} m³")
        c2.metric("TRH con el caudal actual", f"{e['V'] / q_m3h:.2f} h")
    if e.get("nota"):
        st.caption(e["nota"])
    if clave in CALCULOS:
        st.markdown("---")
        CALCULOS[clave]()


def pagina_evaluacion():
    st.header("🎓 Evaluación de Conocimiento - Recorrido PTAR Kenzo Jeans")
    st.markdown(
        """
        **Universidad Central — Sistemas de Tratamiento Avanzado**  
        Por favor ingresa tus datos personales y responde las 7 preguntas basadas en el recorrido por la planta. 
        Al finalizar, haz clic en el botón para enviar, guardar en registro y conocer tu calificación.
        """
    )
    st.markdown("---")

    with st.form("form_evaluacion"):
        st.subheader("👤 Datos del Estudiante")
        col_d1, col_d2, col_d3 = st.columns(3)
        nombre = col_d1.text_input("Nombre completo")
        cedula = col_d2.text_input("Cédula / Documento")
        correo = col_d3.text_input("Correo institucional")

        st.markdown("---")
        st.subheader("📝 Cuestionario de la PTAR")

        # Pregunta 1
        st.markdown("**1. ¿Cuál es la función principal de la torre de enfriamiento en la cabecera del tren de tratamiento textil?**")
        p1 = st.radio("Opciones_p1", [
            "A) Retirar los sólidos suspendidos de gran tamaño mediante rejillas.",
            "B) Disipar calor y bajar la temperatura del efluente de tintorería por debajo de 30 °C.",
            "C) Elevar el pH del agua inyectando cal viva."
        ], index=0, label_visibility="collapsed")

        # Pregunta 2
        st.markdown("**2. ¿Qué producto químico se utiliza habitualmente en el tanque de coagulación para desestabilizar los coloides?**")
        p2 = st.radio("Opciones_p2", [
            "A) Peróxido de hidrógeno ($H_2O_2$)",
            "B) Policloruro de aluminio (PAC)",
            "C) Hipoclorito de sodio"
        ], index=0, label_visibility="collapsed")

        # Pregunta 3
        st.markdown("**3. En el tanque de homogenización y neutralización, ¿cómo se realiza normalmente el ajuste de pH en esta planta?**")
        p3 = st.radio("Opciones_p3", [
            "A) Dosificación automática computarizada con válvulas PID.",
            "B) Aplicación manual de cal hidratada según el valor medido.",
            "C) Adición continua de ácido sulfúrico."
        ], index=0, label_visibility="collapsed")

        # Pregunta 4
        st.markdown("**4. ¿Cuál es el objetivo físico principal de la zona de sedimentación con sus paneles inclinados?**")
        p4 = st.radio("Opciones_p4", [
            "A) Retener y separar por gravedad los flóculos formados, aumentando el área superficial efectiva.",
            "B) Oxigenar el agua para eliminar completamente la DQO.",
            "C) Filtrar bacterias patógenas mediante membranas porosas."
        ], index=0, label_visibility="collapsed")

        # Pregunta 5
        st.markdown("**5. ¿Qué función cumple específicamente el filtro de carbón activado en las etapas finales del tren?**")
        p5 = st.radio("Opciones_p5", [
            "A) Retener únicamente arena gruesa del río.",
            "B) Adsorber color remanente, tensoactivos y olores del efluente.",
            "C) Aumentar la temperatura del agua antes del vertimiento."
        ], index=0, label_visibility="collapsed")

        # Pregunta 6
        st.markdown("**6. ¿Qué proceso químico se lleva a cabo en el tanque de oxidación empleando peróxido de hidrógeno?**")
        p6 = st.radio("Opciones_p6", [
            "A) Reducción de la carga orgánica disuelta (DQO) y color que persiste tras el fisicoquímico.",
            "B) Coagulación primaria de sólidos gruesos.",
            "C) Desinfección microbiológica con cloro residual libre."
        ], index=0, label_visibility="collapsed")

        # Pregunta 7
        st.markdown("**7. ¿Cuál es el principal factor o problema operativo que amenaza la vida útil de las membranas de micro/ultrafiltración (fouling)?**")
        p7 = st.radio("Opciones_p7", [
            "A) El exceso de colorantes azulados en el agua.",
            "B) El ensuciamiento por sólidos finos, coloides o agentes incompatibles que no fueron removidos antes.",
            "C) El exceso de presión por debajo de 10 psi."
        ], index=0, label_visibility="collapsed")

        st.markdown("---")
        enviar_quiz = st.form_submit_button("📤 Enviar y Guardar Evaluación")

        if enviar_quiz:
            if not nombre.strip() or not cedula.strip() or not correo.strip():
                st.error("⚠️ Por favor completa tus datos personales (Nombre, Cédula y Correo) antes de enviar.")
            else:
                # Calificación automática
                puntaje = 0
                if p1.startswith("B)"): puntaje += 1
                if p2.startswith("B)"): puntaje += 1
                if p3.startswith("B)"): puntaje += 1
                if p4.startswith("A)"): puntaje += 1
                if p5.startswith("B)"): puntaje += 1
                if p6.startswith("A)"): puntaje += 1
                if p7.startswith("B)"): puntaje += 1

                # Preparar JSON para Google Sheets
                payload = {
                    "nombre": nombre,
                    "cedula": cedula,
                    "correo": correo,
                    "puntaje": f"{puntaje}/7",
                    "p1": p1,
                    "p2": p2,
                    "p3": p3,
                    "p4": p4,
                    "p5": p5,
                    "p6": p6,
                    "p7": p7
                }

                # Enviar al Webhook de Google Apps Script
                try:
                    res = requests.post(WEBHOOK_SHEET_URL, json=payload, timeout=8)
                    if res.status_code == 200:
                        st.success(f"🎉 ¡Evaluación registrada exitosamente en Google Sheets, **{nombre}**!")
                    else:
                        st.warning(f"⚠️ Evaluación completada, pero hubo un contratiempo al conectar con Sheets (Código {res.status_code}).")
                except Exception as err:
                    st.warning(f"⚠️ Evaluación completada, pero no se logró conectar con Google Sheets: {err}")

                st.metric("Calificación Obtenida", f"{puntaje} / 7 aciertos")
                
                if puntaje >= 6:
                    st.info("🌟 ¡Excelente dominio de los procesos de tratamiento de la PTAR!")
                elif puntaje >= 4:
                    st.info("👍 Buen desempeño, repasa algunos detalles del tren fisicoquímico y de filtración.")
                else:
                    st.warning("💡 Te sugerimos revisar nuevamente las fichas técnicas de los equipos en el menú lateral.")


def pagina_qr():
    st.header("📱 Códigos QR")
    base = st.text_input("URL base de la app", APP_URL).rstrip("/")
    st.subheader("🚪 QR de ingreso (lleva a la portada)")
    buf = io.BytesIO()
    qrcode.make(base).save(buf, format="PNG")
    c1, c2 = st.columns([1, 2])
    c1.image(buf.getvalue(), width=150)
    c2.write("**Ingreso al recorrido**: para proyectar o imprimir en la entrada de la planta.")
    c2.download_button("Descargar PNG", buf.getvalue(), "qr_ingreso.png", "image/png", key="dl_ingreso")
    st.subheader("📍 QR por equipo (van directo a la ficha)")
    for clave, e in EQUIPOS.items():
        buf = io.BytesIO()
        qrcode.make(f"{base}/?equipo={clave}").save(buf, format="PNG")
        c1, c2 = st.columns([1, 2])
        c1.image(buf.getvalue(), width=150)
        c2.write(f"**{e['nombre']}**")
        c2.download_button("Descargar PNG", buf.getvalue(), f"qr_{clave}.png", "image/png", key=f"dl_{clave}")


# ---------------------------------------------------------------------------
# ENRUTADOR
# ---------------------------------------------------------------------------
if pagina == "inicio":
    st.title("💧 Planta de Tratamiento de Agua Residual - Kenzo Jeans")
    st.markdown(
        """
        ### 🌿 Compromiso ambiental
        En **Kenzo Jeans** buscamos que la producción de moda vaya de la mano con el cuidado de los recursos naturales.
        El agua de nuestros procesos de tintorería recibe un tratamiento fisicoquímico y de pulimento antes de su descarga,
        con el objetivo de cumplir la normativa ambiental vigente y reducir nuestro impacto sobre el recurso hídrico.
        """
    )
    st.markdown("---")
    st.info("👉 **Instrucciones:** elige un equipo en el menú lateral para explorar sus fichas técnicas, planos 3D y calculadoras, "
            "o dirígete a la sección de evaluación académica si realizaste el recorrido.")
elif pagina == "evaluacion":
    pagina_evaluacion(https://script.google.com/macros/s/AKfycbxI8178gRI44TBgtZfS4leESFAxgoa4vrVYSC1wy8h4FkdujtewyHrcoq69GaWvJaOnkA/exec)
elif pagina == "qr":
    pagina_qr()
else:
    ficha(pagina)
