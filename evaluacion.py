import random

import requests
import streamlit as st

MOSTRAR_RESPUESTAS = False  # True para mostrar las respuestas correctas al terminar (cuando ya todos presentaron)

# La PRIMERA opción de cada pregunta es la correcta; el orden se baraja distinto para cada estudiante.
PREGUNTAS = [
    {"q": "¿Cuál es el orden correcto de las etapas del tren de tratamiento?",
     "op": ["Draga y rejillas → torre de enfriamiento → homogenización → coagulación → sedimentador → oxidación → filtración → MF/UF",
            "Draga y rejillas → homogenización → torre de enfriamiento → sedimentador → coagulación → filtración → oxidación",
            "Torre de enfriamiento → draga y rejillas → coagulación → homogenización → sedimentador → oxidación → filtración",
            "Homogenización → draga y rejillas → coagulación → torre de enfriamiento → oxidación → sedimentador → filtración"],
     "exp": "Primero se retiran los sólidos gruesos, se enfría el agua, se homogeniza, se trata fisicoquímicamente (coagulación y sedimentación) y al final se pule (oxidación, filtros y membranas)."},
    {"q": "¿Por qué se enfría el agua en la torre antes del tratamiento fisicoquímico?",
     "op": ["Porque el agua de tintorería sale caliente y la temperatura afecta las reacciones posteriores y a equipos sensibles como las membranas",
            "Para concentrar los contaminantes por evaporación",
            "Para aumentar la cantidad de lodo producido",
            "Para retirar el color del agua con el aire"],
     "exp": "El agua baja por debajo de 30 °C para que la coagulación, la sedimentación y los módulos de filtración trabajen en mejores condiciones."},
    {"q": "¿Qué se hace en el tanque de homogenización y neutralización?",
     "op": ["Se amortiguan las variaciones de caudal, pH y carga, y se ajusta el pH aplicando cal hidratada de forma manual",
            "Se separan los flóculos por gravedad",
            "Se oxida el color remanente con peróxido de hidrógeno",
            "Se dosifica automáticamente el floculante con una bomba de diafragma"],
     "exp": "El tanque entrega un agua más estable al tratamiento; el pH se corrige con cal aplicada a mano, sin sistema automático."},
    {"q": "¿Por qué se usa PAC (policloruro de aluminio) y no alumbre (sulfato de aluminio)?",
     "op": ["Porque está prehidrolizado: funciona en un rango de pH más amplio, consume menos alcalinidad y suele requerir menor dosis y generar menos lodo",
            "Porque es un polímero orgánico que reemplaza al floculante",
            "Porque no necesita ensayo de jarras para definir la dosis",
            "Porque elimina el color por oxidación"],
     "exp": "El alumbre consume alcalinidad, baja el pH y tiene un rango de trabajo más estrecho; el PAC es más tolerante y eficiente."},
    {"q": "¿Qué floculante se usa en la planta y cómo actúa?",
     "op": ["Poliacrilamida aniónica de alto peso molecular: forma puentes entre los microflóculos y los une en flóculos más grandes y pesados",
            "Un polímero catiónico de bajo peso molecular que neutraliza la carga de los coloides",
            "Cloruro férrico, que precipita metales disueltos",
            "Cal hidratada, que forma lodo de hidróxido"],
     "exp": "El floculante no desestabiliza coloides (eso lo hace el coagulante); engrosa los flóculos para que sedimenten."},
    {"q": "¿Qué proceso ocurre en el tanque de oxidación con peróxido de hidrógeno?",
     "op": ["Se reduce la materia orgánica (DQO) y el color que persisten tras el tratamiento fisicoquímico",
            "Se coagulan los sólidos gruesos",
            "Se desinfecta el agua con cloro residual libre",
            "Se retienen los sólidos finos por tamaño de poro"],
     "exp": "El peróxido oxida compuestos orgánicos y color remanentes; la bomba B1 recircula el agua para mezclarlo."},
    {"q": "¿Qué función cumple el filtro de carbón activado?",
     "op": ["Adsorber color remanente, tensoactivos y olor",
            "Retener los flóculos que escaparon del sedimentador",
            "Retener partículas por tamaño de poro, como una membrana",
            "Oxidar la materia orgánica con peróxido"],
     "exp": "Los filtros de arena retienen sólidos; el de carbón actúa por adsorción sobre color, tensoactivos y olor."},
]


def _enviar(url, payload):
    if not url:
        return True, "sin webhook configurado"
    try:
        r = requests.post(url, json=payload, timeout=8)
        return (r.status_code == 200), f"código {r.status_code}"
    except Exception as err:
        return False, str(err)


def _resultado():
    r = st.session_state["eval_resultado"]
    st.success(f"Gracias, **{r['nombre']}**. Tu evaluación fue enviada." if r["ok"] else
               "Tu evaluación se calificó, pero no se pudo registrar en la hoja.")
    st.metric("Calificación", f"{r['puntaje']} / {len(PREGUNTAS)} aciertos")
    if not r["ok"]:
        st.warning(f"Problema de conexión ({r['msg']}). No cierres esta página.")
        if st.button("🔁 Reintentar envío"):
            r["ok"], r["msg"] = _enviar(r["url"], r["payload"])
            st.rerun()
    if r["puntaje"] >= 6:
        st.info("🌟 ¡Excelente dominio de los procesos de la PTAR!")
    elif r["puntaje"] >= 4:
        st.info("👍 Buen desempeño. Repasa algunos detalles del tren en las fichas técnicas.")
    else:
        st.warning("💡 Te sugerimos revisar de nuevo las fichas técnicas del menú lateral.")
    if MOSTRAR_RESPUESTAS:
        with st.expander("Respuestas correctas"):
            for i, p in enumerate(PREGUNTAS, 1):
                st.markdown(f"**{i}. {p['q']}**  \n✅ {p['op'][0]}  \n{p['exp']}")


def pagina_evaluacion(webhook_url=""):
    st.header("🎓 Evaluación de conocimiento - Recorrido PTAR Kenzo Jeans")
    if st.session_state.get("eval_resultado"):
        _resultado()
        return
    st.markdown("**Universidad Central — Sistemas de Tratamiento Avanzado**  \n"
                f"Completa tus datos y responde las {len(PREGUNTAS)} preguntas basadas en el recorrido por la planta.")
    if "eval_orden" not in st.session_state:
        st.session_state["eval_orden"] = [random.sample(p["op"], len(p["op"])) for p in PREGUNTAS]

    with st.form("form_evaluacion"):
        st.subheader("👤 Datos del estudiante")
        c1, c2, c3 = st.columns(3)
        nombre = c1.text_input("Nombre completo")
        cedula = c2.text_input("Cédula / Documento")
        correo = c3.text_input("Correo institucional")
        st.subheader("📝 Cuestionario")
        resp = [st.radio(f"**{i + 1}. {p['q']}**", st.session_state["eval_orden"][i], index=None, key=f"eval_q{i}")
                for i, p in enumerate(PREGUNTAS)]
        acepto = st.checkbox("Autorizo el tratamiento de mis datos (nombre, documento y correo) únicamente para registrar "
                             "esta evaluación académica.")
        enviar = st.form_submit_button("📤 Enviar evaluación")

    if enviar:
        if not (nombre.strip() and cedula.strip() and correo.strip()):
            st.error("⚠️ Completa nombre, documento y correo.")
        elif any(r is None for r in resp):
            faltan = [str(i + 1) for i, r in enumerate(resp) if r is None]
            st.error(f"⚠️ Te faltan por responder las preguntas: {', '.join(faltan)}.")
        elif not acepto:
            st.error("⚠️ Debes autorizar el tratamiento de tus datos para enviar.")
        else:
            puntaje = sum(r == p["op"][0] for r, p in zip(resp, PREGUNTAS))
            payload = {"nombre": nombre, "cedula": cedula, "correo": correo, "puntaje": f"{puntaje}/{len(PREGUNTAS)}",
                       **{f"p{i + 1}": r for i, r in enumerate(resp)}}
            ok, msg = _enviar(webhook_url, payload)
            st.session_state["eval_resultado"] = {"nombre": nombre, "puntaje": puntaje, "ok": ok, "msg": msg,
                                                  "url": webhook_url, "payload": payload}
            st.rerun()
