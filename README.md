# Visita Técnica a la PTAR – Recorrido y Evaluación (Universidad Central)

Aplicación educativa para acompañar el recorrido de los estudiantes de la Universidad Central por la Planta de Tratamiento de Agua Residual (PTAR) de la tintorería de Kenzo Jeans. Reúne la ficha técnica de cada equipo del tren de tratamiento, planos 3D, calculadoras de diseño y una evaluación al final de la visita.

## Propósito

- Que cada estudiante pueda escanear un código QR en un equipo y ver su ficha: qué es, para qué sirve, cuándo se usa y cuándo no.
- Mostrar cómo se dimensionan y operan las unidades, con calculadoras que se pueden manipular.
- Evaluar lo aprendido durante el recorrido y guardar los resultados en una hoja de cálculo.

## Tren de tratamiento que cubre

Las fichas siguen el orden del proceso:

| # | Etapa | Tipo en la aplicación |
|---|---|---|
| 1 | Draga y rejillas | Preliminar |
| 2 | Torre de enfriamiento | Preliminar |
| 3 | Tanque de homogenización y neutralización | Con parámetros de diseño y calculadora (cal hidratada) |
| 4 | Tanque de coagulación | Con parámetros de diseño y calculadora (dosificación de PAC) |
| 5 | Sedimentador clarificador | Con parámetros de diseño y calculadora (carga superficial, TRH) |
| 6 | Tanque de oxidación | Con parámetros de diseño |
| 7 | Filtración (arena y carbón activado) | Calculadora (tasa de filtración, tiempo de contacto) |
| 8 | Microfiltración y ultrafiltración | Calculadora (flujo por membrana) |

## Qué contiene cada ficha

Tipo de industria, qué es y para qué sirve, cuándo sí y cuándo no se usa, especificaciones, un dato curioso, el plano 3D del equipo y, según la etapa, parámetros de diseño y una calculadora interactiva. Algunas incluyen una pregunta para pensar o una "pregunta pista" con verificación de la respuesta.

## Navegación y códigos QR

- **Menú lateral:** selector de etapa o equipo, con la evaluación al final.
- **Enlace directo a una ficha:** `URL_de_la_app/?equipo=<clave>`. Las claves son `draga_rejillas`, `torre_enfriamiento`, `homogenizacion`, `coagulacion`, `sedimentador`, `oxidacion`, `filtros` y `mf_uf`.
- **Generador de códigos QR:** se abre agregando `?admin=1` a la URL de la aplicación. Produce un QR de ingreso (lleva a la portada) y un QR por equipo (lleva a su ficha), descargables en PNG para imprimir y pegar en la planta. Este parámetro solo muestra el generador; no es un control de seguridad.
- La URL base de la aplicación se define en la constante `APP_URL` del código; hay que actualizarla si la aplicación cambia de dirección.

## Calculadoras

Todas usan el **caudal de referencia** definido en cada ficha (por defecto 100 L/min), que el usuario puede cambiar para explorar escenarios.

| Calculadora | Qué calcula |
|---|---|
| Homogenización | Dosis de cal hidratada (g/m³) según los kg aplicados y el volumen útil del tanque |
| Coagulación | Caudal de la bomba dosificadora de PAC (L/h) con Q₂ = Q₁·C₁/C₂; avisa si supera 10 L/h |
| Sedimentador | Área superficial, tiempo de retención hidráulica (TRH) y carga superficial; permite sumar el área de paneles inclinados |
| Filtros | Tasa de filtración (m/h) con 1 o 2 filtros de arena y tiempo de contacto en lecho vacío (EBCT) del carbón |
| Microfiltración y ultrafiltración | Flujo por membrana J = Q/A (L/m²·h) |

## Datos pendientes de verificar

Los datos de los equipos están en el diccionario `EQUIPOS` del código (medidas en metros y volúmenes en m³). El propio código indica que deben editarse allí al verificarlos. Hoy hay datos estimados o pendientes:

- **Caudal de referencia (100 L/min):** valor de ejemplo, no el caudal real de la planta.
- **Dimensiones de la draga y de la torre de enfriamiento:** estimadas.
- **Microfiltración y ultrafiltración:** tipo de membrana, área y flujo de diseño pendientes; el área (10 m²) es un valor de ejemplo. Plano pendiente.
- **Altura del lecho de carbón activado (0,8 m):** valor de ejemplo, pendiente de medir.
- **Rangos de referencia** de carga superficial, tasa de filtración y tiempo de contacto: marcados en el código como "verificar" (por ejemplo, contra Metcalf & Eddy o el RAS).

Mientras estos datos no se confirmen, las calculadoras son ilustrativas y no representan la operación real de la planta.

## Evaluación

La página de evaluación se carga desde el módulo `evaluacion.py` y envía los resultados a una hoja de cálculo mediante un **webhook (Google Apps Script)**, cuya dirección está en la constante `WEBHOOK_SHEET_URL`.

> Completar: cómo se califica, qué datos se guardan de cada estudiante, en qué hoja de cálculo y cuenta de Google quedan los resultados, y dónde está el código del Apps Script.

## Estructura del proyecto

| Archivo | Función |
|---|---|
| Archivo principal | Navegación, datos de los equipos, fichas, calculadoras y generador de QR |
| `portada.py` | Portada de ingreso (`portada_activa`) |
| `planos3d.py` | Plano 3D de cada equipo (`mostrar_plano`) |
| `evaluacion.py` | Página de evaluación (`pagina_evaluacion`) |
| `logo.png` | Logo que se muestra en la barra lateral (opcional) |

> Completar: describir los tres módulos con más detalle (de dónde salen los modelos 3D, cómo se construyen las preguntas).

## Tecnologías y dependencias

Python con Streamlit y `qrcode` (con Pillow) para los códigos QR, más las librerías que usen los módulos `portada.py`, `planos3d.py` y `evaluacion.py`.

> Completar: confirmar que `requirements.txt` incluya todas las dependencias.

## Ejecución y despliegue

> Completar:

- **Archivo principal:** `[nombre del archivo, p. ej. app.py]`
- **Instalar dependencias:** `pip install -r requirements.txt`
- **Ejecutar en local:** `streamlit run [archivo].py`
- **Despliegue:** Streamlit Cloud, cuenta `[completar]`, URL `[completar]`
- **Hoja de cálculo de resultados y Apps Script:** `[completar]`

## Responsables

- **Dueño del proceso (gestión ambiental / PTAR):** `[área / cargo]`
- **Contacto en la Universidad Central:** `[completar]`
- **Mantenimiento técnico de la aplicación:** `[nombre / cargo]`
- **Cuentas (GitHub, Streamlit, Google):** `[a nombre de quién]`
